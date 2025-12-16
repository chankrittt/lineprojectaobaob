from celery import Task
from typing import Dict, Optional
import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.database import File as FileModel
from app.services.ai_service import ai_service
from app.services.storage_service import storage_service
from app.services.vector_service import vector_service
from app.utils.text_extractor import TextExtractor
from app.utils.metadata_extractor import metadata_extractor

logger = logging.getLogger(__name__)


class FileProcessingTask(Task):
    """Base task with database session management"""

    def __call__(self, *args, **kwargs):
        """Execute task with database session"""
        return super().__call__(*args, **kwargs)


@celery_app.task(
    bind=True,
    base=FileProcessingTask,
    name="app.workers.tasks.file_processing.process_uploaded_file",
    max_retries=3,
    default_retry_delay=60
)
def process_uploaded_file(self, file_id: str, user_id: str) -> Dict:
    """
    Background task to process uploaded file with AI

    Args:
        file_id: UUID of the file record
        user_id: UUID of the user who uploaded the file

    Returns:
        Dict with processing results
    """
    db = SessionLocal()

    try:
        logger.info(f"Starting background processing for file_id={file_id}, user_id={user_id}")

        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Starting file processing', 'progress': 10}
        )

        # Get file record from database
        result = db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == user_id
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            logger.error(f"File not found: {file_id}")
            raise ValueError(f"File not found: {file_id}")

        # Update status to processing
        file_record.processing_status = 'processing'
        db.commit()

        # Download file from MinIO
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Downloading file from storage', 'progress': 20}
        )

        file_data = storage_service.download_file_sync(file_record.file_path)

        if not file_data:
            raise ValueError("Failed to download file from storage")

        # Extract text content
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Extracting text content', 'progress': 30}
        )

        text_content = TextExtractor.extract_text(
            file_data,
            file_record.mime_type,
            file_record.original_filename
        )

        # Extract file metadata (EXIF, PDF info, etc.)
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Extracting file metadata', 'progress': 35}
        )

        try:
            file_metadata = metadata_extractor.extract_metadata_from_mime_type(
                file_data,
                file_record.mime_type or ''
            )
            if file_metadata and 'error' not in file_metadata:
                file_record.file_metadata = file_metadata
                logger.info(f"Extracted metadata for {file_id}: {list(file_metadata.keys())}")
        except Exception as e:
            logger.warning(f"Failed to extract metadata for {file_id}: {e}")
            # Don't fail the entire processing if metadata extraction fails

        if not text_content:
            logger.warning(f"No text content extracted from file: {file_id}")
            file_record.processing_status = 'completed'
            file_record.processed_at = datetime.utcnow()
            db.commit()

            return {
                'file_id': file_id,
                'status': 'completed',
                'message': 'No text content to process',
                'progress': 100
            }

        # AI Processing
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Running AI analysis', 'progress': 40}
        )

        ai_result = generate_ai_metadata_sync(
            text_content=text_content,
            filename=file_record.original_filename
        )

        # Update file record with AI results
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Updating file metadata', 'progress': 80}
        )

        file_record.ai_generated_filename = ai_result['suggested_filename']
        file_record.final_filename = ai_result['suggested_filename']
        file_record.summary = ai_result['summary']
        file_record.ai_tags = [tag['tag'] for tag in ai_result['tags']]
        file_record.processing_status = 'completed'
        file_record.processed_at = datetime.utcnow()

        # Store embedding in Qdrant
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Storing vector embedding', 'progress': 90}
        )

        vector_service.add_vector_sync(
            file_id=str(file_record.id),
            embedding=ai_result['embedding'],
            payload={
                "filename": file_record.final_filename,
                "summary": file_record.summary,
                "tags": file_record.ai_tags,
                "user_id": str(user_id)
            }
        )

        db.commit()

        logger.info(f"File processing completed successfully: {file_id}")

        # Dispatch thumbnail generation task (fire and forget)
        try:
            if file_record.mime_type and (
                file_record.mime_type.startswith('image/') or
                file_record.mime_type == 'application/pdf'
            ):
                from app.workers.tasks.thumbnail import generate_thumbnail, generate_pdf_thumbnail

                if file_record.mime_type.startswith('image/'):
                    generate_thumbnail.delay(file_id)
                    logger.info(f"Dispatched image thumbnail generation for {file_id}")
                elif file_record.mime_type == 'application/pdf':
                    generate_pdf_thumbnail.delay(file_id)
                    logger.info(f"Dispatched PDF thumbnail generation for {file_id}")
        except Exception as e:
            logger.warning(f"Failed to dispatch thumbnail generation: {e}")
            # Don't fail the main task if thumbnail dispatch fails

        return {
            'file_id': file_id,
            'status': 'completed',
            'suggested_filename': ai_result['suggested_filename'],
            'summary': ai_result['summary'],
            'tags': [tag['tag'] for tag in ai_result['tags']],
            'progress': 100
        }

    except Exception as e:
        logger.error(f"Error processing file {file_id}: {e}")

        # Update file status to failed
        if file_record:
            file_record.processing_status = 'failed'
            file_record.error_message = str(e)
            db.commit()

        # Retry the task
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


def generate_ai_metadata_sync(text_content: str, filename: str) -> Dict:
    """
    Synchronous wrapper for AI metadata generation

    This is needed because Celery workers run in sync mode,
    but our AI service methods are async.
    """
    import asyncio

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run async AI analysis in sync context
        result = loop.run_until_complete(
            ai_service.analyze_file(text_content, filename)
        )
        return result
    finally:
        loop.close()


@celery_app.task(
    name="app.workers.tasks.file_processing.generate_ai_metadata",
    max_retries=3
)
def generate_ai_metadata(file_id: str, text_content: str, filename: str) -> Dict:
    """
    Generate AI metadata for a file
    Can be called independently or as part of the full processing pipeline
    """
    try:
        logger.info(f"Generating AI metadata for file: {file_id}")

        result = generate_ai_metadata_sync(text_content, filename)

        logger.info(f"AI metadata generated successfully for: {file_id}")
        return result

    except Exception as e:
        logger.error(f"Error generating AI metadata: {e}")
        raise


@celery_app.task(name="app.workers.tasks.file_processing.cleanup_old_tasks")
def cleanup_old_tasks():
    """
    Periodic task to clean up old Celery task results
    Runs every hour via Celery Beat
    """
    try:
        logger.info("Starting cleanup of old task results")

        # Celery automatically expires results based on result_expires setting
        # This task can be extended to clean up other temporary data

        db = SessionLocal()
        try:
            # Clean up files stuck in 'processing' status for > 1 hour
            from sqlalchemy import and_
            from datetime import timedelta

            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            result = db.execute(
                select(FileModel).where(
                    and_(
                        FileModel.processing_status == 'processing',
                        FileModel.uploaded_at < one_hour_ago
                    )
                )
            )
            stuck_files = result.scalars().all()

            for file in stuck_files:
                file.processing_status = 'failed'
                file.error_message = 'Processing timeout'
                logger.warning(f"Marked stuck file as failed: {file.id}")

            db.commit()

            logger.info(f"Cleanup completed. Marked {len(stuck_files)} stuck files as failed")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")


@celery_app.task(
    name="app.workers.tasks.file_processing.reprocess_file",
    max_retries=2
)
def reprocess_file(file_id: str, user_id: str) -> Dict:
    """
    Reprocess a file that failed or needs re-analysis
    """
    logger.info(f"Reprocessing file: {file_id}")

    db = SessionLocal()
    try:
        # Reset file status
        result = db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == user_id
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise ValueError(f"File not found: {file_id}")

        file_record.processing_status = 'pending'
        file_record.error_message = None
        db.commit()

    finally:
        db.close()

    # Call the main processing task
    return process_uploaded_file(file_id, user_id)

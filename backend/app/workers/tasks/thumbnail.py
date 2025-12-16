from celery import Task
from typing import Dict, Optional
import logging
import io
from datetime import datetime

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.database import File as FileModel
from app.services.storage_service import storage_service
from app.utils.thumbnail_generator import thumbnail_generator
from sqlalchemy import select

logger = logging.getLogger(__name__)


class ThumbnailTask(Task):
    """Base task for thumbnail generation"""
    pass


@celery_app.task(
    bind=True,
    base=ThumbnailTask,
    name="app.workers.tasks.thumbnail.generate_thumbnail",
    max_retries=3
)
def generate_thumbnail(self, file_id: str) -> Dict:
    """
    Generate thumbnail for an image file

    Args:
        file_id: UUID of the file record

    Returns:
        Dict with thumbnail info
    """
    db = SessionLocal()

    try:
        logger.info(f"Starting thumbnail generation for file_id={file_id}")

        # Get file record
        result = db.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise ValueError(f"File not found: {file_id}")

        # Only generate thumbnails for images
        if not file_record.mime_type.startswith('image/'):
            logger.info(f"Skipping thumbnail for non-image file: {file_id}")
            return {
                'file_id': file_id,
                'status': 'skipped',
                'message': 'Not an image file'
            }

        # Download file from storage
        file_data = storage_service.download_file_sync(file_record.file_path)

        # Generate thumbnail using utility
        thumbnail_bytes = thumbnail_generator.generate_image_thumbnail(file_data)

        if not thumbnail_bytes:
            raise ValueError("Failed to generate thumbnail")

        # Upload thumbnail to storage
        thumbnail_path = thumbnail_generator.get_thumbnail_path(
            file_record.file_path,
            str(file_record.id)
        )
        thumbnail_io = io.BytesIO(thumbnail_bytes)
        storage_service.upload_file_sync(
            file_data=thumbnail_io,
            object_name=thumbnail_path,
            content_type='image/jpeg'
        )

        # Update file record with thumbnail path
        file_record.thumbnail_path = thumbnail_path
        db.commit()

        logger.info(f"Thumbnail generated successfully for file: {file_id}")

        return {
            'file_id': file_id,
            'status': 'success',
            'thumbnail_path': thumbnail_path
        }

    except Exception as e:
        logger.error(f"Error generating thumbnail for {file_id}: {e}")
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=ThumbnailTask,
    name="app.workers.tasks.thumbnail.generate_pdf_thumbnail",
    max_retries=2
)
def generate_pdf_thumbnail(self, file_id: str) -> Dict:
    """
    Generate thumbnail for PDF file (first page)
    Requires pdf2image library and poppler

    Args:
        file_id: UUID of the file record

    Returns:
        Dict with thumbnail info
    """
    db = SessionLocal()

    try:
        logger.info(f"Starting PDF thumbnail generation for file_id={file_id}")

        # Get file record
        result = db.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise ValueError(f"File not found: {file_id}")

        # Only generate thumbnails for PDFs
        if file_record.mime_type != 'application/pdf':
            logger.info(f"Skipping thumbnail for non-PDF file: {file_id}")
            return {
                'file_id': file_id,
                'status': 'skipped',
                'message': 'Not a PDF file'
            }

        # Download file from storage
        file_data = storage_service.download_file_sync(file_record.file_path)

        # Generate PDF thumbnail using utility
        thumbnail_bytes = thumbnail_generator.generate_pdf_thumbnail(file_data)

        if not thumbnail_bytes:
            raise ValueError("Failed to generate PDF thumbnail")

        # Upload thumbnail to storage
        thumbnail_path = thumbnail_generator.get_thumbnail_path(
            file_record.file_path,
            str(file_record.id)
        )
        thumbnail_io = io.BytesIO(thumbnail_bytes)
        storage_service.upload_file_sync(
            file_data=thumbnail_io,
            object_name=thumbnail_path,
            content_type='image/jpeg'
        )

        # Update file record with thumbnail path
        file_record.thumbnail_path = thumbnail_path
        db.commit()

        logger.info(f"PDF thumbnail generated successfully for file: {file_id}")

        return {
            'file_id': file_id,
            'status': 'success',
            'thumbnail_path': thumbnail_path
        }

    except Exception as e:
        logger.error(f"Error generating PDF thumbnail for {file_id}: {e}")
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


@celery_app.task(
    name="app.workers.tasks.thumbnail.batch_generate_thumbnails",
)
def batch_generate_thumbnails(file_ids: list) -> Dict:
    """
    Generate thumbnails for multiple files

    Args:
        file_ids: List of file IDs

    Returns:
        Dict with batch results
    """
    logger.info(f"Batch thumbnail generation for {len(file_ids)} files")

    results = []
    for file_id in file_ids:
        try:
            result = generate_thumbnail(file_id)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to generate thumbnail for {file_id}: {e}")
            results.append({
                'file_id': file_id,
                'status': 'failed',
                'error': str(e)
            })

    return {
        'total': len(file_ids),
        'results': results
    }

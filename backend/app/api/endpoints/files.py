from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
import logging
import io
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.database import User, File as FileModel
from app.schemas.file import FileResponse, FileListResponse, FileUploadResponse, FileUpdate
from app.services.storage_service import storage_service
from app.services.ai_service import ai_service
from app.services.vector_service import vector_service
from app.utils.file_utils import (
    get_mime_type,
    is_allowed_file,
    generate_unique_filename,
    sanitize_filename
)
from app.utils.text_extractor import TextExtractor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file and process it with AI
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )

        # Check if file type is allowed
        if not is_allowed_file(file.filename, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )

        # Read file data
        file_data = await file.read()
        file_size = len(file_data)

        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
            )

        # Calculate file hash
        file_io = io.BytesIO(file_data)
        file_hash = storage_service.calculate_hash(file_io)

        # Check for duplicate
        result = await db.execute(
            select(FileModel).where(
                FileModel.file_hash == file_hash,
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False
            )
        )
        existing_file = result.scalar_one_or_none()

        if existing_file:
            logger.info(f"Duplicate file detected: {file_hash}")
            return FileUploadResponse(
                file_id=existing_file.id,
                message="File already exists",
                status="duplicate"
            )

        # Get MIME type
        mime_type = get_mime_type(file.filename, file_data)

        # Generate storage path
        storage_path = generate_unique_filename(file.filename, str(current_user.id), file_hash)

        # Upload to MinIO
        file_io.seek(0)
        await storage_service.upload_file(
            file_data=file_io,
            object_name=storage_path,
            content_type=mime_type,
            metadata={
                "original_filename": file.filename,
                "user_id": str(current_user.id)
            }
        )

        # Create file record in database
        sanitized_filename = sanitize_filename(file.filename)
        file_record = FileModel(
            user_id=current_user.id,
            original_filename=file.filename,
            final_filename=sanitized_filename,
            file_path=storage_path,
            file_size=file_size,
            mime_type=mime_type,
            file_hash=file_hash,
            processing_status='pending'
        )

        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        logger.info(f"File uploaded: {file_record.id}")

        # Start AI processing in background (for now, do it synchronously)
        try:
            # Extract text
            text_content = TextExtractor.extract_text(file_data, mime_type, file.filename)

            if text_content:
                # AI analysis
                ai_result = await ai_service.analyze_file(text_content, file.filename)

                # Update file record with AI results
                file_record.ai_generated_filename = ai_result['suggested_filename']
                file_record.final_filename = ai_result['suggested_filename']
                file_record.summary = ai_result['summary']
                file_record.ai_tags = [tag['tag'] for tag in ai_result['tags']]
                file_record.processing_status = 'completed'
                file_record.processed_at = datetime.utcnow()

                # Store embedding in Qdrant
                await vector_service.add_vector(
                    file_id=str(file_record.id),
                    embedding=ai_result['embedding'],
                    payload={
                        "filename": file_record.final_filename,
                        "summary": file_record.summary,
                        "tags": file_record.ai_tags,
                        "user_id": str(current_user.id)
                    }
                )

                logger.info(f"AI processing completed for file: {file_record.id}")
            else:
                file_record.processing_status = 'completed'
                file_record.processed_at = datetime.utcnow()
                logger.warning(f"No text extracted from file: {file_record.id}")

        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
            file_record.processing_status = 'failed'

        await db.commit()
        await db.refresh(file_record)

        return FileUploadResponse(
            file_id=file_record.id,
            message="File uploaded successfully",
            status=file_record.processing_status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List user's files with pagination and search
    """
    try:
        # Build query
        query = select(FileModel).where(
            FileModel.user_id == current_user.id,
            FileModel.is_deleted == False
        )

        # Add search filter
        if search:
            search_filter = or_(
                FileModel.original_filename.ilike(f"%{search}%"),
                FileModel.final_filename.ilike(f"%{search}%"),
                FileModel.summary.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.order_by(FileModel.uploaded_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await db.execute(query)
        files = result.scalars().all()

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size

        return FileListResponse(
            items=[FileResponse.from_orm(f) for f in files],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get file details"""
    try:
        result = await db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        return FileResponse.from_orm(file_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file"
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get presigned URL for file download"""
    try:
        result = await db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Generate presigned URL
        url = await storage_service.get_presigned_url(file_record.file_path)

        return {
            "download_url": url,
            "filename": file_record.final_filename,
            "expires_in": 3600  # 1 hour
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )


@router.put("/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: str,
    file_update: FileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update file metadata"""
    try:
        result = await db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Update fields
        if file_update.final_filename:
            file_record.final_filename = sanitize_filename(file_update.final_filename)

        if file_update.summary:
            file_record.summary = file_update.summary

        if file_update.ai_tags:
            file_record.ai_tags = file_update.ai_tags

        await db.commit()
        await db.refresh(file_record)

        logger.info(f"File updated: {file_id}")

        return FileResponse.from_orm(file_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update file"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete file"""
    try:
        result = await db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Soft delete
        file_record.is_deleted = True
        await db.commit()

        logger.info(f"File deleted: {file_id}")

        return {"message": "File deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )

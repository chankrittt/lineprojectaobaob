from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, Collection, CollectionFile

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas
class CollectionCreate(BaseModel):
    name: str
    description: str = None
    is_public: bool = False


class CollectionResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str = None
    is_public: bool
    created_at: datetime
    updated_at: datetime = None

    class Config:
        from_attributes = True


@router.post("/", response_model=CollectionResponse)
async def create_collection(
    collection_data: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new collection"""
    try:
        collection = Collection(
            user_id=current_user.id,
            name=collection_data.name,
            description=collection_data.description,
            is_public=collection_data.is_public
        )

        db.add(collection)
        await db.commit()
        await db.refresh(collection)

        logger.info(f"Created collection: {collection.id}")

        return CollectionResponse.from_orm(collection)

    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create collection"
        )


@router.get("/", response_model=List[CollectionResponse])
async def list_collections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's collections"""
    try:
        result = await db.execute(
            select(Collection).where(Collection.user_id == current_user.id)
        )
        collections = result.scalars().all()

        return [CollectionResponse.from_orm(c) for c in collections]

    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list collections"
        )


@router.post("/{collection_id}/files/{file_id}")
async def add_file_to_collection(
    collection_id: str,
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a file to a collection"""
    try:
        # Verify collection ownership
        result = await db.execute(
            select(Collection).where(
                Collection.id == collection_id,
                Collection.user_id == current_user.id
            )
        )
        collection = result.scalar_one_or_none()

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )

        # Check if file already in collection
        result = await db.execute(
            select(CollectionFile).where(
                CollectionFile.collection_id == collection_id,
                CollectionFile.file_id == file_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return {"message": "File already in collection"}

        # Add file to collection
        collection_file = CollectionFile(
            collection_id=collection_id,
            file_id=file_id
        )

        db.add(collection_file)
        await db.commit()

        logger.info(f"Added file {file_id} to collection {collection_id}")

        return {"message": "File added to collection"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding file to collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add file to collection"
        )


@router.delete("/{collection_id}/files/{file_id}")
async def remove_file_from_collection(
    collection_id: str,
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a file from a collection"""
    try:
        # Verify collection ownership
        result = await db.execute(
            select(Collection).where(
                Collection.id == collection_id,
                Collection.user_id == current_user.id
            )
        )
        collection = result.scalar_one_or_none()

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )

        # Remove file from collection
        result = await db.execute(
            select(CollectionFile).where(
                CollectionFile.collection_id == collection_id,
                CollectionFile.file_id == file_id
            )
        )
        collection_file = result.scalar_one_or_none()

        if not collection_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not in collection"
            )

        await db.delete(collection_file)
        await db.commit()

        logger.info(f"Removed file {file_id} from collection {collection_id}")

        return {"message": "File removed from collection"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing file from collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove file from collection"
        )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, File as FileModel
from app.schemas.file import FileResponse
from app.services.ai_service import ai_service
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/semantic", response_model=List[FileResponse])
async def semantic_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Semantic search using AI embeddings
    Search files by meaning, not just keywords
    """
    try:
        # Generate embedding for search query
        query_embedding = await ai_service.generate_embedding(query)

        # Search in Qdrant
        similar_results = await vector_service.search_similar(
            query_vector=query_embedding,
            limit=limit,
            score_threshold=0.6,
            filter_conditions={"user_id": str(current_user.id)}
        )

        if not similar_results:
            return []

        # Get file IDs
        file_ids = [result['file_id'] for result in similar_results]

        # Get files from database
        result = await db.execute(
            select(FileModel).where(
                FileModel.id.in_(file_ids),
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False
            )
        )
        files = result.scalars().all()

        # Sort by score (match order from Qdrant)
        file_dict = {str(f.id): f for f in files}
        sorted_files = []
        for similar in similar_results:
            file_id = similar['file_id']
            if file_id in file_dict:
                sorted_files.append(file_dict[file_id])

        logger.info(f"Semantic search: '{query}' found {len(sorted_files)} results")

        return [FileResponse.from_orm(f) for f in sorted_files]

    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/suggest-tags")
async def suggest_tags(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tag suggestions based on query
    """
    try:
        # Get all unique tags from user's files
        result = await db.execute(
            select(FileModel.ai_tags).where(
                FileModel.user_id == current_user.id,
                FileModel.is_deleted == False,
                FileModel.ai_tags.isnot(None)
            )
        )

        all_tags = set()
        for row in result.scalars():
            if row:
                all_tags.update(row)

        # Filter tags that match query
        query_lower = query.lower()
        matching_tags = [
            tag for tag in all_tags
            if query_lower in tag.lower()
        ]

        return {
            "tags": sorted(matching_tags)[:10]
        }

    except Exception as e:
        logger.error(f"Error suggesting tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suggest tags"
        )

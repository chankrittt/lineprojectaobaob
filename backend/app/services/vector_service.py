from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
import logging
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.QDRANT_VECTOR_SIZE
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {e}")
            raise

    async def add_vector(
        self,
        file_id: str,
        embedding: List[float],
        payload: Dict = None
    ) -> str:
        """Add vector to Qdrant"""
        try:
            point_id = str(uuid.uuid4())

            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "file_id": file_id,
                    **(payload or {})
                }
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            logger.info(f"Added vector for file: {file_id}")
            return point_id

        except Exception as e:
            logger.error(f"Error adding vector: {e}")
            raise

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar vectors"""
        try:
            # Build filter if provided
            search_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                search_filter = Filter(must=conditions)

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter
            )

            # Format results
            formatted_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "file_id": result.payload.get("file_id"),
                    "payload": result.payload
                }
                for result in results
            ]

            logger.info(f"Found {len(formatted_results)} similar vectors")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise

    async def delete_vector(self, point_id: str):
        """Delete vector from Qdrant"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            logger.info(f"Deleted vector: {point_id}")

        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            raise

    async def delete_by_file_id(self, file_id: str):
        """Delete all vectors for a specific file"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="file_id",
                            match=MatchValue(value=file_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted all vectors for file: {file_id}")

        except Exception as e:
            logger.error(f"Error deleting vectors by file_id: {e}")
            raise

    async def get_collection_info(self) -> Dict:
        """Get collection statistics"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.name,
                "vector_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise


# Singleton instance
vector_service = VectorService()

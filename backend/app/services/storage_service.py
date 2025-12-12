from minio import Minio
from minio.error import S3Error
from typing import Optional, BinaryIO
import hashlib
import logging
from datetime import timedelta
import io

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise

    async def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict] = None
    ) -> str:
        """Upload file to MinIO"""
        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Seek back to start

            # Upload
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
                metadata=metadata or {}
            )

            logger.info(f"Uploaded file: {object_name} ({file_size} bytes)")
            return object_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def download_file(self, object_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise

    async def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Get presigned URL for file download"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error getting presigned URL: {e}")
            raise

    async def delete_file(self, object_name: str):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted file: {object_name}")
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise

    async def file_exists(self, object_name: str) -> bool:
        """Check if file exists"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    @staticmethod
    def calculate_hash(file_data: BinaryIO) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        file_data.seek(0)
        while chunk := file_data.read(8192):
            sha256.update(chunk)
        file_data.seek(0)
        return sha256.hexdigest()

    async def get_file_info(self, object_name: str) -> dict:
        """Get file metadata"""
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                "size": stat.size,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata
            }
        except S3Error as e:
            logger.error(f"Error getting file info: {e}")
            raise


# Singleton instance
storage_service = StorageService()

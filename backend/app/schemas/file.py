from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID


class FileBase(BaseModel):
    original_filename: str
    final_filename: str


class FileCreate(BaseModel):
    original_filename: str
    file_size: int
    mime_type: Optional[str] = None


class FileUpdate(BaseModel):
    final_filename: Optional[str] = None
    summary: Optional[str] = None
    ai_tags: Optional[List[str]] = None


class TagResponse(BaseModel):
    tag: str
    confidence: float
    is_user_confirmed: bool = False


class FileResponse(BaseModel):
    id: UUID
    user_id: UUID
    original_filename: str
    ai_generated_filename: Optional[str] = None
    final_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    file_hash: Optional[str] = None
    summary: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    version: int
    processing_status: str
    is_deleted: bool
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    items: List[FileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FileUploadResponse(BaseModel):
    file_id: UUID
    message: str
    status: str

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    picture_url: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

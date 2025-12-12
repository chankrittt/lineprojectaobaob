from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.database import User
from app.schemas.user import TokenResponse, UserResponse, UserCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/line", response_model=TokenResponse)
async def line_login(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    LINE Login - Create or get user and return JWT token
    """
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.line_user_id == user_data.line_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Create new user
            user = User(
                line_user_id=user_data.line_user_id,
                display_name=user_data.display_name,
                picture_url=user_data.picture_url
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created new user: {user.line_user_id}")
        else:
            # Update existing user info
            user.display_name = user_data.display_name
            user.picture_url = user_data.picture_url
            await db.commit()
            await db.refresh(user)
            logger.info(f"Updated existing user: {user.line_user_id}")

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )

    except Exception as e:
        logger.error(f"Error in LINE login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse.from_orm(user)

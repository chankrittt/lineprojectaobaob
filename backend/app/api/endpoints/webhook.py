from fastapi import APIRouter, Request, HTTPException, status, Header, Depends
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    PostbackEvent,
    FileMessage,
    ImageMessage,
    VideoMessage,
    TextMessage
)
import logging
import magic
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from typing import Optional
from datetime import datetime, timedelta
import io

from app.core.config import settings
from app.core.security import verify_line_signature
from app.core.database import SessionLocal
from app.models.database import User as UserModel, File as FileModel
from app.services.line_service import line_service
from app.services.storage_service import storage_service
from app.templates.flex_messages import flex_templates
from app.workers.tasks.file_processing import process_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize LINE Bot API
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_or_create_user(line_user_id: str, db: Session) -> Optional[UserModel]:
    """Get or create user from LINE ID"""
    try:
        # Check if user exists
        result = db.execute(
            select(UserModel).where(UserModel.line_user_id == line_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Get profile from LINE
            profile = line_service.get_user_profile(line_user_id)
            if not profile:
                return None

            # Create new user
            user = UserModel(
                line_user_id=line_user_id,
                display_name=profile['display_name'],
                picture_url=profile.get('picture_url')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {line_user_id}")

        return user

    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        return None


@router.post("/line")
async def line_webhook(
    request: Request,
    x_line_signature: str = Header(None)
):
    """
    LINE webhook endpoint
    Receives messages from LINE and processes them
    """
    try:
        # Get request body
        body = await request.body()

        # Verify signature
        if not x_line_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )

        if not verify_line_signature(body, x_line_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

        # Handle webhook
        handler.handle(body.decode('utf-8'), x_line_signature)

        return {"status": "ok"}

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    except Exception as e:
        logger.error(f"Error in LINE webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    """Handle file messages from LINE"""
    try:
        logger.info(f"Received file message: {event.message.id}")

        db = SessionLocal()
        try:
            # Get or create user
            user = get_or_create_user_sync(event.source.user_id, db)
            if not user:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถระบุผู้ใช้ได้")
                return

            # Download file from LINE
            file_content = line_service.download_content(event.message.id)
            if not file_content:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถดาวน์โหลดไฟล์ได้")
                return

            # Get file info
            filename = event.message.file_name
            file_size = event.message.file_size

            # Detect MIME type
            mime_type = magic.from_buffer(file_content, mime=True)

            # Upload to MinIO
            file_hash = storage_service.generate_file_hash(file_content)
            object_name = f"uploads/{user.id}/{file_hash}/{filename}"

            file_io = io.BytesIO(file_content)
            storage_service.upload_file_sync(
                file_data=file_io,
                object_name=object_name,
                content_type=mime_type
            )

            # Create file record
            file_record = FileModel(
                user_id=user.id,
                original_filename=filename,
                final_filename=filename,
                file_path=object_name,
                file_size=file_size,
                mime_type=mime_type,
                file_hash=file_hash,
                processing_status='pending'
            )
            db.add(file_record)
            db.commit()
            db.refresh(file_record)

            # Send confirmation with Flex Message
            flex_content = flex_templates.file_upload_confirmation(
                filename=filename,
                file_size=file_size,
                file_type=mime_type,
                file_id=str(file_record.id)
            )
            line_service.reply_flex(
                event.reply_token,
                alt_text=f"อัปโหลด {filename} สำเร็จ",
                flex_content=flex_content
            )

            # Start background processing
            process_uploaded_file.delay(str(file_record.id), str(user.id))

            logger.info(f"File uploaded and queued for processing: {file_record.id}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling file message: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาดในการอัปโหลดไฟล์")


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """Handle image messages from LINE"""
    try:
        logger.info(f"Received image message: {event.message.id}")

        db = SessionLocal()
        try:
            user = get_or_create_user_sync(event.source.user_id, db)
            if not user:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถระบุผู้ใช้ได้")
                return

            # Download image
            file_content = line_service.download_content(event.message.id)
            if not file_content:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถดาวน์โหลดรูปภาพได้")
                return

            # Detect MIME type and extension
            mime_type = magic.from_buffer(file_content, mime=True)
            ext = mime_type.split('/')[-1] if '/' in mime_type else 'jpg'
            filename = f"image_{event.message.id}.{ext}"
            file_size = len(file_content)

            # Upload to MinIO
            file_hash = storage_service.generate_file_hash(file_content)
            object_name = f"uploads/{user.id}/{file_hash}/{filename}"

            file_io = io.BytesIO(file_content)
            storage_service.upload_file_sync(
                file_data=file_io,
                object_name=object_name,
                content_type=mime_type
            )

            # Create file record
            file_record = FileModel(
                user_id=user.id,
                original_filename=filename,
                final_filename=filename,
                file_path=object_name,
                file_size=file_size,
                mime_type=mime_type,
                file_hash=file_hash,
                processing_status='pending'
            )
            db.add(file_record)
            db.commit()
            db.refresh(file_record)

            # Send confirmation
            flex_content = flex_templates.file_upload_confirmation(
                filename=filename,
                file_size=file_size,
                file_type=mime_type,
                file_id=str(file_record.id)
            )
            line_service.reply_flex(
                event.reply_token,
                alt_text=f"อัปโหลดรูปภาพสำเร็จ",
                flex_content=flex_content
            )

            # Start processing
            process_uploaded_file.delay(str(file_record.id), str(user.id))

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling image message: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ")


@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    """Handle video messages from LINE"""
    try:
        logger.info(f"Received video message: {event.message.id}")

        db = SessionLocal()
        try:
            user = get_or_create_user_sync(event.source.user_id, db)
            if not user:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถระบุผู้ใช้ได้")
                return

            # Download video
            file_content = line_service.download_content(event.message.id)
            if not file_content:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถดาวน์โหลดวิดีโอได้")
                return

            mime_type = magic.from_buffer(file_content, mime=True)
            ext = mime_type.split('/')[-1] if '/' in mime_type else 'mp4'
            filename = f"video_{event.message.id}.{ext}"
            file_size = len(file_content)

            # Upload to MinIO
            file_hash = storage_service.generate_file_hash(file_content)
            object_name = f"uploads/{user.id}/{file_hash}/{filename}"

            file_io = io.BytesIO(file_content)
            storage_service.upload_file_sync(
                file_data=file_io,
                object_name=object_name,
                content_type=mime_type
            )

            # Create file record
            file_record = FileModel(
                user_id=user.id,
                original_filename=filename,
                final_filename=filename,
                file_path=object_name,
                file_size=file_size,
                mime_type=mime_type,
                file_hash=file_hash,
                processing_status='pending'
            )
            db.add(file_record)
            db.commit()
            db.refresh(file_record)

            # Send confirmation
            flex_content = flex_templates.file_upload_confirmation(
                filename=filename,
                file_size=file_size,
                file_type=mime_type,
                file_id=str(file_record.id)
            )
            line_service.reply_flex(
                event.reply_token,
                alt_text=f"อัปโหลดวิดีโอสำเร็จ",
                flex_content=flex_content
            )

            # Start processing
            process_uploaded_file.delay(str(file_record.id), str(user.id))

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling video message: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาดในการอัปโหลดวิดีโอ")


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """Handle text messages and commands from LINE"""
    try:
        user_message = event.message.text.strip()
        logger.info(f"Received text message: {user_message}")

        db = SessionLocal()
        try:
            user = get_or_create_user_sync(event.source.user_id, db)
            if not user:
                line_service.reply_text(event.reply_token, "ขออภัย ไม่สามารถระบุผู้ใช้ได้")
                return

            # Handle commands
            if user_message.startswith("/search"):
                handle_search_command(event, user, db)
            elif user_message == "/list":
                handle_list_command(event, user, db)
            elif user_message == "/stats":
                handle_stats_command(event, user, db)
            elif user_message == "/help" or user_message == "help":
                handle_help_command(event)
            else:
                # Default welcome message with quick reply
                quick_reply = line_service.create_quick_reply([
                    {'label': '🔍 ค้นหา', 'text': '/search'},
                    {'label': '📋 รายการไฟล์', 'text': '/list'},
                    {'label': '📊 สถิติ', 'text': '/stats'},
                    {'label': 'ℹ️ ช่วยเหลือ', 'text': '/help'}
                ])
                line_service.reply_text(
                    event.reply_token,
                    "สวัสดีค่ะ! 👋\n\n📤 ส่งไฟล์/รูปภาพ/วิดีโอมาได้เลย\n💡 หรือใช้คำสั่งด้านล่างเพื่อจัดการไฟล์",
                    quick_reply=quick_reply
                )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาด")


@handler.add(PostbackEvent)
def handle_postback(event):
    """Handle postback events (button clicks)"""
    try:
        postback_data = event.postback.data
        logger.info(f"Received postback: {postback_data}")

        # Parse postback data
        data_dict = dict(item.split('=') for item in postback_data.split('&'))

        action = data_dict.get('action')

        if action == 'share':
            file_id = data_dict.get('file_id')
            line_service.reply_text(
                event.reply_token,
                f"ฟีเจอร์แชร์ไฟล์กำลังพัฒนา\nFile ID: {file_id}"
            )
        else:
            line_service.reply_text(event.reply_token, "ไม่รู้จักคำสั่งนี้")

    except Exception as e:
        logger.error(f"Error handling postback: {e}")


# Command handlers

def handle_search_command(event, user: UserModel, db: Session):
    """Handle /search command"""
    try:
        query = event.message.text.replace("/search", "").strip()

        if not query:
            line_service.reply_text(
                event.reply_token,
                "กรุณาระบุคำค้นหา\nตัวอย่าง: /search ใบเสร็จ"
            )
            return

        # Search files (simple text search for now)
        result = db.execute(
            select(FileModel)
            .where(
                FileModel.user_id == user.id,
                FileModel.is_deleted == False,
                (FileModel.final_filename.ilike(f"%{query}%") |
                 FileModel.summary.ilike(f"%{query}%"))
            )
            .order_by(desc(FileModel.uploaded_at))
            .limit(10)
        )
        files = result.scalars().all()

        # Convert to dict
        file_dicts = [
            {
                'id': str(f.id),
                'final_filename': f.final_filename,
                'summary': f.summary or 'ไม่มีสรุป'
            }
            for f in files
        ]

        # Send Flex Message with results
        flex_content = flex_templates.search_results(
            query=query,
            files=file_dicts,
            total_count=len(file_dicts)
        )
        line_service.reply_flex(
            event.reply_token,
            alt_text=f"ผลการค้นหา: {query}",
            flex_content=flex_content
        )

    except Exception as e:
        logger.error(f"Error in search command: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาดในการค้นหา")


def handle_list_command(event, user: UserModel, db: Session):
    """Handle /list command"""
    try:
        # Get recent files
        result = db.execute(
            select(FileModel)
            .where(
                FileModel.user_id == user.id,
                FileModel.is_deleted == False
            )
            .order_by(desc(FileModel.uploaded_at))
            .limit(10)
        )
        files = result.scalars().all()

        if not files:
            line_service.reply_text(event.reply_token, "ยังไม่มีไฟล์ในระบบ")
            return

        # Build message
        message = "📋 ไฟล์ล่าสุด 10 ไฟล์:\n\n"
        for i, f in enumerate(files, 1):
            status_emoji = "✅" if f.processing_status == "completed" else "⏳"
            message += f"{i}. {status_emoji} {f.final_filename}\n"

        quick_reply = line_service.create_quick_reply([
            {'label': '🔍 ค้นหา', 'text': '/search'},
            {'label': '📊 สถิติ', 'text': '/stats'}
        ])

        line_service.reply_text(event.reply_token, message, quick_reply=quick_reply)

    except Exception as e:
        logger.error(f"Error in list command: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาดในการดึงรายการไฟล์")


def handle_stats_command(event, user: UserModel, db: Session):
    """Handle /stats command"""
    try:
        # Get statistics
        total_files = db.execute(
            select(func.count(FileModel.id))
            .where(
                FileModel.user_id == user.id,
                FileModel.is_deleted == False
            )
        ).scalar()

        total_size = db.execute(
            select(func.sum(FileModel.file_size))
            .where(
                FileModel.user_id == user.id,
                FileModel.is_deleted == False
            )
        ).scalar() or 0

        # Files by type
        type_result = db.execute(
            select(
                func.substring(FileModel.mime_type, 1, func.position('/' in FileModel.mime_type) - 1).label('type'),
                func.count(FileModel.id).label('count')
            )
            .where(
                FileModel.user_id == user.id,
                FileModel.is_deleted == False
            )
            .group_by('type')
        )
        by_type = {row.type: row.count for row in type_result}

        # Recent uploads (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_uploads = db.execute(
            select(func.count(FileModel.id))
            .where(
                FileModel.user_id == user.id,
                FileModel.is_deleted == False,
                FileModel.uploaded_at >= seven_days_ago
            )
        ).scalar()

        # Send Flex Message
        flex_content = flex_templates.statistics(
            total_files=total_files or 0,
            total_size=total_size,
            by_type=by_type,
            recent_uploads=recent_uploads or 0
        )
        line_service.reply_flex(
            event.reply_token,
            alt_text="สถิติการใช้งาน",
            flex_content=flex_content
        )

    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาดในการดึงสถิติ")


def handle_help_command(event):
    """Handle /help command"""
    try:
        flex_content = flex_templates.help_menu()
        line_service.reply_flex(
            event.reply_token,
            alt_text="คำสั่งที่ใช้ได้",
            flex_content=flex_content
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        line_service.reply_text(event.reply_token, "ขออภัย เกิดข้อผิดพลาด")


# Helper function for sync user creation
def get_or_create_user_sync(line_user_id: str, db: Session) -> Optional[UserModel]:
    """Synchronous version of get_or_create_user for webhook handlers"""
    try:
        result = db.execute(
            select(UserModel).where(UserModel.line_user_id == line_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            profile = line_service.get_user_profile(line_user_id)
            if not profile:
                return None

            user = UserModel(
                line_user_id=line_user_id,
                display_name=profile['display_name'],
                picture_url=profile.get('picture_url')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {line_user_id}")

        return user

    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        return None

from celery import Task
from typing import Dict, Optional, List
import logging
from datetime import datetime

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.database import File as FileModel, User
from app.services.line_service import line_service
from app.templates.flex_messages import flex_templates
from sqlalchemy import select

logger = logging.getLogger(__name__)


class NotificationTask(Task):
    """Base task for notifications"""
    pass


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="app.workers.tasks.notifications.send_processing_complete",
    max_retries=3
)
def send_processing_complete(self, file_id: str, user_id: str) -> Dict:
    """
    Send notification when file processing is complete

    Args:
        file_id: UUID of the file record
        user_id: UUID of the user

    Returns:
        Dict with notification status
    """
    db = SessionLocal()

    try:
        logger.info(f"Sending processing complete notification for file_id={file_id}")

        # Get file record
        result = db.execute(
            select(FileModel).where(
                FileModel.id == file_id,
                FileModel.user_id == user_id
            )
        )
        file_record = result.scalar_one_or_none()

        if not file_record:
            raise ValueError(f"File not found: {file_id}")

        # Get user record
        user_result = db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Only send if processing was completed
        if file_record.processing_status == 'completed':
            # Create Flex Message
            flex_content = flex_templates.processing_complete(
                filename=file_record.original_filename,
                ai_filename=file_record.ai_generated_filename or file_record.final_filename,
                summary=file_record.summary or 'ไม่มีสรุป',
                tags=file_record.ai_tags or [],
                file_id=str(file_record.id),
                thumbnail_url=None  # TODO: Get thumbnail URL from MinIO
            )

            # Send to user via LINE
            line_service.push_flex(
                user.line_user_id,
                alt_text=f"✅ ประมวลผล {file_record.final_filename} เสร็จแล้ว",
                flex_content=flex_content
            )

            logger.info(
                f"Sent processing complete Flex Message to user {user.line_user_id}: "
                f"File '{file_record.final_filename}'"
            )

            return {
                'file_id': file_id,
                'user_id': user_id,
                'status': 'sent',
                'notification_type': 'processing_complete'
            }
        else:
            logger.info(f"File {file_id} not completed, skipping notification")
            return {
                'file_id': file_id,
                'user_id': user_id,
                'status': 'skipped',
                'reason': 'not_completed'
            }

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()


@celery_app.task(
    name="app.workers.tasks.notifications.send_processing_failed",
    max_retries=3
)
def send_processing_failed(file_id: str, user_id: str, error_message: str) -> Dict:
    """
    Send notification when file processing fails

    Args:
        file_id: UUID of the file record
        user_id: UUID of the user
        error_message: Error message

    Returns:
        Dict with notification status
    """
    db = SessionLocal()

    try:
        logger.info(f"Sending processing failed notification for file_id={file_id}")

        # Get user and file
        user_result = db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        file_result = db.execute(
            select(FileModel).where(FileModel.id == file_id)
        )
        file_record = file_result.scalar_one_or_none()

        if user and file_record:
            # Send simple text notification
            message = f"❌ ประมวลผลล้มเหลว\n📄 {file_record.original_filename}\n\n{error_message}\n\nกรุณาลองใหม่อีกครั้ง"

            line_service.push_text(user.line_user_id, message)

            logger.info(f"Sent processing failed notification to user {user.line_user_id}")

        return {
            'file_id': file_id,
            'user_id': user_id,
            'status': 'sent',
            'notification_type': 'processing_failed'
        }

    except Exception as e:
        logger.error(f"Error sending failed notification: {e}")
        return {'status': 'failed', 'error': str(e)}

    finally:
        db.close()


@celery_app.task(
    name="app.workers.tasks.notifications.send_storage_quota_alert",
    max_retries=3
)
def send_storage_quota_alert(user_id: str, usage_percent: float) -> Dict:
    """
    Send notification when storage quota reaches threshold

    Args:
        user_id: UUID of the user
        usage_percent: Current storage usage percentage

    Returns:
        Dict with notification status
    """
    logger.info(f"Sending storage quota alert for user_id={user_id}: {usage_percent}%")

    # TODO: Send LINE notification
    # For now, just log
    logger.warning(
        f"Storage quota alert: user_id={user_id}, usage={usage_percent}%"
    )

    return {
        'user_id': user_id,
        'status': 'sent',
        'notification_type': 'storage_quota_alert',
        'usage_percent': usage_percent
    }


@celery_app.task(
    name="app.workers.tasks.notifications.send_daily_summary"
)
def send_daily_summary(user_id: str) -> Dict:
    """
    Send daily summary of uploaded files

    Args:
        user_id: UUID of the user

    Returns:
        Dict with notification status
    """
    db = SessionLocal()

    try:
        logger.info(f"Sending daily summary for user_id={user_id}")

        # Get today's files
        from datetime import datetime, timedelta

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        result = db.execute(
            select(FileModel).where(
                FileModel.user_id == user_id,
                FileModel.uploaded_at >= today_start,
                FileModel.uploaded_at < today_end,
                FileModel.is_deleted == False
            )
        )
        files = result.scalars().all()

        logger.info(f"Daily summary for user {user_id}: {len(files)} files uploaded today")

        # TODO: Send LINE notification with summary
        # For now, just log

        return {
            'user_id': user_id,
            'status': 'sent',
            'notification_type': 'daily_summary',
            'files_count': len(files)
        }

    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")
        raise

    finally:
        db.close()


@celery_app.task(
    name="app.workers.tasks.notifications.send_batch_notifications"
)
def send_batch_notifications(notifications: List[Dict]) -> Dict:
    """
    Send multiple notifications in batch

    Args:
        notifications: List of notification dicts with type and data

    Returns:
        Dict with batch results
    """
    logger.info(f"Sending batch of {len(notifications)} notifications")

    results = []
    for notification in notifications:
        try:
            notification_type = notification.get('type')
            data = notification.get('data', {})

            if notification_type == 'processing_complete':
                result = send_processing_complete(data['file_id'], data['user_id'])
            elif notification_type == 'processing_failed':
                result = send_processing_failed(
                    data['file_id'],
                    data['user_id'],
                    data.get('error_message', 'Unknown error')
                )
            elif notification_type == 'storage_quota_alert':
                result = send_storage_quota_alert(
                    data['user_id'],
                    data['usage_percent']
                )
            else:
                result = {'status': 'unknown_type', 'type': notification_type}

            results.append(result)

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            results.append({'status': 'failed', 'error': str(e)})

    return {
        'total': len(notifications),
        'results': results
    }

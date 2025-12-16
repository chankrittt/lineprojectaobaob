from celery import Task
from typing import Dict, Optional, List
import logging
from datetime import datetime

from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.database import File as FileModel, User
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

        # TODO: Send LINE notification using Flex Message
        # For now, just log
        logger.info(
            f"Processing complete notification for user {user.line_user_id}: "
            f"File '{file_record.final_filename}' processed successfully"
        )

        # In production, this would send a LINE Flex Message like:
        # {
        #   "type": "flex",
        #   "altText": "File processing complete",
        #   "contents": {
        #     "type": "bubble",
        #     "body": {
        #       "type": "box",
        #       "layout": "vertical",
        #       "contents": [
        #         {"type": "text", "text": "✅ Processing Complete", "weight": "bold"},
        #         {"type": "text", "text": file_record.final_filename},
        #         {"type": "text", "text": file_record.summary}
        #       ]
        #     }
        #   }
        # }

        return {
            'file_id': file_id,
            'user_id': user_id,
            'status': 'sent',
            'notification_type': 'processing_complete'
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
    logger.info(f"Sending processing failed notification for file_id={file_id}")

    # TODO: Send LINE notification
    # For now, just log
    logger.warning(
        f"Processing failed notification: file_id={file_id}, error={error_message}"
    )

    return {
        'file_id': file_id,
        'user_id': user_id,
        'status': 'sent',
        'notification_type': 'processing_failed'
    }


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

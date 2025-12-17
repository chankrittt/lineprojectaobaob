"""
LINE Service - Handle LINE Bot operations

Includes:
- File download from LINE CDN
- Send Flex Messages
- Send notifications
- Reply with templates
"""

import logging
import httpx
from typing import Optional, Dict, List, Any
from linebot import LineBotApi
from linebot.models import (
    TextSendMessage,
    FlexSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction,
    PostbackAction,
    ImageSendMessage
)
import io

from app.core.config import settings

logger = logging.getLogger(__name__)


class LineService:
    """Service for LINE Bot operations"""

    def __init__(self):
        self.bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.channel_secret = settings.LINE_CHANNEL_SECRET

    async def download_content(self, message_id: str) -> Optional[bytes]:
        """
        Download file content from LINE CDN

        Args:
            message_id: LINE message ID containing the file

        Returns:
            File bytes or None if failed
        """
        try:
            # Get message content from LINE
            message_content = self.bot_api.get_message_content(message_id)

            # Read content as bytes
            content_bytes = io.BytesIO()
            for chunk in message_content.iter_content():
                content_bytes.write(chunk)

            content_bytes.seek(0)
            file_data = content_bytes.getvalue()

            logger.info(f"Downloaded {len(file_data)} bytes from LINE message {message_id}")
            return file_data

        except Exception as e:
            logger.error(f"Error downloading content from LINE: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Get LINE user profile

        Args:
            user_id: LINE user ID

        Returns:
            User profile dict or None
        """
        try:
            profile = self.bot_api.get_profile(user_id)

            return {
                'user_id': profile.user_id,
                'display_name': profile.display_name,
                'picture_url': profile.picture_url,
                'status_message': getattr(profile, 'status_message', None)
            }

        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    def reply_text(self, reply_token: str, text: str, quick_reply: Optional[QuickReply] = None):
        """
        Send simple text reply

        Args:
            reply_token: Reply token from event
            text: Text message to send
            quick_reply: Optional quick reply buttons
        """
        try:
            message = TextSendMessage(text=text, quick_reply=quick_reply)
            self.bot_api.reply_message(reply_token, message)
            logger.info(f"Sent text reply: {text[:50]}...")

        except Exception as e:
            logger.error(f"Error sending text reply: {e}")

    def reply_flex(self, reply_token: str, alt_text: str, flex_content: Dict):
        """
        Send Flex Message reply

        Args:
            reply_token: Reply token from event
            alt_text: Alternative text for notifications
            flex_content: Flex Message JSON structure
        """
        try:
            message = FlexSendMessage(
                alt_text=alt_text,
                contents=flex_content
            )
            self.bot_api.reply_message(reply_token, message)
            logger.info(f"Sent Flex Message: {alt_text}")

        except Exception as e:
            logger.error(f"Error sending Flex Message: {e}")

    def push_message(self, user_id: str, message):
        """
        Push message to user

        Args:
            user_id: LINE user ID
            message: Message object to send
        """
        try:
            self.bot_api.push_message(user_id, message)
            logger.info(f"Pushed message to user: {user_id}")

        except Exception as e:
            logger.error(f"Error pushing message: {e}")

    def push_text(self, user_id: str, text: str):
        """
        Push text message to user

        Args:
            user_id: LINE user ID
            text: Text to send
        """
        try:
            message = TextSendMessage(text=text)
            self.push_message(user_id, message)

        except Exception as e:
            logger.error(f"Error pushing text: {e}")

    def push_flex(self, user_id: str, alt_text: str, flex_content: Dict):
        """
        Push Flex Message to user

        Args:
            user_id: LINE user ID
            alt_text: Alternative text
            flex_content: Flex Message structure
        """
        try:
            message = FlexSendMessage(alt_text=alt_text, contents=flex_content)
            self.push_message(user_id, message)

        except Exception as e:
            logger.error(f"Error pushing Flex Message: {e}")

    def create_quick_reply(self, actions: List[Dict[str, str]]) -> QuickReply:
        """
        Create Quick Reply buttons

        Args:
            actions: List of actions [{'label': 'Search', 'text': '/search'}, ...]

        Returns:
            QuickReply object
        """
        buttons = []
        for action in actions:
            if action.get('type') == 'postback':
                buttons.append(
                    QuickReplyButton(
                        action=PostbackAction(
                            label=action['label'],
                            data=action['data']
                        )
                    )
                )
            else:
                buttons.append(
                    QuickReplyButton(
                        action=MessageAction(
                            label=action['label'],
                            text=action.get('text', action['label'])
                        )
                    )
                )

        return QuickReply(items=buttons)

    def send_processing_notification(
        self,
        user_id: str,
        file_id: str,
        filename: str,
        status: str,
        message: Optional[str] = None
    ):
        """
        Send file processing status notification

        Args:
            user_id: LINE user ID
            file_id: File UUID
            filename: File name
            status: processing status (pending, completed, failed)
            message: Optional custom message
        """
        try:
            if status == 'completed':
                text = f"✅ ประมวลผลเสร็จแล้ว\n📄 {filename}\n\n{message or 'ไฟล์พร้อมใช้งานแล้ว'}"
            elif status == 'failed':
                text = f"❌ ประมวลผลล้มเหลว\n📄 {filename}\n\n{message or 'กรุณาลองใหม่อีกครั้ง'}"
            else:
                text = f"⏳ กำลังประมวลผล...\n📄 {filename}"

            # Create quick reply actions
            quick_reply = self.create_quick_reply([
                {'label': '🔍 ค้นหา', 'text': '/search'},
                {'label': '📋 รายการไฟล์', 'text': '/list'},
                {'label': 'ℹ️ ช่วยเหลือ', 'text': '/help'}
            ])

            message = TextSendMessage(text=text, quick_reply=quick_reply)
            self.push_message(user_id, message)

        except Exception as e:
            logger.error(f"Error sending processing notification: {e}")

    def get_file_detail_url(self, file_id: str) -> str:
        """Get URL to file detail page (LIFF app)"""
        # TODO: Update with actual LIFF app URL when ready
        return f"{settings.FRONTEND_URL}/files/{file_id}"

    def get_thumbnail_url(self, thumbnail_path: str) -> Optional[str]:
        """
        Get public URL for thumbnail

        Args:
            thumbnail_path: Path to thumbnail in MinIO

        Returns:
            Public URL or None
        """
        # TODO: Generate signed URL from MinIO
        # For now, return placeholder
        return None


# Singleton instance
line_service = LineService()

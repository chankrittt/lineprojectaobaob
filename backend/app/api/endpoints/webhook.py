from fastapi import APIRouter, Request, HTTPException, status, Header
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FileMessage, ImageMessage, VideoMessage, TextMessage
import logging

from app.core.config import settings
from app.core.security import verify_line_signature

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize LINE Bot API
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


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
    logger.info(f"Received file message: {event.message.id}")

    # TODO: Download file from LINE and process
    # For now, just send a reply
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text="ได้รับไฟล์แล้ว กำลังประมวลผล...")
    )


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """Handle image messages from LINE"""
    logger.info(f"Received image message: {event.message.id}")

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text="ได้รับรูปภาพแล้ว กำลังประมวลผล...")
    )


@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    """Handle video messages from LINE"""
    logger.info(f"Received video message: {event.message.id}")

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text="ได้รับวิดีโอแล้ว กำลังประมวลผล...")
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """Handle text messages from LINE"""
    user_message = event.message.text
    logger.info(f"Received text message: {user_message}")

    # Simple command handling
    if user_message.startswith("/search"):
        query = user_message.replace("/search", "").strip()
        # TODO: Implement search
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=f"กำลังค้นหา: {query}")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="สวัสดีค่ะ! ส่งไฟล์มาได้เลย หรือพิมพ์ /search เพื่อค้นหาไฟล์")
        )

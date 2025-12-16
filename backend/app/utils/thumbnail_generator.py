"""
Thumbnail Generator Utility

Handles thumbnail generation for various file types:
- Images (JPG, PNG, GIF, etc.)
- PDFs
- Videos (future implementation)
"""

from PIL import Image
import io
import logging
from typing import Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """Generate thumbnails for different file types"""

    DEFAULT_SIZE = (300, 300)
    THUMBNAIL_FORMAT = "JPEG"
    THUMBNAIL_QUALITY = 85

    @staticmethod
    def generate_image_thumbnail(
        image_data: bytes,
        size: Tuple[int, int] = DEFAULT_SIZE,
        maintain_aspect_ratio: bool = True
    ) -> Optional[bytes]:
        """
        Generate thumbnail for image files

        Args:
            image_data: Raw image bytes
            size: Target thumbnail size (width, height)
            maintain_aspect_ratio: Whether to maintain aspect ratio

        Returns:
            Thumbnail bytes in JPEG format or None if failed
        """
        try:
            # Open image from bytes
            img = Image.open(io.BytesIO(image_data))

            # Convert RGBA to RGB (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize image
            if maintain_aspect_ratio:
                img.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(size, Image.Resampling.LANCZOS)

            # Save to bytes
            output = io.BytesIO()
            img.save(
                output,
                format=ThumbnailGenerator.THUMBNAIL_FORMAT,
                quality=ThumbnailGenerator.THUMBNAIL_QUALITY,
                optimize=True
            )
            output.seek(0)

            thumbnail_bytes = output.getvalue()
            logger.info(f"Generated image thumbnail: {len(thumbnail_bytes)} bytes")
            return thumbnail_bytes

        except Exception as e:
            logger.error(f"Error generating image thumbnail: {e}")
            return None

    @staticmethod
    def generate_pdf_thumbnail(
        pdf_data: bytes,
        page_number: int = 0,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> Optional[bytes]:
        """
        Generate thumbnail for PDF files (first page by default)

        Args:
            pdf_data: Raw PDF bytes
            page_number: Page number to generate thumbnail from (0-indexed)
            size: Target thumbnail size

        Returns:
            Thumbnail bytes in JPEG format or None if failed
        """
        try:
            # Import pdf2image here to avoid dependency errors if not installed
            from pdf2image import convert_from_bytes

            # Convert first page to image
            images = convert_from_bytes(
                pdf_data,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=150  # Balance between quality and speed
            )

            if not images:
                logger.warning("No images generated from PDF")
                return None

            # Get first page image
            img = images[0]

            # Convert PIL Image to bytes and generate thumbnail
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Use image thumbnail generator
            return ThumbnailGenerator.generate_image_thumbnail(
                img_bytes.getvalue(),
                size=size
            )

        except ImportError:
            logger.error("pdf2image not installed. Install with: pip install pdf2image")
            return None
        except Exception as e:
            logger.error(f"Error generating PDF thumbnail: {e}")
            return None

    @staticmethod
    def generate_video_thumbnail(
        video_path: str,
        timestamp: float = 1.0,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> Optional[bytes]:
        """
        Generate thumbnail for video files

        Args:
            video_path: Path to video file
            timestamp: Timestamp in seconds to capture frame
            size: Target thumbnail size

        Returns:
            Thumbnail bytes in JPEG format or None if failed

        Note: Requires ffmpeg to be installed
        TODO: Implement using ffmpeg or opencv-python
        """
        logger.warning("Video thumbnail generation not yet implemented")
        return None

    @staticmethod
    def generate_thumbnail_from_mime_type(
        file_data: bytes,
        mime_type: str,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> Optional[bytes]:
        """
        Generate thumbnail based on MIME type

        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file
            size: Target thumbnail size

        Returns:
            Thumbnail bytes or None if type not supported
        """
        try:
            # Image types
            if mime_type.startswith('image/'):
                return ThumbnailGenerator.generate_image_thumbnail(file_data, size)

            # PDF
            elif mime_type == 'application/pdf':
                return ThumbnailGenerator.generate_pdf_thumbnail(file_data, size=size)

            # Video types (not implemented yet)
            elif mime_type.startswith('video/'):
                logger.info(f"Video thumbnail generation not yet implemented for {mime_type}")
                return None

            # Unsupported type
            else:
                logger.info(f"Thumbnail generation not supported for MIME type: {mime_type}")
                return None

        except Exception as e:
            logger.error(f"Error generating thumbnail for {mime_type}: {e}")
            return None

    @staticmethod
    def get_thumbnail_path(file_path: str, file_id: str) -> str:
        """
        Generate thumbnail storage path in MinIO

        Args:
            file_path: Original file path
            file_id: File UUID

        Returns:
            Thumbnail path (e.g., "thumbnails/uuid.jpg")
        """
        return f"thumbnails/{file_id}.jpg"

    @staticmethod
    def get_image_dimensions(image_data: bytes) -> Optional[Tuple[int, int]]:
        """
        Get original image dimensions

        Args:
            image_data: Raw image bytes

        Returns:
            (width, height) tuple or None if failed
        """
        try:
            img = Image.open(io.BytesIO(image_data))
            return img.size
        except Exception as e:
            logger.error(f"Error getting image dimensions: {e}")
            return None


# Convenience instance
thumbnail_generator = ThumbnailGenerator()

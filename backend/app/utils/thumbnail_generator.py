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
        video_data: bytes,
        timestamp: float = 1.0,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> Optional[bytes]:
        """
        Generate thumbnail for video files using ffmpeg

        Args:
            video_data: Raw video bytes
            timestamp: Timestamp in seconds to capture frame
            size: Target thumbnail size

        Returns:
            Thumbnail bytes in JPEG format or None if failed

        Note: Requires ffmpeg to be installed
        """
        import subprocess
        import tempfile
        import os

        try:
            # Create temporary files for input video and output thumbnail
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_file:
                video_file.write(video_data)
                video_path = video_file.name

            output_path = tempfile.mktemp(suffix='.jpg')

            try:
                # Use ffmpeg to extract frame at specified timestamp
                # -ss: seek to timestamp
                # -i: input file
                # -vframes 1: extract only 1 frame
                # -vf scale: resize to target size while maintaining aspect ratio
                # -q:v 2: high quality JPEG (1-31, lower is better)
                command = [
                    'ffmpeg',
                    '-ss', str(timestamp),
                    '-i', video_path,
                    '-vframes', '1',
                    '-vf', f'scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease',
                    '-q:v', '2',
                    '-y',  # Overwrite output file
                    output_path
                ]

                # Run ffmpeg
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    check=True
                )

                # Read the generated thumbnail
                if os.path.exists(output_path):
                    with open(output_path, 'rb') as thumb_file:
                        thumbnail_bytes = thumb_file.read()

                    logger.info(f"Generated video thumbnail: {len(thumbnail_bytes)} bytes")
                    return thumbnail_bytes
                else:
                    logger.error("ffmpeg did not generate thumbnail file")
                    return None

            finally:
                # Clean up temporary files
                if os.path.exists(video_path):
                    os.remove(video_path)
                if os.path.exists(output_path):
                    os.remove(output_path)

        except subprocess.TimeoutExpired:
            logger.error(f"Video thumbnail generation timed out after 30 seconds")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg error: {e.stderr.decode('utf-8', errors='ignore')}")
            return None
        except FileNotFoundError:
            logger.error("ffmpeg not found. Install with: apt-get install ffmpeg")
            return None
        except Exception as e:
            logger.error(f"Error generating video thumbnail: {e}")
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

            # Video types
            elif mime_type.startswith('video/'):
                return ThumbnailGenerator.generate_video_thumbnail(file_data, size=size)

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

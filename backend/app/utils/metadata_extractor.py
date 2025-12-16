"""
Metadata Extractor Utility

Extracts metadata from various file types:
- Images (EXIF data, dimensions, format)
- PDFs (page count, author, title, creation date)
- Videos (duration, resolution, codec) - future
"""

from PIL import Image
from PIL.ExifTags import TAGS
import io
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import PyPDF2

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract metadata from different file types"""

    @staticmethod
    def extract_image_metadata(image_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from image files

        Args:
            image_data: Raw image bytes

        Returns:
            Dictionary containing image metadata
        """
        metadata = {}

        try:
            img = Image.open(io.BytesIO(image_data))

            # Basic image info
            metadata['format'] = img.format
            metadata['mode'] = img.mode
            metadata['width'], metadata['height'] = img.size
            metadata['dimensions'] = f"{img.size[0]}x{img.size[1]}"

            # Extract EXIF data
            exif_data = img.getexif()
            if exif_data:
                exif = {}
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)

                    # Convert bytes to string
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)

                    # Skip large binary data
                    if isinstance(value, (bytes, bytearray)) and len(value) > 1000:
                        continue

                    exif[tag] = value

                # Extract commonly used EXIF fields
                if 'Make' in exif:
                    metadata['camera_make'] = exif['Make']
                if 'Model' in exif:
                    metadata['camera_model'] = exif['Model']
                if 'DateTime' in exif:
                    metadata['date_taken'] = exif['DateTime']
                if 'Orientation' in exif:
                    metadata['orientation'] = exif['Orientation']
                if 'Flash' in exif:
                    metadata['flash'] = exif['Flash']
                if 'FocalLength' in exif:
                    metadata['focal_length'] = exif['FocalLength']
                if 'ExposureTime' in exif:
                    metadata['exposure_time'] = exif['ExposureTime']
                if 'ISOSpeedRatings' in exif:
                    metadata['iso'] = exif['ISOSpeedRatings']
                if 'GPSInfo' in exif:
                    metadata['has_gps'] = True

                # Store full EXIF data (limit to reasonable fields)
                safe_exif = {k: v for k, v in exif.items() if not isinstance(v, (bytes, bytearray))}
                metadata['exif'] = safe_exif

            logger.info(f"Extracted image metadata: {metadata.get('format')} {metadata.get('dimensions')}")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            return {'error': str(e)}

    @staticmethod
    def extract_pdf_metadata(pdf_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from PDF files

        Args:
            pdf_data: Raw PDF bytes

        Returns:
            Dictionary containing PDF metadata
        """
        metadata = {}

        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))

            # Basic PDF info
            metadata['page_count'] = len(pdf_reader.pages)

            # Get document info
            doc_info = pdf_reader.metadata
            if doc_info:
                # Extract common fields
                if doc_info.title:
                    metadata['title'] = doc_info.title
                if doc_info.author:
                    metadata['author'] = doc_info.author
                if doc_info.subject:
                    metadata['subject'] = doc_info.subject
                if doc_info.creator:
                    metadata['creator'] = doc_info.creator
                if doc_info.producer:
                    metadata['producer'] = doc_info.producer
                if doc_info.creation_date:
                    try:
                        metadata['creation_date'] = str(doc_info.creation_date)
                    except:
                        pass
                if doc_info.modification_date:
                    try:
                        metadata['modification_date'] = str(doc_info.modification_date)
                    except:
                        pass

            # Get first page dimensions (if available)
            if len(pdf_reader.pages) > 0:
                first_page = pdf_reader.pages[0]
                if hasattr(first_page, 'mediabox'):
                    width = float(first_page.mediabox.width)
                    height = float(first_page.mediabox.height)
                    metadata['page_width'] = width
                    metadata['page_height'] = height
                    metadata['page_dimensions'] = f"{width:.1f}x{height:.1f}"

            # Check if PDF is encrypted
            metadata['is_encrypted'] = pdf_reader.is_encrypted

            logger.info(f"Extracted PDF metadata: {metadata.get('page_count')} pages")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {'error': str(e)}

    @staticmethod
    def extract_video_metadata(video_path: str) -> Dict[str, Any]:
        """
        Extract metadata from video files

        Args:
            video_path: Path to video file

        Returns:
            Dictionary containing video metadata

        Note: Requires ffprobe (part of ffmpeg)
        TODO: Implement using ffprobe or opencv-python
        """
        logger.warning("Video metadata extraction not yet implemented")
        return {'error': 'Not implemented'}

    @staticmethod
    def extract_metadata_from_mime_type(
        file_data: bytes,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Extract metadata based on MIME type

        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file

        Returns:
            Dictionary containing file metadata
        """
        try:
            # Image types
            if mime_type.startswith('image/'):
                return MetadataExtractor.extract_image_metadata(file_data)

            # PDF
            elif mime_type == 'application/pdf':
                return MetadataExtractor.extract_pdf_metadata(file_data)

            # Video types (not implemented yet)
            elif mime_type.startswith('video/'):
                logger.info(f"Video metadata extraction not yet implemented for {mime_type}")
                return {}

            # Unsupported type
            else:
                logger.info(f"Metadata extraction not supported for MIME type: {mime_type}")
                return {}

        except Exception as e:
            logger.error(f"Error extracting metadata for {mime_type}: {e}")
            return {'error': str(e)}


# Convenience instance
metadata_extractor = MetadataExtractor()

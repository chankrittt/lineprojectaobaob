import io
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text content from various file types"""

    @staticmethod
    def extract_from_pdf(file_data: bytes) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    @staticmethod
    def extract_from_docx(file_data: bytes) -> str:
        """Extract text from DOCX"""
        try:
            from docx import Document
            doc_file = io.BytesIO(file_data)
            doc = Document(doc_file)

            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text_parts.append(paragraph.text)

            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""

    @staticmethod
    def extract_from_txt(file_data: bytes) -> str:
        """Extract text from plain text file"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return file_data.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return file_data.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            return ""

    @staticmethod
    def extract_from_image(file_data: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(io.BytesIO(file_data))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""

    @staticmethod
    def extract_text(file_data: bytes, mime_type: str, filename: str) -> str:
        """
        Extract text from file based on mime type
        Returns extracted text or empty string if extraction fails
        """
        try:
            if mime_type == 'application/pdf':
                return TextExtractor.extract_from_pdf(file_data)

            elif mime_type in [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword'
            ]:
                return TextExtractor.extract_from_docx(file_data)

            elif mime_type.startswith('text/'):
                return TextExtractor.extract_from_txt(file_data)

            elif mime_type.startswith('image/'):
                return TextExtractor.extract_from_image(file_data)

            else:
                logger.warning(f"Unsupported mime type for text extraction: {mime_type}")
                return ""

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    @staticmethod
    def get_text_preview(text: str, max_length: int = 500) -> str:
        """Get preview of text content"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

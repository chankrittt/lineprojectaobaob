import os
import mimetypes
from typing import Tuple, Optional
import magic
from pathlib import Path


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def get_mime_type(filename: str, file_data: bytes = None) -> str:
    """Get MIME type from filename or file content"""
    # Try from content first (more accurate)
    if file_data:
        try:
            mime = magic.Magic(mime=True)
            return mime.from_buffer(file_data)
        except:
            pass

    # Fallback to filename
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def is_allowed_file(filename: str, allowed_extensions: str) -> bool:
    """Check if file extension is allowed"""
    ext = get_file_extension(filename).lstrip('.')
    allowed = [e.strip().lower() for e in allowed_extensions.split(',')]
    return ext.lower() in allowed


def generate_unique_filename(original_filename: str, user_id: str, file_hash: str) -> str:
    """Generate unique filename for storage"""
    ext = get_file_extension(original_filename)
    # Use hash for uniqueness
    return f"{user_id}/{file_hash[:8]}/{file_hash}{ext}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove dangerous characters"""
    # Remove path separators
    filename = os.path.basename(filename)
    # Replace spaces and special chars
    filename = filename.replace(" ", "_")
    # Keep only alphanumeric, dots, underscores, hyphens
    safe_chars = []
    for char in filename:
        if char.isalnum() or char in '._-':
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    return ''.join(safe_chars)


def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_file_category(mime_type: str) -> str:
    """Get file category from MIME type"""
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf']:
        return 'document'
    elif mime_type in [
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ]:
        return 'document'
    elif mime_type.startswith('text/'):
        return 'text'
    elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']:
        return 'archive'
    else:
        return 'other'

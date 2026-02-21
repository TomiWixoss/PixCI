"""File handling service"""
import os
import uuid
from pathlib import Path
from typing import BinaryIO
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidFileException
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileService:
    """Service for file operations"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.temp_dir = Path(settings.TEMP_DIR)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories"""
        self.upload_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"Directories initialized: {self.upload_dir}, {self.temp_dir}")
    
    def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise InvalidFileException("No filename provided")
        
        # Check extension
        ext = file.filename.split('.')[-1].lower()
        if ext not in settings.allowed_extensions_list:
            raise InvalidFileException(
                f"Invalid file extension. Allowed: {', '.join(settings.allowed_extensions_list)}"
            )
        
        logger.info(f"File validated: {file.filename}")
    
    async def save_upload(self, file: UploadFile) -> Path:
        """Save uploaded file to disk"""
        self.validate_file(file)
        
        # Generate unique filename
        ext = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        content = await file.read()
        
        # Check file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise InvalidFileException(
                f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        return file_path
    
    def create_temp_file(self, content: str, extension: str = "xml") -> Path:
        """Create temporary file with content"""
        unique_filename = f"{uuid.uuid4()}.{extension}"
        file_path = self.temp_dir / unique_filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Temp file created: {file_path}")
        return file_path
    
    def cleanup_file(self, file_path: Path) -> None:
        """Delete file if exists"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {e}")
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """Clean up old temporary files"""
        import time
        current_time = time.time()
        
        for directory in [self.upload_dir, self.temp_dir]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_hours * 3600:
                        self.cleanup_file(file_path)


file_service = FileService()

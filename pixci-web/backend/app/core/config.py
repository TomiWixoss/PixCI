"""Application configuration management"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    RELOAD: bool = Field(default=True, description="Auto-reload on code changes")
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Allowed CORS origins (comma-separated)"
    )
    
    # Upload Configuration
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Max upload size in bytes (10MB)")
    ALLOWED_EXTENSIONS: str = Field(default="png,jpg,jpeg,gif", description="Allowed file extensions")
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")
    TEMP_DIR: str = Field(default="temp", description="Temporary files directory")
    
    # Processing Configuration
    MAX_IMAGE_DIMENSION: int = Field(default=512, description="Maximum image dimension")
    DEFAULT_BLOCK_SIZE: int = Field(default=1, description="Default block size for encoding")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions into list"""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

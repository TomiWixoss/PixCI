"""Pydantic models for request/response validation"""
from typing import Optional
from pydantic import BaseModel, Field, validator


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(description="Application version")


class EncodeRequest(BaseModel):
    """Request model for encoding image to PXVG"""
    block_size: int = Field(default=1, ge=1, le=16, description="Block size for pixel grouping")
    auto_detect: bool = Field(default=False, description="Auto-detect optimal block size")
    
    class Config:
        json_schema_extra = {
            "example": {
                "block_size": 1,
                "auto_detect": False
            }
        }


class EncodeResponse(BaseModel):
    """Response model for encoding"""
    pxvg_code: str = Field(description="Generated PXVG XML code")
    grid_width: int = Field(description="Grid width in blocks")
    grid_height: int = Field(description="Grid height in blocks")
    num_colors: int = Field(description="Number of unique colors")
    block_size: int = Field(description="Block size used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pxvg_code": "<pxvg w=\"32\" h=\"32\">...</pxvg>",
                "grid_width": 32,
                "grid_height": 32,
                "num_colors": 8,
                "block_size": 1
            }
        }


class DecodeRequest(BaseModel):
    """Request model for decoding PXVG to image"""
    pxvg_code: str = Field(description="PXVG XML code to decode")
    scale: int = Field(default=1, ge=1, le=20, description="Output image scale factor")
    
    @validator('pxvg_code')
    def validate_pxvg(cls, v):
        """Validate PXVG code format"""
        if not v.strip():
            raise ValueError("PXVG code cannot be empty")
        if '<pxvg' not in v.lower():
            raise ValueError("Invalid PXVG format: missing <pxvg> tag")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "pxvg_code": "<pxvg w=\"32\" h=\"32\">...</pxvg>",
                "scale": 10
            }
        }


class DecodeResponse(BaseModel):
    """Response model for decoding"""
    image_base64: str = Field(description="Base64 encoded PNG image")
    width: int = Field(description="Original grid width")
    height: int = Field(description="Original grid height")
    scaled_width: int = Field(description="Scaled output width")
    scaled_height: int = Field(description="Scaled output height")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
                "width": 32,
                "height": 32,
                "scaled_width": 320,
                "scaled_height": 320
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid file format",
                "error_code": "INVALID_FILE"
            }
        }

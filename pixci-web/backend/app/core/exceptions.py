"""Custom exception classes"""
from fastapi import HTTPException, status


class PixCIException(HTTPException):
    """Base exception for PixCI application"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InvalidFileException(PixCIException):
    """Raised when uploaded file is invalid"""
    def __init__(self, detail: str = "Invalid file format or size"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class ProcessingException(PixCIException):
    """Raised when image processing fails"""
    def __init__(self, detail: str = "Failed to process image"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EncodingException(PixCIException):
    """Raised when encoding fails"""
    def __init__(self, detail: str = "Failed to encode image to PXVG"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DecodingException(PixCIException):
    """Raised when decoding fails"""
    def __init__(self, detail: str = "Failed to decode PXVG to image"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

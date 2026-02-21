"""Decode endpoints - PXVG to Image"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import DecodeRequest, DecodeResponse, ErrorResponse
from app.services.file_service import file_service
from app.services.pixci_service import pixci_service
from app.core.logging import get_logger
from app.core.exceptions import PixCIException

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "",
    response_model=DecodeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    }
)
async def decode_pxvg(request: DecodeRequest):
    """
    Decode PXVG code to image
    
    Convert PXVG XML code back to a PNG image.
    
    - **pxvg_code**: PXVG XML code string
    - **scale**: Output image scale factor (1-20)
    
    Returns base64 encoded PNG image and metadata.
    """
    pxvg_path = None
    output_path = None
    
    try:
        # Save PXVG code to temporary file
        pxvg_path = file_service.create_temp_file(request.pxvg_code, "pxvg.xml")
        
        # Create output path for PNG
        output_path = file_service.temp_dir / f"{pxvg_path.stem}.png"
        
        # Decode PXVG to image
        width, height = pixci_service.decode_from_pxvg(
            pxvg_path=pxvg_path,
            output_path=output_path,
            scale=request.scale
        )
        
        # Convert image to base64
        image_base64 = pixci_service.image_to_base64(output_path)
        
        logger.info(f"Successfully decoded PXVG to {width}x{height} image")
        
        return DecodeResponse(
            image_base64=image_base64,
            width=width,
            height=height,
            scaled_width=width * request.scale,
            scaled_height=height * request.scale
        )
        
    except PixCIException as e:
        logger.error(f"PixCI error during decoding: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during decoding: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Cleanup temporary files
        if pxvg_path:
            file_service.cleanup_file(pxvg_path)
        if output_path:
            file_service.cleanup_file(output_path)

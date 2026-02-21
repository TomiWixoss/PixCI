"""Encode endpoints - Image to PXVG"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import EncodeResponse, ErrorResponse
from app.services.file_service import file_service
from app.services.pixci_service import pixci_service
from app.core.logging import get_logger
from app.core.exceptions import PixCIException

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "",
    response_model=EncodeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    }
)
async def encode_image(
    file: UploadFile = File(..., description="Image file to encode (PNG, JPG, GIF)"),
    block_size: int = Form(default=1, ge=1, le=16, description="Block size for pixel grouping"),
    auto_detect: bool = Form(default=False, description="Auto-detect optimal block size")
):
    """
    Encode an image to PXVG format
    
    Upload an image file and convert it to PXVG XML code.
    
    - **file**: Image file (PNG, JPG, GIF)
    - **block_size**: Size of pixel blocks (1-16)
    - **auto_detect**: Automatically detect optimal block size
    
    Returns PXVG XML code and metadata.
    """
    image_path = None
    output_path = None
    
    try:
        # Save uploaded file
        image_path = await file_service.save_upload(file)
        
        # Create output path for PXVG
        output_path = file_service.temp_dir / f"{image_path.stem}.pxvg.xml"
        
        # Encode to PXVG
        grid_w, grid_h, num_colors, final_block_size = pixci_service.encode_to_pxvg(
            image_path=image_path,
            output_path=output_path,
            block_size=block_size,
            auto_detect=auto_detect
        )
        
        # Read generated PXVG code
        with open(output_path, "r", encoding="utf-8") as f:
            pxvg_code = f.read()
        
        logger.info(f"Successfully encoded {file.filename}")
        
        return EncodeResponse(
            pxvg_code=pxvg_code,
            grid_width=grid_w,
            grid_height=grid_h,
            num_colors=num_colors,
            block_size=final_block_size
        )
        
    except PixCIException as e:
        logger.error(f"PixCI error during encoding: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during encoding: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Cleanup temporary files
        if image_path:
            file_service.cleanup_file(image_path)
        if output_path:
            file_service.cleanup_file(output_path)

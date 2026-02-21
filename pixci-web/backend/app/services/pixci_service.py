"""PixCI encoding/decoding service"""
import sys
import base64
from pathlib import Path
from typing import Tuple
from PIL import Image

from app.core.config import settings
from app.core.exceptions import EncodingException, DecodingException, ProcessingException
from app.core.logging import get_logger

logger = get_logger(__name__)

# Add parent directory to path to import pixci
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

try:
    from pixci.core.pxvg_engine import encode_pxvg, decode_pxvg
    from pixci.core.smart_encoder import smart_encode_pxvg
except ImportError as e:
    logger.error(f"Failed to import pixci modules: {e}")
    raise


class PixCIService:
    """Service for PixCI operations"""
    
    def validate_image(self, image_path: Path) -> None:
        """Validate image dimensions and format"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                if width > settings.MAX_IMAGE_DIMENSION or height > settings.MAX_IMAGE_DIMENSION:
                    raise ProcessingException(
                        f"Image too large. Max dimension: {settings.MAX_IMAGE_DIMENSION}px"
                    )
                
                if img.mode not in ['RGB', 'RGBA', 'P', 'L']:
                    raise ProcessingException(f"Unsupported image mode: {img.mode}")
                
                logger.info(f"Image validated: {width}x{height}, mode={img.mode}")
        except Exception as e:
            if isinstance(e, ProcessingException):
                raise
            raise ProcessingException(f"Failed to validate image: {str(e)}")
    
    def encode_to_pxvg(
        self, 
        image_path: Path, 
        output_path: Path,
        block_size: int = 1,
        auto_detect: bool = False
    ) -> Tuple[int, int, int, int]:
        """
        Encode image to PXVG format
        
        Returns:
            Tuple of (grid_width, grid_height, num_colors, final_block_size)
        """
        try:
            self.validate_image(image_path)
            
            logger.info(f"Encoding image: {image_path}, block_size={block_size}, auto={auto_detect}")
            
            # Use smart encoder for better optimization
            result = smart_encode_pxvg(
                image_path=image_path,
                output_path=output_path,
                block_size=block_size,
                auto_detect=auto_detect
            )
            
            logger.info(f"Encoding successful: grid={result[0]}x{result[1]}, colors={result[2]}")
            return result
            
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise EncodingException(f"Failed to encode image: {str(e)}")
    
    def decode_from_pxvg(
        self,
        pxvg_path: Path,
        output_path: Path,
        scale: int = 1
    ) -> Tuple[int, int]:
        """
        Decode PXVG to image
        
        Returns:
            Tuple of (width, height)
        """
        try:
            logger.info(f"Decoding PXVG: {pxvg_path}, scale={scale}")
            
            result = decode_pxvg(
                text_path=pxvg_path,
                output_path=output_path,
                scale=scale
            )
            
            logger.info(f"Decoding successful: {result[0]}x{result[1]}")
            return result
            
        except Exception as e:
            logger.error(f"Decoding failed: {e}")
            raise DecodingException(f"Failed to decode PXVG: {str(e)}")
    
    def image_to_base64(self, image_path: Path) -> str:
        """Convert image to base64 string"""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {e}")
            raise ProcessingException(f"Failed to process image: {str(e)}")


pixci_service = PixCIService()

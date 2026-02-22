"""
decoder.py - Decode PXVG back to geo.json and texture atlas
Allows AI to edit PXVG files, then rebuild the 3D model.
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image
import re


def decode_pxvg_to_geo(
    pxvg_dir: Path,
    original_geo_path: Path,
    output_geo_path: Path,
    output_texture_path: Path,
    mode: str = 'by_face'
) -> Tuple[Path, Path]:
    """Reconstruct geo.json and texture atlas from modified PXVG files.
    
    Args:
        pxvg_dir: Directory containing modified PXVG files
        original_geo_path: Original geo.json (for structure reference)
        output_geo_path: Where to save reconstructed geo.json
        output_texture_path: Where to save reconstructed texture atlas
        mode: Decoding mode (must match encoding mode)
            - 'by_face': Reconstruct from individual face PXVGs
            - 'by_cube': Reconstruct from cube PXVGs
            - 'by_bone': Reconstruct from bone PXVGs
            
    Returns:
        Tuple of (geo_path, texture_path)
    """
    from ..pxvg_engine import decode_pxvg
    
    pxvg_dir = Path(pxvg_dir)
    
    # Load original geo.json for structure
    with open(original_geo_path, 'r', encoding='utf-8') as f:
        geo_data = json.load(f)
        
    geometry = geo_data['minecraft:geometry'][0]
    desc = geometry['description']
    texture_width = desc.get('texture_width', 64)
    texture_height = desc.get('texture_height', 64)
    
    # Create blank texture atlas
    atlas = Image.new('RGBA', (texture_width, texture_height), (0, 0, 0, 0))
    
    if mode == 'by_face':
        # Reconstruct from individual face PXVGs
        pxvg_files = list(pxvg_dir.glob('*.pxvg'))
        
        for pxvg_path in pxvg_files:
            # Extract metadata from PXVG comments
            metadata = _extract_pxvg_metadata(pxvg_path)
            
            if not metadata:
                continue
                
            # Decode PXVG to PNG
            with NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = Path(tmp.name)
                
            try:
                decode_pxvg(pxvg_path, tmp_path, scale=1)
                face_img = Image.open(tmp_path).convert('RGBA')
                
                # Get UV coordinates from metadata
                uv_data = metadata.get('uv', {})
                if 'uv' in uv_data:
                    uv = uv_data['uv']
                    uv_size = uv_data['uv_size']
                    
                    # Paste face image back into atlas
                    x = int(uv[0])
                    y = int(uv[1])
                    
                    # Handle negative UV sizes
                    if uv_size[0] < 0:
                        face_img = face_img.transpose(Image.FLIP_LEFT_RIGHT)
                    if uv_size[1] < 0:
                        face_img = face_img.transpose(Image.FLIP_TOP_BOTTOM)
                        
                    atlas.paste(face_img, (x, y), face_img)
                    
            finally:
                tmp_path.unlink(missing_ok=True)
                
    # Save reconstructed texture atlas
    atlas.save(output_texture_path)
    
    # Save geo.json (unchanged structure, only texture modified)
    with open(output_geo_path, 'w', encoding='utf-8') as f:
        json.dump(geo_data, f, indent='\t')
        
    return (output_geo_path, output_texture_path)


def rebuild_texture_atlas(
    face_images: Dict[str, Image.Image],
    uv_mappings: Dict[str, Dict],
    texture_width: int = 64,
    texture_height: int = 64
) -> Image.Image:
    """Rebuild texture atlas from individual face images.
    
    Args:
        face_images: Dict mapping face IDs to PIL Images
        uv_mappings: Dict mapping face IDs to UV data (uv, uv_size)
        texture_width: Atlas width
        texture_height: Atlas height
        
    Returns:
        PIL Image of reconstructed atlas
    """
    atlas = Image.new('RGBA', (texture_width, texture_height), (0, 0, 0, 0))
    
    for face_id, face_img in face_images.items():
        if face_id not in uv_mappings:
            continue
            
        uv_data = uv_mappings[face_id]
        uv = uv_data.get('uv', [0, 0])
        uv_size = uv_data.get('uv_size', [1, 1])
        
        x = int(uv[0])
        y = int(uv[1])
        
        # Handle flipped textures
        img = face_img.copy()
        if uv_size[0] < 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if uv_size[1] < 0:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
        # Resize if needed
        target_w = int(abs(uv_size[0]))
        target_h = int(abs(uv_size[1]))
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.NEAREST)
            
        atlas.paste(img, (x, y), img)
        
    return atlas


def _extract_pxvg_metadata(pxvg_path: Path) -> Dict:
    """Extract metadata from PXVG XML comments.
    
    Returns:
        Dict with metadata fields (model, bone, cube_index, face, uv)
    """
    metadata = {}
    
    with open(pxvg_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract metadata from comments
    comment_pattern = r'<!-- (\w+): (.+?) -->'
    matches = re.findall(comment_pattern, content)
    
    for key, value in matches:
        if key == 'uv':
            # Parse UV data (stored as string representation of dict)
            try:
                metadata[key] = eval(value)
            except:
                pass
        elif key in ['cube_index']:
            metadata[key] = int(value)
        else:
            metadata[key] = value
            
    return metadata


from tempfile import NamedTemporaryFile

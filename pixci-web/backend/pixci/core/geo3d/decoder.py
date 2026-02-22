"""
decoder.py - Gộp các file PXVG đã chỉnh thành texture PNG gốc
Chỉ xử lý texture, KHÔNG tạo hay chỉnh geo.json
"""
import json
import re
from pathlib import Path
from typing import Dict
from PIL import Image


def decode_pxvg_to_texture(
    pxvg_dir: Path,
    geo_path: Path,
    output_texture_path: Path
) -> Path:
    """Gộp các file PXVG đã chỉnh thành texture PNG gốc.
    
    Args:
        pxvg_dir: Thư mục chứa các file PXVG đã chỉnh
        geo_path: File geo.json gốc (để lấy texture size)
        output_texture_path: Đường dẫn output cho texture PNG
        
    Returns:
        Path của texture PNG đã tạo
    """
    from ..pxvg_engine import decode_pxvg
    from tempfile import NamedTemporaryFile
    
    pxvg_dir = Path(pxvg_dir)
    
    # Load geo.json để lấy texture size
    with open(geo_path, 'r', encoding='utf-8') as f:
        geo_data = json.load(f)
    
    # Get texture dimensions
    if 'minecraft:geometry' in geo_data:
        # Format mới
        desc = geo_data['minecraft:geometry'][0]['description']
        texture_width = desc.get('texture_width', 64)
        texture_height = desc.get('texture_height', 64)
    else:
        # Format cũ
        geo_key = [k for k in geo_data.keys() if k.startswith('geometry.')][0]
        geometry = geo_data[geo_key]
        texture_width = geometry.get('texturewidth', 64)
        texture_height = geometry.get('textureheight', 64)
    
    # Create blank texture atlas
    atlas = Image.new('RGBA', (texture_width, texture_height), (0, 0, 0, 0))
    
    # Check if global bbox PNG exists (for 100% lossless)
    model_name = pxvg_dir.name.split('_')[0] if '_' in pxvg_dir.name else 'model'
    
    # Try to find model name from first PXVG file
    pxvg_files = list(pxvg_dir.glob('*.pxvg'))
    if pxvg_files:
        first_file = pxvg_files[0].stem
        model_name = first_file.rsplit('_', 1)[0] if '_' in first_file else first_file
        # Remove bone name
        parts = model_name.split('_')
        if len(parts) > 1:
            model_name = parts[0]
    
    full_png_path = pxvg_dir / f"{model_name}_full.png"
    metadata_path = pxvg_dir / f"{model_name}_metadata.txt"
    
    if full_png_path.exists() and metadata_path.exists():
        # Use global bbox for 100% lossless reconstruction
        with open(metadata_path) as f:
            metadata_line = f.read().strip()
            if metadata_line.startswith('global_bbox:'):
                bbox_str = metadata_line.replace('global_bbox:', '')
                bbox_x, bbox_y, bbox_w, bbox_h = map(int, bbox_str.split(','))
                
                # Load and paste global bbox
                global_bbox_img = Image.open(full_png_path).convert('RGBA')
                atlas.paste(global_bbox_img, (bbox_x, bbox_y))
                
                # Save and return (100% lossless!)
                atlas.save(output_texture_path)
                return output_texture_path
    
    # Fallback: process individual bones
    # Process all PXVG files
    pxvg_files = list(pxvg_dir.glob('*.pxvg'))
    
    for pxvg_path in pxvg_files:
        # Extract metadata
        metadata = _extract_metadata_from_pxvg(pxvg_path)
        
        if not metadata:
            continue
        
        # Check if original PNG exists (for lossless reconstruction)
        png_path = pxvg_path.with_suffix('.png')
        
        if png_path.exists() and 'bbox' in metadata:
            # Use original bbox PNG (100% lossless)
            bbox_img = Image.open(png_path).convert('RGBA')
            bbox_x, bbox_y, bbox_w, bbox_h = map(int, metadata['bbox'].split(','))
            
            # Paste entire bbox back to atlas
            atlas.paste(bbox_img, (bbox_x, bbox_y))
        else:
            # Fallback: decode PXVG and split
            uv_keys = metadata.get('uv', '')
            if not uv_keys:
                continue
            
            with NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = Path(tmp.name)
            
            try:
                decode_pxvg(pxvg_path, tmp_path, scale=1)
                combined_img = Image.open(tmp_path).convert('RGBA')
                
                uv_list = uv_keys.split('|')
                
                if len(uv_list) == 1:
                    x, y, w, h = map(int, uv_list[0].split(','))
                    atlas.paste(combined_img, (x, y))
                else:
                    x_offset = 0
                    for uv_key in uv_list:
                        x, y, w, h = map(int, uv_key.split(','))
                        face_img = combined_img.crop((x_offset, 0, x_offset + w, combined_img.height))
                        if face_img.height != h:
                            face_img = face_img.crop((0, 0, w, h))
                        atlas.paste(face_img, (x, y))
                        x_offset += w
            finally:
                tmp_path.unlink(missing_ok=True)
    
    # Save texture
    atlas.save(output_texture_path)
    
    return output_texture_path


def _extract_metadata_from_pxvg(pxvg_path: Path) -> dict:
    """Trích xuất metadata từ PXVG."""
    with open(pxvg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = {}
    
    # Find UV comment (format: bbox:x,y,w,h|uv:...)
    match = re.search(r'<!-- UV: (.+?) -->', content)
    
    if match:
        data = match.group(1)
        
        # Parse bbox and uv
        if 'bbox:' in data:
            parts = data.split('|uv:')
            if len(parts) == 2:
                bbox_part = parts[0].replace('bbox:', '')
                uv_part = parts[1]
                metadata['bbox'] = bbox_part
                metadata['uv'] = uv_part
        else:
            # Old format (just UV keys)
            metadata['uv'] = data
    
    return metadata

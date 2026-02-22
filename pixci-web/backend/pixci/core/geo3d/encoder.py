"""
encoder.py - Tách texture atlas thành nhiều file PXVG dựa vào geo.json
Chỉ xử lý texture, KHÔNG tạo hay chỉnh geo.json
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image


def encode_texture_to_pxvg(
    geo_path: Path,
    texture_path: Path,
    output_dir: Path,
    by_face: bool = False
) -> List[Path]:
    """Tách texture atlas thành nhiều file PXVG dựa vào UV mapping.
    
    Args:
        geo_path: Đường dẫn file geo.json (để lấy UV mapping)
        texture_path: Đường dẫn texture PNG gốc
        output_dir: Thư mục output cho các file PXVG
        by_face: True = mỗi face 1 file, False = mỗi bone 1 file (mặc định)
        
    Returns:
        List các file PXVG đã tạo
    """
    from ..pxvg_engine import encode_pxvg
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load geo.json
    with open(geo_path, 'r', encoding='utf-8') as f:
        geo_data = json.load(f)
    
    # Load texture
    texture = Image.open(texture_path).convert('RGBA')
    
    # Parse geometry (hỗ trợ cả format cũ và mới)
    if 'minecraft:geometry' in geo_data:
        # Format mới (1.12.0+)
        geometry = geo_data['minecraft:geometry'][0]
        bones = geometry['bones']
        model_name = geometry['description']['identifier'].split(':')[-1]
    else:
        # Format cũ (1.8.0)
        geo_key = [k for k in geo_data.keys() if k.startswith('geometry.')][0]
        geometry = geo_data[geo_key]
        bones = geometry['bones']
        model_name = geo_key.replace('geometry.', '')
    
    pxvg_files = []
    seen_uvs = set()  # Track để skip duplicate faces
    all_bone_uvs = []  # Track all UVs from all bones for global bbox
    
    for bone in bones:
        bone_name = bone['name']
        cubes = bone.get('cubes', [])
        
        if not cubes:
            continue
        
        if by_face:
            # Mỗi face 1 file PXVG
            for cube_idx, cube in enumerate(cubes):
                faces = _extract_cube_faces(cube, texture)
                
                for face_name, (face_img, uv_key) in faces.items():
                    # Skip duplicate faces (từ mirror bones)
                    if uv_key in seen_uvs:
                        continue
                    
                    # Skip transparent faces
                    if _is_fully_transparent(face_img):
                        continue
                    
                    seen_uvs.add(uv_key)
                    
                    # Save face as PXVG
                    filename = f"{model_name}_{bone_name}_c{cube_idx}_{face_name}.pxvg"
                    pxvg_path = output_dir / filename
                    
                    # Save temp PNG
                    temp_png = output_dir / f"temp_{filename}.png"
                    face_img.save(temp_png)
                    
                    # Encode to PXVG
                    encode_pxvg(temp_png, pxvg_path)
                    temp_png.unlink()
                    
                    # Add metadata comment
                    _add_metadata_to_pxvg(pxvg_path, model_name, bone_name, cube_idx, face_name, uv_key)
                    
                    pxvg_files.append(pxvg_path)
        else:
            # Mỗi bone 1 file PXVG (gộp tất cả faces của bone)
            bone_faces = []
            bone_uvs = []  # Track all UVs (including skipped ones)
            
            for cube_idx, cube in enumerate(cubes):
                faces = _extract_cube_faces(cube, texture)
                
                for face_name, (face_img, uv_key) in faces.items():
                    # Track all UVs for global bbox
                    all_bone_uvs.append(uv_key)
                    bone_uvs.append(uv_key)
                    
                    if uv_key in seen_uvs or _is_fully_transparent(face_img):
                        continue
                    
                    seen_uvs.add(uv_key)
                    bone_faces.append((face_img, uv_key))
            
            if not bone_faces:
                continue
            
            # Calculate bounding box of all UVs (including skipped)
            all_coords = []
            for uv_key in bone_uvs:
                x, y, w, h = map(int, uv_key.split(','))
                all_coords.extend([(x, y), (x + w, y + h)])
            
            if not all_coords:
                continue
            
            xs = [c[0] for c in all_coords]
            ys = [c[1] for c in all_coords]
            bbox_x = min(xs)
            bbox_y = min(ys)
            bbox_w = max(xs) - bbox_x
            bbox_h = max(ys) - bbox_y
            
            # Crop bounding box from original texture (100% lossless)
            bbox_img = texture.crop((bbox_x, bbox_y, bbox_x + bbox_w, bbox_y + bbox_h))
            
            # Gộp tất cả faces thành 1 ảnh lớn (for PXVG)
            combined_img = _combine_faces(bone_faces)
            
            # Collect all UV keys for metadata
            uv_keys = [uv_key for _, uv_key in bone_faces]
            
            # Save as PXVG
            filename = f"{model_name}_{bone_name}.pxvg"
            pxvg_path = output_dir / filename
            
            # Save bounding box PNG (for 100% lossless reconstruction)
            png_path = output_dir / f"{model_name}_{bone_name}.png"
            bbox_img.save(png_path)
            
            temp_png = output_dir / f"temp_{filename}.png"
            combined_img.save(temp_png)
            
            encode_pxvg(temp_png, pxvg_path)
            temp_png.unlink()
            
            # Add metadata with bbox and UV keys
            metadata_str = f"bbox:{bbox_x},{bbox_y},{bbox_w},{bbox_h}|uv:{"|".join(uv_keys)}"
            _add_metadata_to_pxvg(pxvg_path, model_name, bone_name, len(cubes), "combined", metadata_str)
            
            pxvg_files.append(pxvg_path)
    
    # Save global bbox PNG (covers ALL bones including mirrors) for 100% lossless
    if all_bone_uvs:
        all_coords = []
        for uv_key in all_bone_uvs:
            x, y, w, h = map(int, uv_key.split(','))
            all_coords.extend([(x, y), (x + w, y + h)])
        
        xs = [c[0] for c in all_coords]
        ys = [c[1] for c in all_coords]
        global_bbox_x = min(xs)
        global_bbox_y = min(ys)
        global_bbox_w = max(xs) - global_bbox_x
        global_bbox_h = max(ys) - global_bbox_y
        
        # Crop global bbox from original texture
        global_bbox_img = texture.crop((global_bbox_x, global_bbox_y, 
                                       global_bbox_x + global_bbox_w, 
                                       global_bbox_y + global_bbox_h))
        
        # Save as _full.png
        full_png_path = output_dir / f"{model_name}_full.png"
        global_bbox_img.save(full_png_path)
        
        # Save metadata
        metadata_path = output_dir / f"{model_name}_metadata.txt"
        with open(metadata_path, 'w') as f:
            f.write(f"global_bbox:{global_bbox_x},{global_bbox_y},{global_bbox_w},{global_bbox_h}\n")
    
    return pxvg_files


def _extract_cube_faces(cube: Dict, texture: Image.Image) -> Dict[str, Tuple[Image.Image, str]]:
    """Trích xuất 6 faces của cube từ texture atlas.
    
    Returns:
        Dict mapping face_name -> (face_image, uv_key)
    """
    faces = {}
    
    # Get cube dimensions
    size = cube.get('size', [1, 1, 1])
    w, h, d = size
    
    # Get UV coordinates
    if 'uv' in cube:
        # Format mới: {"uv": [x, y]}
        if isinstance(cube['uv'], dict):
            uv = cube['uv'].get('uv', [0, 0])
        else:
            uv = cube['uv']
    else:
        uv = [0, 0]
    
    u, v = uv
    
    # UV layout cho box model:
    # +---+---+---+---+
    # | R | F | L | B |  <- Top row (height = d)
    # +---+---+---+---+
    # | T | F | B |   |  <- Bottom row (height = h)
    # +---+---+---+---+
    #   d   w   d   w
    
    face_uvs = {
        'right': (u, v + d, d, h),           # Right face
        'front': (u + d, v + d, w, h),       # Front face
        'left': (u + d + w, v + d, d, h),    # Left face
        'back': (u + d + w + d, v + d, w, h), # Back face
        'top': (u + d, v, w, d),             # Top face
        'bottom': (u + d + w, v, w, d),      # Bottom face
    }
    
    for face_name, (fx, fy, fw, fh) in face_uvs.items():
        # Crop face from texture
        face_img = texture.crop((fx, fy, fx + fw, fy + fh))
        
        # Create unique key for this UV region
        uv_key = f"{fx},{fy},{fw},{fh}"
        
        faces[face_name] = (face_img, uv_key)
    
    return faces


def _is_fully_transparent(img: Image.Image) -> bool:
    """Check nếu ảnh hoàn toàn trong suốt."""
    if img.mode != 'RGBA':
        return False
    
    alpha = img.split()[3]
    return alpha.getextrema()[1] == 0


def _combine_faces(faces: List[Tuple[Image.Image, str]]) -> Image.Image:
    """Gộp nhiều faces thành 1 ảnh lớn (xếp theo hàng ngang)."""
    if not faces:
        return Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    
    # Calculate total width and max height
    total_width = sum(img.width for img, _ in faces)
    max_height = max(img.height for img, _ in faces)
    
    # Create combined image
    combined = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))
    
    x_offset = 0
    for img, _ in faces:
        # Paste without mask to preserve all pixels including transparent ones
        combined.paste(img, (x_offset, 0))
        x_offset += img.width
    
    return combined


def _add_metadata_to_pxvg(pxvg_path: Path, model: str, bone: str, cube_count: int, face: str, uv_key: str):
    """Thêm metadata vào PXVG file (dưới dạng XML comments)."""
    with open(pxvg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert metadata after XML declaration
    lines = content.split('\n')
    metadata_lines = [
        f'<!-- Model: {model} -->',
        f'<!-- Bone: {bone} -->',
        f'<!-- Cubes: {cube_count} -->',
        f'<!-- Face: {face} -->',
    ]
    
    if uv_key:
        metadata_lines.append(f'<!-- UV: {uv_key} -->')
    
    # Insert after first line (XML declaration)
    lines = [lines[0]] + metadata_lines + lines[1:]
    
    with open(pxvg_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

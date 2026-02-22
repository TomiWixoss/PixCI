"""
encoder.py - Encode geo.json models to PXVG format
Converts 3D model faces to AI-editable 2D pixel art.
"""
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image
from tempfile import NamedTemporaryFile

from .parser import GeoModel


def encode_geo_to_pxvg(
    geo_path: Path,
    texture_path: Path,
    output_dir: Path,
    mode: str = 'by_bone'
) -> Dict[str, Path]:
    """Encode a geo.json model to PXVG format(s).
    
    Args:
        geo_path: Path to geo.json file
        texture_path: Path to texture atlas PNG
        output_dir: Directory to save PXVG files
        mode: Encoding mode:
            - 'by_bone': One PXVG per bone (RECOMMENDED - balanced)
            - 'by_face': One PXVG per cube face (most granular, many files)
        
    Returns:
        Dictionary mapping identifiers to output PXVG paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model = GeoModel(geo_path, texture_path)
    cubes = model.get_all_cubes()
    
    outputs = {}
    
    if mode == 'by_face':
        # Track unique UV regions to avoid duplicates
        seen_uvs = {}
        
        for cube_info in cubes:
            bone_name = cube_info['bone']
            cube_idx = cube_info['cube_index']
            cube = cube_info['cube_data']
            uv = cube.get('uv', {})
            
            # Handle old format: uv is a list [x, y]
            if isinstance(uv, list):
                uv = model._generate_box_uv_old(uv, cube.get('size', [1, 1, 1]))
            
            for face_name in ['north', 'south', 'east', 'west', 'up', 'down']:
                if face_name not in uv:
                    continue
                    
                # Create unique key for this UV region
                uv_key = f"{uv[face_name]['uv'][0]}_{uv[face_name]['uv'][1]}_{uv[face_name]['uv_size'][0]}_{uv[face_name]['uv_size'][1]}"
                
                # Skip if already processed (handles mirror bones)
                if uv_key in seen_uvs:
                    continue
                    
                face_img = model.extract_face_texture(uv[face_name], face_name)
                if not face_img or face_img.size[0] == 0 or face_img.size[1] == 0:
                    continue
                
                # Skip fully transparent faces
                pixels = face_img.load()
                has_color = False
                for x in range(face_img.size[0]):
                    for y in range(face_img.size[1]):
                        if pixels[x, y][3] > 0:  # Alpha > 0
                            has_color = True
                            break
                    if has_color:
                        break
                
                if not has_color:
                    continue
                
                key = f"{bone_name}_cube{cube_idx}_{face_name}"
                output_path = output_dir / f"{model.identifier}_{key}.pxvg"
                
                encode_face_to_pxvg(
                    face_img, 
                    output_path,
                    metadata={
                        'model': model.identifier,
                        'bone': bone_name,
                        'cube_index': cube_idx,
                        'face': face_name,
                        'uv': uv[face_name]
                    }
                )
                outputs[key] = output_path
                seen_uvs[uv_key] = key
                        
    else:  # mode == 'by_bone' (default)
        # One PXVG per bone (good balance)
        bones_dict = {}
        for cube_info in cubes:
            bone_name = cube_info['bone']
            if bone_name not in bones_dict:
                bones_dict[bone_name] = []
            bones_dict[bone_name].append(cube_info)
            
        for bone_name, bone_cubes in bones_dict.items():
            output_path = output_dir / f"{model.identifier}_{bone_name}.pxvg"
            _encode_bone_to_pxvg(model, bone_cubes, output_path)
            outputs[bone_name] = output_path
        
    return outputs


def encode_face_to_pxvg(
    face_img: Image.Image, 
    output_path: Path, 
    metadata: Optional[Dict] = None
):
    """Encode a single cube face texture to PXVG.
    
    Args:
        face_img: PIL Image of the face texture
        output_path: Where to save the PXVG file
        metadata: Optional metadata to embed in comments
    """
    from ..smart_encoder import smart_encode_pxvg
    
    # Save face image temporarily
    with NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        face_img.save(tmp_path)
        
    try:
        # Encode to PXVG with auto block detection
        gw, gh, num_colors, block_size = smart_encode_pxvg(
            tmp_path, 
            output_path, 
            block_size=1, 
            auto_detect=True
        )
        
        # Add metadata as XML comments
        if metadata:
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Insert metadata after XML declaration
            comment_lines = ['<!-- Minecraft Geometry Face Texture -->']
            for key, value in metadata.items():
                comment_lines.append(f'<!-- {key}: {value} -->')
            comment_lines.append(f'<!-- dimensions: {face_img.size[0]}x{face_img.size[1]} -->')
            comment_lines.append(f'<!-- colors: {num_colors} -->')
            comment_lines.append(f'<!-- block_size: {block_size} -->')
            
            # Insert after <?xml...?>
            lines[1:1] = comment_lines
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
    finally:
        tmp_path.unlink(missing_ok=True)


def _encode_bone_to_pxvg(model: GeoModel, bone_cubes: List[Dict], output_path: Path):
    """Encode all cubes in a bone to a single PXVG with layers."""
    from ..canvas import Canvas
    
    bone_name = bone_cubes[0]['bone']
    
    # Collect all faces with their images
    faces_data = []
    max_w, max_h = 0, 0
    
    for cube_info in bone_cubes:
        cube = cube_info['cube_data']
        cube_idx = cube_info['cube_index']
        uv = cube.get('uv', {})
        
        # Handle old format
        if isinstance(uv, list):
            uv = model._generate_box_uv_old(uv, cube.get('size', [1, 1, 1]))
        
        for face_name in ['north', 'south', 'east', 'west', 'up', 'down']:
            if face_name not in uv:
                continue
                
            face_img = model.extract_face_texture(uv[face_name], face_name)
            if not face_img:
                continue
            
            # Skip transparent faces
            pixels = face_img.load()
            has_color = False
            for x in range(face_img.size[0]):
                for y in range(face_img.size[1]):
                    if pixels[x, y][3] > 0:
                        has_color = True
                        break
                if has_color:
                    break
            
            if not has_color:
                continue
            
            w, h = face_img.size
            max_w = max(max_w, w)
            max_h = max(max_h, h)
            
            faces_data.append({
                'cube_idx': cube_idx,
                'face': face_name,
                'image': face_img,
                'uv': uv[face_name]
            })
    
    if not faces_data:
        return
    
    # Create canvas with layers for each face
    canvas = Canvas(max_w, max_h)
    
    for face_info in faces_data:
        layer_name = f"cube{face_info['cube_idx']}_{face_info['face']}"
        canvas.add_layer(layer_name)
        canvas.set_layer(layer_name)
        
        face_img = face_info['image']
        pixels = face_img.load()
        
        for x in range(face_img.size[0]):
            for y in range(face_img.size[1]):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    canvas.set_pixel((x, y), (r, g, b, a))
    
    # Merge and save
    canvas.merge_all()
    
    with NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        canvas.save(str(tmp_path), scale=1)
    
    try:
        from ..smart_encoder import smart_encode_pxvg
        smart_encode_pxvg(tmp_path, output_path, block_size=1, auto_detect=True)
        
        # Add metadata
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        lines.insert(1, f'<!-- Model: {model.identifier} -->')
        lines.insert(2, f'<!-- Bone: {bone_name} -->')
        lines.insert(3, f'<!-- Faces: {len(faces_data)} -->')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    finally:
        tmp_path.unlink(missing_ok=True)

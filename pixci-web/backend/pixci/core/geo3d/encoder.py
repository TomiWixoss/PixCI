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
            - 'by_bone': One PXVG per bone (default)
            - 'by_cube': One PXVG per cube (all 6 faces)
            - 'by_face': One PXVG per cube face (most granular)
            - 'single': One PXVG for entire model
        
    Returns:
        Dictionary mapping identifiers to output PXVG paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model = GeoModel(geo_path, texture_path)
    cubes = model.get_all_cubes()
    
    outputs = {}
    
    if mode == 'by_face':
        # Most granular: separate PXVG for each face
        for cube_info in cubes:
            bone_name = cube_info['bone']
            cube_idx = cube_info['cube_index']
            cube = cube_info['cube_data']
            uv = cube.get('uv', {})
            
            for face_name in ['north', 'south', 'east', 'west', 'up', 'down']:
                if face_name in uv:
                    face_img = model.extract_face_texture(uv[face_name], face_name)
                    if face_img and face_img.size[0] > 0 and face_img.size[1] > 0:
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
                        
    elif mode == 'by_cube':
        # One PXVG per cube (combines all faces)
        for cube_info in cubes:
            bone_name = cube_info['bone']
            cube_idx = cube_info['cube_index']
            key = f"{bone_name}_cube{cube_idx}"
            output_path = output_dir / f"{model.identifier}_{key}.pxvg"
            
            _encode_cube_to_pxvg(model, cube_info, output_path)
            outputs[key] = output_path
            
    elif mode == 'by_bone':
        # One PXVG per bone (default, good balance)
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
            
    else:  # mode == 'single'
        # Single PXVG for entire model
        output_path = output_dir / f"{model.identifier}.pxvg"
        _encode_model_to_pxvg(model, cubes, output_path)
        outputs['model'] = output_path
        
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


def _encode_cube_to_pxvg(model: GeoModel, cube_info: Dict, output_path: Path):
    """Encode all faces of a cube into a single PXVG with layers."""
    from ..canvas import Canvas
    
    cube = cube_info['cube_data']
    uv = cube.get('uv', {})
    bone_name = cube_info['bone']
    cube_idx = cube_info['cube_index']
    
    # Determine canvas size (max face dimensions)
    max_w, max_h = 0, 0
    faces_data = {}
    
    for face_name in ['north', 'south', 'east', 'west', 'up', 'down']:
        if face_name in uv:
            face_img = model.extract_face_texture(uv[face_name], face_name)
            if face_img:
                w, h = face_img.size
                max_w = max(max_w, w)
                max_h = max(max_h, h)
                faces_data[face_name] = face_img
                
    if not faces_data:
        return
        
    # Create canvas with layers for each face
    canvas = Canvas(max_w, max_h)
    
    for face_name, face_img in faces_data.items():
        canvas.add_layer(face_name)
        canvas.set_layer(face_name)
        
        # Load face image onto layer
        pixels = face_img.load()
        for x in range(face_img.size[0]):
            for y in range(face_img.size[1]):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    canvas.set_pixel((x, y), (r, g, b, a))
                    
    # Save as PXVG (need to implement Canvas.save_pxvg)
    # For now, merge and save as PNG, then encode
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
        lines.insert(3, f'<!-- Cube: {cube_idx} -->')
        lines.insert(4, f'<!-- Faces: {", ".join(faces_data.keys())} -->')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    finally:
        tmp_path.unlink(missing_ok=True)


def _encode_bone_to_pxvg(model: GeoModel, bone_cubes: List[Dict], output_path: Path):
    """Encode all cubes in a bone to a single PXVG."""
    # TODO: Implement bone-level encoding
    # This would create a structured PXVG with groups for each cube
    pass


def _encode_model_to_pxvg(model: GeoModel, cubes: List[Dict], output_path: Path):
    """Encode the entire model to a single PXVG."""
    # TODO: Implement full model encoding
    pass

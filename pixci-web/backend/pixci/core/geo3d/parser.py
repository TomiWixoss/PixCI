"""
parser.py - Minecraft Geometry (geo.json) Parser
Parses Blockbench/Minecraft Bedrock Edition geometry files.
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image


class GeoModel:
    """Represents a parsed Minecraft geometry model."""
    
    def __init__(self, geo_path: Path, texture_path: Optional[Path] = None):
        self.geo_path = Path(geo_path)
        self.texture_path = Path(texture_path) if texture_path else None
        self.data = None
        self.texture = None
        self.texture_width = 64
        self.texture_height = 64
        self.identifier = "unknown"
        self.bones = []
        self.visible_bounds = {}
        
        self._load()
        
    def _load(self):
        """Load and parse geo.json file."""
        with open(self.geo_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
        # Extract geometry data
        geometry = self.data.get('minecraft:geometry', [{}])[0]
        desc = geometry.get('description', {})
        
        self.identifier = desc.get('identifier', 'unknown').replace('geometry.', '')
        self.texture_width = desc.get('texture_width', 64)
        self.texture_height = desc.get('texture_height', 64)
        self.bones = geometry.get('bones', [])
        
        # Visible bounds (for rendering hints)
        self.visible_bounds = {
            'width': desc.get('visible_bounds_width', 2),
            'height': desc.get('visible_bounds_height', 2),
            'offset': desc.get('visible_bounds_offset', [0, 0, 0])
        }
        
        # Load texture if provided
        if self.texture_path and self.texture_path.exists():
            self.texture = Image.open(self.texture_path).convert('RGBA')
            
    def get_all_cubes(self) -> List[Dict]:
        """Extract all cubes from all bones with full metadata.
        
        Returns:
            List of dicts containing:
                - bone: bone name
                - parent: parent bone name (or None)
                - bone_pivot: [x, y, z] pivot point
                - bone_rotation: [x, y, z] rotation in degrees
                - cube_index: index within bone
                - cube_data: full cube dict (origin, size, uv, rotation, etc)
        """
        cubes = []
        for bone in self.bones:
            bone_name = bone.get('name', 'unnamed')
            bone_pivot = bone.get('pivot', [0, 0, 0])
            bone_rotation = bone.get('rotation', [0, 0, 0])
            parent = bone.get('parent', None)
            
            for cube_idx, cube in enumerate(bone.get('cubes', [])):
                cubes.append({
                    'bone': bone_name,
                    'parent': parent,
                    'bone_pivot': bone_pivot,
                    'bone_rotation': bone_rotation,
                    'cube_index': cube_idx,
                    'cube_data': cube
                })
        return cubes
        
    def get_bone_hierarchy(self) -> Dict[str, List[str]]:
        """Build parent-child bone hierarchy.
        
        Returns:
            Dict mapping parent bone names to list of child bone names
        """
        hierarchy = {}
        for bone in self.bones:
            parent = bone.get('parent')
            if parent:
                if parent not in hierarchy:
                    hierarchy[parent] = []
                hierarchy[parent].append(bone.get('name'))
        return hierarchy
        
    def extract_face_texture(self, uv_data: Dict, face_name: str) -> Optional[Image.Image]:
        """Extract a single face texture from the main texture atlas.
        
        Args:
            uv_data: UV mapping data for the face (contains 'uv' and 'uv_size')
            face_name: 'north', 'south', 'east', 'west', 'up', 'down'
            
        Returns:
            PIL Image of the face texture, or None if texture not loaded
        """
        if not self.texture:
            return None
            
        uv = uv_data.get('uv', [0, 0])
        uv_size = uv_data.get('uv_size', [1, 1])
        
        # Convert UV coordinates (0-texture_width/height range)
        x1 = float(uv[0])
        y1 = float(uv[1])
        w = float(uv_size[0])
        h = float(uv_size[1])
        
        # Handle negative UV sizes (flipped textures)
        if w < 0:
            x1 = x1 + w
            w = abs(w)
        if h < 0:
            y1 = y1 + h
            h = abs(h)
            
        x2 = x1 + w
        y2 = y1 + h
        
        # Clamp to texture bounds
        x1 = max(0, min(int(x1), self.texture_width))
        y1 = max(0, min(int(y1), self.texture_height))
        x2 = max(0, min(int(x2), self.texture_width))
        y2 = max(0, min(int(y2), self.texture_height))
        
        # Extract region
        if x2 > x1 and y2 > y1:
            return self.texture.crop((x1, y1, x2, y2))
        return None
        
    def get_cube_info(self, bone_name: str, cube_index: int) -> Optional[Dict]:
        """Get detailed info about a specific cube.
        
        Args:
            bone_name: Name of the bone
            cube_index: Index of cube within bone
            
        Returns:
            Dict with cube metadata or None if not found
        """
        for bone in self.bones:
            if bone.get('name') == bone_name:
                cubes = bone.get('cubes', [])
                if 0 <= cube_index < len(cubes):
                    cube = cubes[cube_index]
                    return {
                        'origin': cube.get('origin', [0, 0, 0]),
                        'size': cube.get('size', [1, 1, 1]),
                        'pivot': cube.get('pivot', [0, 0, 0]),
                        'rotation': cube.get('rotation', [0, 0, 0]),
                        'uv': cube.get('uv', {}),
                        'inflate': cube.get('inflate', 0),
                        'mirror': cube.get('mirror', False)
                    }
        return None
        
    def get_face_dimensions(self, cube_data: Dict, face_name: str) -> Tuple[int, int]:
        """Calculate the pixel dimensions of a cube face.
        
        Args:
            cube_data: Cube dictionary
            face_name: 'north', 'south', 'east', 'west', 'up', 'down'
            
        Returns:
            (width, height) in pixels
        """
        size = cube_data.get('size', [1, 1, 1])
        
        # Map face to dimensions
        if face_name in ['north', 'south']:
            return (int(size[0]), int(size[1]))  # width, height
        elif face_name in ['east', 'west']:
            return (int(size[2]), int(size[1]))  # depth, height
        elif face_name in ['up', 'down']:
            return (int(size[0]), int(size[2]))  # width, depth
        return (1, 1)

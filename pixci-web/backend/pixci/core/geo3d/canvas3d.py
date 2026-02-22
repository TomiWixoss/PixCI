"""
canvas3d.py - 3D Canvas for AI to create Minecraft models from scratch
Provides high-level API for AI to design 3D models programmatically.
"""
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import json
from PIL import Image


class Canvas3D:
    """High-level 3D modeling canvas for AI.
    
    Allows AI to create Minecraft geometry models programmatically
    without dealing with low-level geo.json structure.
    """
    
    def __init__(self, identifier: str, texture_width: int = 64, texture_height: int = 64):
        self.identifier = identifier
        self.texture_width = texture_width
        self.texture_height = texture_height
        self.bones = []
        self.texture_atlas = Image.new('RGBA', (texture_width, texture_height), (0, 0, 0, 0))
        self.next_uv_x = 0
        self.next_uv_y = 0
        self.current_bone = None
        
    def add_bone(
        self, 
        name: str, 
        pivot: Tuple[float, float, float] = (0, 0, 0),
        rotation: Tuple[float, float, float] = (0, 0, 0),
        parent: Optional[str] = None
    ):
        """Add a new bone to the model.
        
        Args:
            name: Bone identifier
            pivot: Pivot point [x, y, z]
            rotation: Rotation in degrees [x, y, z]
            parent: Parent bone name (for hierarchical models)
        """
        bone = {
            'name': name,
            'pivot': list(pivot),
            'rotation': list(rotation),
            'cubes': []
        }
        
        if parent:
            bone['parent'] = parent
            
        self.bones.append(bone)
        self.current_bone = bone
        return self
        
    def add_cube(
        self,
        origin: Tuple[float, float, float],
        size: Tuple[float, float, float],
        texture: Optional[Image.Image] = None,
        uv_offset: Optional[Tuple[int, int]] = None,
        rotation: Tuple[float, float, float] = (0, 0, 0),
        pivot: Optional[Tuple[float, float, float]] = None
    ):
        """Add a cube to the current bone.
        
        Args:
            origin: Bottom-left-back corner [x, y, z]
            size: Dimensions [width, height, depth]
            texture: Optional PIL Image for cube texture (auto-placed in atlas)
            uv_offset: Manual UV offset in atlas (if texture not provided)
            rotation: Cube rotation [x, y, z] in degrees
            pivot: Rotation pivot point (defaults to origin)
        """
        if not self.current_bone:
            raise ValueError("No bone selected. Call add_bone() first.")
            
        cube = {
            'origin': list(origin),
            'size': list(size),
            'uv': {}
        }
        
        if rotation != (0, 0, 0):
            cube['rotation'] = list(rotation)
            
        if pivot:
            cube['pivot'] = list(pivot)
            
        # Handle texture placement
        if texture:
            uv_data = self._place_texture_in_atlas(texture, size)
            cube['uv'] = uv_data
        elif uv_offset:
            cube['uv'] = self._generate_box_uv(uv_offset, size)
            
        self.current_bone['cubes'].append(cube)
        return self
        
    def add_box(
        self,
        center: Tuple[float, float, float],
        size: Tuple[float, float, float],
        texture: Optional[Image.Image] = None
    ):
        """Add a cube centered at a point (convenience method).
        
        Args:
            center: Center point [x, y, z]
            size: Dimensions [width, height, depth]
            texture: Optional texture image
        """
        origin = (
            center[0] - size[0] / 2,
            center[1] - size[1] / 2,
            center[2] - size[2] / 2
        )
        return self.add_cube(origin, size, texture)
        
    def set_face_texture(
        self,
        bone_name: str,
        cube_index: int,
        face: str,
        texture: Image.Image
    ):
        """Set texture for a specific cube face.
        
        Args:
            bone_name: Name of the bone
            cube_index: Index of cube in bone
            face: 'north', 'south', 'east', 'west', 'up', 'down'
            texture: PIL Image for the face
        """
        bone = self._get_bone(bone_name)
        if not bone or cube_index >= len(bone['cubes']):
            raise ValueError(f"Cube not found: {bone_name}[{cube_index}]")
            
        cube = bone['cubes'][cube_index]
        
        # Place texture in atlas
        uv_x, uv_y = self._allocate_atlas_space(texture.size[0], texture.size[1])
        self.texture_atlas.paste(texture, (uv_x, uv_y), texture)
        
        # Update UV mapping
        cube['uv'][face] = {
            'uv': [uv_x, uv_y],
            'uv_size': [texture.size[0], texture.size[1]]
        }
        
        return self
        
    def save(self, geo_path: Path, texture_path: Path):
        """Save the 3D model to geo.json and texture atlas.
        
        Args:
            geo_path: Output path for geo.json
            texture_path: Output path for texture PNG
        """
        geo_data = {
            'format_version': '1.12.0',
            'minecraft:geometry': [{
                'description': {
                    'identifier': f'geometry.{self.identifier}',
                    'texture_width': self.texture_width,
                    'texture_height': self.texture_height,
                    'visible_bounds_width': 2,
                    'visible_bounds_height': 2,
                    'visible_bounds_offset': [0, 0, 0]
                },
                'bones': self.bones
            }]
        }
        
        # Save geo.json
        with open(geo_path, 'w', encoding='utf-8') as f:
            json.dump(geo_data, f, indent='\t')
            
        # Save texture atlas
        self.texture_atlas.save(texture_path)
        
    def _get_bone(self, name: str) -> Optional[Dict]:
        """Get bone by name."""
        for bone in self.bones:
            if bone['name'] == name:
                return bone
        return None
        
    def _place_texture_in_atlas(
        self, 
        texture: Image.Image, 
        cube_size: Tuple[float, float, float]
    ) -> Dict:
        """Place a cube texture in the atlas and return UV mapping.
        
        This generates a box UV layout (unwrapped cube).
        """
        w, h, d = cube_size
        
        # Calculate required atlas space for box UV
        # Layout: top, bottom, front, back, left, right
        required_width = int(w + d + w + d)
        required_height = int(h + d)
        
        # Allocate space
        uv_x, uv_y = self._allocate_atlas_space(required_width, required_height)
        
        # If texture provided, place it (assuming it's a box UV layout)
        if texture:
            self.texture_atlas.paste(texture, (uv_x, uv_y), texture)
            
        # Generate UV mapping for each face
        return self._generate_box_uv((uv_x, uv_y), cube_size)
        
    def _generate_box_uv(
        self, 
        offset: Tuple[int, int], 
        size: Tuple[float, float, float]
    ) -> Dict:
        """Generate standard box UV mapping.
        
        Box UV layout:
        ```
           [up]
        [west][north][east][south]
           [down]
        ```
        """
        x, y = offset
        w, h, d = [int(s) for s in size]
        
        return {
            'north': {'uv': [x + d, y + d], 'uv_size': [w, h]},
            'south': {'uv': [x + d + w + d, y + d], 'uv_size': [w, h]},
            'east': {'uv': [x + d + w, y + d], 'uv_size': [d, h]},
            'west': {'uv': [x, y + d], 'uv_size': [d, h]},
            'up': {'uv': [x + d, y], 'uv_size': [w, d]},
            'down': {'uv': [x + d + w, y], 'uv_size': [w, d]}
        }
        
    def _allocate_atlas_space(self, width: int, height: int) -> Tuple[int, int]:
        """Allocate space in texture atlas (simple row-based packing).
        
        Returns:
            (x, y) coordinates in atlas
        """
        # Check if current row has space
        if self.next_uv_x + width > self.texture_width:
            # Move to next row
            self.next_uv_x = 0
            self.next_uv_y += height
            
        if self.next_uv_y + height > self.texture_height:
            raise ValueError(f"Texture atlas full! Cannot fit {width}x{height}")
            
        x, y = self.next_uv_x, self.next_uv_y
        self.next_uv_x += width
        
        return (x, y)

"""
geo3d - Minecraft Geometry 3D Model Framework for AI
Converts Blockbench/Minecraft models to AI-editable PXVG format.
"""
from .parser import GeoModel
from .encoder import encode_geo_to_pxvg, encode_face_to_pxvg
from .decoder import decode_pxvg_to_geo, rebuild_texture_atlas
from .canvas3d import Canvas3D

__all__ = [
    'GeoModel',
    'encode_geo_to_pxvg',
    'encode_face_to_pxvg',
    'decode_pxvg_to_geo',
    'rebuild_texture_atlas',
    'Canvas3D',
]

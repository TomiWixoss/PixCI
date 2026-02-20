from .core.canvas import Canvas
from .core.grid_engine import (
    encode_image, encode_code, decode_text, 
    init_canvas, init_code_canvas,
    AI_CODE_SYSTEM_PROMPT,
)
from .core.mixins.color import _OFFLINE_PALETTES as BUILTIN_PALETTES

__all__ = [
    "Canvas",
    "encode_image",
    "encode_code",
    "decode_text",
    "init_canvas",
    "init_code_canvas",
    "AI_CODE_SYSTEM_PROMPT",
    "BUILTIN_PALETTES",
]

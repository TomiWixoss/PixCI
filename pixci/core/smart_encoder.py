"""
smart_encoder.py - Simplified PXVG encoder
Tự động phát hiện block size và encode tối ưu
"""
import numpy as np
from pathlib import Path
from PIL import Image
from typing import Tuple


def smart_encode_pxvg(
    image_path: Path, 
    output_path: Path, 
    block_size: int = 1, 
    auto_detect: bool = True
) -> Tuple[int, int, int, int]:
    """
    Smart PXVG encoder - đơn giản và hiệu quả
    
    Args:
        image_path: Đường dẫn ảnh input
        output_path: Đường dẫn PXVG output
        block_size: Kích thước block (1-16)
        auto_detect: Tự động phát hiện block size tối ưu
    
    Returns:
        (grid_width, grid_height, num_colors, final_block_size)
    """
    from .code_engine import _detect_block_size, _build_grid, _find_best_rects, _collect_all_runs
    
    # Load image
    img = Image.open(image_path).convert("RGBA")
    
    # Auto detect block size
    if auto_detect:
        block_size = _detect_block_size(img)
    
    # Build grid
    gw, gh, grid, palette = _build_grid(img, block_size)
    
    # Find rectangles
    rects, used = _find_best_rects(grid, gw, gh)
    
    # Collect remaining runs (rows)
    runs = _collect_all_runs(grid, gw, gh, used)
    
    # Separate single pixels and multi-pixel runs
    single_pixels = []
    rows = []
    
    for y, x_start, x_end, color in runs:
        if x_start == x_end:
            single_pixels.append((y, x_start, color))
        else:
            rows.append((y, x_start, x_end, color))
    
    # Group single pixels by color for dots
    dots_by_color = {}
    for y, x, color in single_pixels:
        if color not in dots_by_color:
            dots_by_color[color] = []
        dots_by_color[color].append((x, y))
    
    # Write PXVG file
    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(f'<pxvg w="{gw}" h="{gh}" xmlns="http://pixci.dev/pxvg">\n')
        
        # Palette
        f.write('  <palette>\n')
        for hex_color, color_key in sorted(palette.items(), key=lambda x: x[1]):
            f.write(f'    <color k="{color_key}" hex="{hex_color}" />\n')
        f.write('  </palette>\n')
        
        # Layer
        f.write('  <layer id="main">\n')
        
        # Rectangles (most efficient)
        for x0, y0, x1, y1, color in rects:
            w = x1 - x0 + 1
            h = y1 - y0 + 1
            f.write(f'    <rect x="{x0}" y="{y0}" w="{w}" h="{h}" c="{color}" />\n')
        
        # Rows (horizontal lines)
        for y, x_start, x_end, color in rows:
            f.write(f'    <row y="{y}" x1="{x_start}" x2="{x_end}" c="{color}" />\n')
        
        # Dots (single pixels grouped by color)
        for color in sorted(dots_by_color.keys()):
            points = dots_by_color[color]
            pts_str = " ".join([f"{x},{y}" for x, y in points])
            f.write(f'    <dots c="{color}" pts="{pts_str}" />\n')
        
        f.write('  </layer>\n')
        f.write('</pxvg>\n')
    
    return (gw, gh, len(palette), block_size)


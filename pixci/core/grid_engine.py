"""
grid_engine.py - Encode/Decode giữa Image ↔ Text Grid format.
Đây là chế độ cơ bản dùng ký tự ASCII biểu diễn pixel.
"""
import re
from pathlib import Path
from PIL import Image
from typing import Tuple

# Re-export prompts for backward compatibility
from .prompts import SYSTEM_PROMPT, AI_CODE_SYSTEM_PROMPT, init_code_canvas
# Re-export code engine for backward compatibility  
from .code_engine import encode_code


def rgb2hex(r: int, g: int, b: int, a: int = 255) -> str:
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


def hex2rgba(hex_str: str) -> Tuple[int, int, int, int]:
    if hex_str.startswith("#"):
        hex_str = hex_str[1:]
    if len(hex_str) == 6:
        hex_str += "FF"
    if len(hex_str) == 8:
        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), int(hex_str[6:8], 16))
    return (0, 0, 0, 0)


def detect_block_size(img: Image.Image) -> int:
    pixels = img.load()
    w, h = img.size
    if w == 0:
        return 1
    min_run = w
    for y in range(0, h, max(1, h // 10)):
        current_color = pixels[0, y]
        current_run = 0
        for x in range(w):
            if pixels[x, y] == current_color:
                current_run += 1
            else:
                if current_run > 0:
                    min_run = min(min_run, current_run)
                current_color = pixels[x, y]
                current_run = 1
        if current_run > 0:
            min_run = min(min_run, current_run)
    for x in range(0, w, max(1, w // 10)):
        current_color = pixels[x, 0]
        current_run = 0
        for y in range(h):
            if pixels[x, y] == current_color:
                current_run += 1
            else:
                if current_run > 0:
                    min_run = min(min_run, current_run)
                current_color = pixels[x, y]
                current_run = 1
        if current_run > 0:
            min_run = min(min_run, current_run)
    return max(1, min_run)


def encode_image(image_path: Path, output_path: Path, block_size: int, auto_detect: bool) -> Tuple[int, int, int, int]:
    """Encode image to text grid format ([PALETTE] + [GRID])."""
    img = Image.open(image_path).convert("RGBA")
    
    if auto_detect:
        block_size = detect_block_size(img)
        
    width, height = img.size
    grid_w = width // block_size
    grid_h = height // block_size
    pixels = img.load()
    
    chars = [chr(i) for i in range(ord('A'), ord('Z')+1)] + [str(i) for i in range(10)]
    palette_mapping = {}
    char_idx = 0
    
    output_grid = []
    
    for y in range(0, height, block_size):
        row = []
        for x in range(0, width, block_size):
            r, g, b, a = pixels[x, y]
            if a == 0:
                row.append(".")
            else:
                hex_val = rgb2hex(r, g, b, a)
                if hex_val not in palette_mapping:
                    if char_idx >= len(chars):
                        raise ValueError("Quá nhiều màu! PixCI chỉ hỗ trợ tối đa 36 màu duy nhất.")
                    palette_mapping[hex_val] = chars[char_idx]
                    char_idx += 1
                row.append(palette_mapping[hex_val])
        output_grid.append(" ".join(row))
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[PALETTE]\n")
        f.write(". = #00000000 (Trong suốt)\n")
        for hex_val, char in palette_mapping.items():
            f.write(f"{char} = {hex_val}\n")
        f.write("\n[GRID]\n")
        for row_str in output_grid:
            f.write(row_str + "\n")
            
    return (grid_w, grid_h, len(palette_mapping), block_size)


def decode_text(text_path: Path, output_path: Path, scale: int) -> Tuple[int, int]:
    """Decode text grid format to image."""
    with open(text_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    palette_match = re.search(r"\[PALETTE\](.*?)(?:\n\s*\n|\[GRID\])", content, re.DOTALL)
    grid_match = re.search(r"\[GRID\](.*?)(\n\s*\n|\Z)", content, re.DOTALL)
    
    if not palette_match or not grid_match:
        raise ValueError("Không tìm thấy phần [PALETTE] hoặc [GRID] trong file.")
        
    palette_text = palette_match.group(1).strip().split("\n")
    grid_text = grid_match.group(1).strip().split("\n")
    
    palette = {}
    for line in palette_text:
        line = line.strip()
        if not line: continue
        parts = line.split("=")
        if len(parts) >= 2:
            char = parts[0].strip()
            color_part = parts[1].strip()
            hex_match = re.search(r"(#[A-Fa-f0-9]{6,8})", color_part)
            if hex_match:
                palette[char] = hex_match.group(1)
                
    if "." not in palette:
        palette["."] = "#00000000"
        
    grid_lines = []
    for line in grid_text:
        if line.strip().startswith("```"): continue
        chars = line.strip().split()
        if chars:
            grid_lines.append(chars)
            
    if not grid_lines:
        raise ValueError("Lưới rỗng.")
        
    height = len(grid_lines)
    width = len(grid_lines[0])
    
    for idx, row in enumerate(grid_lines):
        if len(row) != width:
            raise ValueError(f"Hàng {idx+1} có độ dài không hợp lệ {len(row)} (Yêu cầu {width}).")
            
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = img.load()
    
    for y, row in enumerate(grid_lines):
        for x, char in enumerate(row):
            if char not in palette:
                raise ValueError(f"Ký tự '{char}' tại ({x}, {y}) không tồn tại trong palette!")
            pixels[x, y] = hex2rgba(palette[char])
            
    if scale > 1:
        img = img.resize((width * scale, height * scale), Image.NEAREST)
        
    img.save(output_path)
    return (width, height)
    

def init_canvas(output_path: Path, width: int, height: int):
    """Init an empty text grid canvas."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[PALETTE]\n")
        f.write(". = #00000000 (Trong suốt)\n")
        f.write("A = #000000FF (Đen)\n\n")
        f.write("[GRID]\n")
        for _ in range(height):
            f.write(" ".join(["."] * width) + "\n")

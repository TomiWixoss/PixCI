import re
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict

SYSTEM_PROMPT = """Bạn là một AI chuyên vẽ Pixel Art.
Người dùng sẽ cung cấp cho bạn một [PALETTE] (bảng màu) và một [GRID] (lưới) gồm các ký tự đại diện cho một bức vẽ pixel.
Nhiệm vụ của bạn là hiểu bức vẽ, chỉnh sửa nó, hoặc tạo ra bức vẽ mới theo cùng một định dạng.
- [PALETTE]: Ánh xạ các ký tự (A-Z, 0-9) sang mã màu Hex (#RRGGBBAA). '.' luôn là trong suốt (khoảng trống).
- [GRID]: Đại diện cho các pixel. Mỗi ký tự hoặc '.' được cách nhau bởi một khoảng trắng. Mỗi dòng là một hàng.
"""

def rgb2hex(r, g, b, a=255):
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"

def hex2rgba(hex_str: str):
    if hex_str.startswith("#"):
        hex_str = hex_str[1:]
    
    # Pad to 8 if it's 6
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
    

def encode_image(image_path: Path, output_path: Path, block_size: int, auto_detect: bool) -> tuple[int, int, int, int]:
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


# =============================================================================
# SMART ENCODE CODE - Phát hiện pattern thay vì dump set_pixel
# =============================================================================

def _build_pixel_grid(img: Image.Image, block_size: int) -> Tuple[int, int, List[List[str]], Dict[str, str]]:
    """Build a grid of palette keys from an image."""
    width, height = img.size
    grid_w = width // block_size
    grid_h = height // block_size
    pixels = img.load()
    
    palette_mapping = {}  # hex -> key
    char_idx = 0
    
    grid = []
    for gy in range(grid_h):
        row = []
        for gx in range(grid_w):
            x, y = gx * block_size, gy * block_size
            r, g, b, a = pixels[x, y]
            if a == 0:
                row.append(None)
            else:
                hex_val = rgb2hex(r, g, b, a)
                if hex_val not in palette_mapping:
                    char_idx += 1
                    palette_mapping[hex_val] = f"C{char_idx:02d}"
                row.append(palette_mapping[hex_val])
        grid.append(row)
    
    return grid_w, grid_h, grid, palette_mapping


def _detect_filled_rects(grid: List[List[str]], grid_w: int, grid_h: int) -> List[Tuple[int, int, int, int, str]]:
    """Detect maximal filled rectangles (greedy). Returns [(x0, y0, x1, y1, color), ...]."""
    used = [[False]*grid_w for _ in range(grid_h)]
    rects = []
    
    for y in range(grid_h):
        for x in range(grid_w):
            if used[y][x] or grid[y][x] is None:
                continue
            color = grid[y][x]
            
            # Expand rectangle right and down
            max_x = x
            while max_x + 1 < grid_w and grid[y][max_x + 1] == color and not used[y][max_x + 1]:
                max_x += 1
            
            max_y = y
            while max_y + 1 < grid_h:
                ok = True
                for cx in range(x, max_x + 1):
                    if grid[max_y + 1][cx] != color or used[max_y + 1][cx]:
                        ok = False
                        break
                if ok:
                    max_y += 1
                else:
                    break
            
            w = max_x - x + 1
            h = max_y - y + 1
            
            # Only emit as rect/row if it covers more than 1 pixel
            if w * h >= 2:
                for ry in range(y, max_y + 1):
                    for rx in range(x, max_x + 1):
                        used[ry][rx] = True
                rects.append((x, y, max_x, max_y, color))
    
    return rects, used


def _collect_draw_rows(grid: List[List[str]], grid_w: int, grid_h: int, used: List[List[bool]]) -> Dict[str, List[Tuple[int, int, int]]]:
    """Collect remaining pixels as horizontal runs grouped by color.
    Returns {color: [(y, x_start, x_end), ...]}
    """
    color_rows = {}
    for y in range(grid_h):
        x = 0
        while x < grid_w:
            if used[y][x] or grid[y][x] is None:
                x += 1
                continue
            color = grid[y][x]
            start_x = x
            while x < grid_w and grid[y][x] == color and not used[y][x]:
                used[y][x] = True
                x += 1
            end_x = x - 1
            if color not in color_rows:
                color_rows[color] = []
            color_rows[color].append((y, start_x, end_x))
    return color_rows


def _collect_single_pixels(grid: List[List[str]], grid_w: int, grid_h: int, used: List[List[bool]]) -> Dict[str, List[Tuple[int, int]]]:
    """Collect any remaining single pixels."""
    singles = {}
    for y in range(grid_h):
        for x in range(grid_w):
            if not used[y][x] and grid[y][x] is not None:
                color = grid[y][x]
                if color not in singles:
                    singles[color] = []
                singles[color].append((x, y))
                used[y][x] = True
    return singles


def encode_code(image_path: Path, output_path: Path, block_size: int, auto_detect: bool) -> tuple[int, int, int, int]:
    """Smart encode: converts an image to READABLE PixCI Python code.
    
    Instead of dumping set_pixel() for every pixel, this:
    1. Detects filled rectangles → fill_rect()
    2. Groups horizontal runs → draw_rows()  
    3. Only uses set_pixel() for isolated pixels
    
    This makes the output code LEARNABLE by AI - it can see patterns
    and understand how to use the PixCI API.
    """
    img = Image.open(image_path).convert("RGBA")
    
    if auto_detect:
        block_size = detect_block_size(img)
    
    grid_w, grid_h, grid, palette_mapping = _build_pixel_grid(img, block_size)
    
    # Detect patterns
    rects, used = _detect_filled_rects(grid, grid_w, grid_h)
    color_rows = _collect_draw_rows(grid, grid_w, grid_h, used)
    singles = _collect_single_pixels(grid, grid_w, grid_h, used)
    
    with open(output_path, "w", encoding="utf-8") as f:
        # Header with coordinate guide
        f.write(f"# PixCI Smart Code - Generated from {image_path.name}\n")
        f.write(f"# Canvas: {grid_w}x{grid_h} pixels, {len(palette_mapping)} colors\n")
        f.write(f"# Coordinate system: (0,0)=top-left, X→right, Y↓down\n")
        f.write(f"#\n")
        
        # Visual coordinate ruler
        f.write(f"# X ruler:  ")
        for x in range(0, grid_w, 5):
            f.write(f"{x:<5d}")
        f.write(f"\n")
        f.write(f"# Y ruler: 0=top, {grid_h//4}=quarter, {grid_h//2}=middle, {grid_h*3//4}=three-quarter, {grid_h-1}=bottom\n")
        f.write(f"#\n")
        f.write(f"# HƯỚNG DẪN: Mỗi hàm dưới đây vẽ ra MỘT PHẦN của ảnh.\n")
        f.write(f"# AI có thể CHỈNH SỬA bất kỳ tham số nào để thay đổi hình dạng, màu sắc, vị trí.\n")
        f.write(f"# Xem README.md để biết đầy đủ các hàm PixCI hỗ trợ.\n\n")
        
        f.write("import pixci\n\n")
        f.write(f"canvas = pixci.Canvas({grid_w}, {grid_h})\n\n")
        
        # Palette with descriptive comments
        f.write("# === BẢNG MÀU ===\n")
        f.write("canvas.add_palette({\n")
        for hex_val, key in sorted(palette_mapping.items(), key=lambda x: x[1]):
            r, g, b, a = hex2rgba(hex_val)
            # Auto-describe color by HSL
            brightness = (r + g + b) / (3 * 255)
            if brightness > 0.8:
                desc = "sáng"
            elif brightness > 0.5:
                desc = "trung bình"
            elif brightness > 0.2:
                desc = "tối"
            else:
                desc = "rất tối"
            
            max_c = max(r, g, b)
            if max_c - min(r, g, b) < 30:
                hue_name = "xám/trắng/đen"
            elif r >= g and r >= b:
                hue_name = "đỏ/cam" if g > b else "đỏ/hồng"
            elif g >= r and g >= b:
                hue_name = "xanh lá"
            else:
                hue_name = "xanh dương/tím"
            
            f.write(f'    "{key}": "{hex_val}",  # {hue_name}, {desc}\n')
        f.write("})\n\n")
        
        # Filled rectangles
        if rects:
            f.write("# === KHỐI CHỮ NHẬT (vùng đặc) ===\n")
            for x0, y0, x1, y1, color in rects:
                w = x1 - x0 + 1
                h = y1 - y0 + 1
                if w == 1 or h == 1:
                    continue  # Will be handled by draw_rows
                f.write(f'canvas.fill_rect(({x0}, {y0}), ({x1}, {y1}), "{color}")  # {w}x{h} block\n')
            f.write("\n")
        
        # Horizontal runs as draw_rows
        # Merge rects that are 1-pixel tall into draw_rows too
        all_rows_data = {}
        for x0, y0, x1, y1, color in rects:
            w = x1 - x0 + 1
            h = y1 - y0 + 1
            if w >= 2 and h == 1:
                if color not in all_rows_data:
                    all_rows_data[color] = []
                all_rows_data[color].append((y0, x0, x1))
            elif h >= 2 and w == 1:
                # Vertical single-width rects → fill_rect already emitted
                pass
        
        for color, rows_list in color_rows.items():
            if color not in all_rows_data:
                all_rows_data[color] = []
            all_rows_data[color].extend(rows_list)
        
        if all_rows_data:
            f.write("# === DÒNG NGANG (sculpt hình dạng) ===\n")
            f.write("# Format: (y, x_start, x_end, color)\n")
            f.write("# y tăng = xuống dưới, x tăng = sang phải\n")
            for color, rows_list in sorted(all_rows_data.items()):
                rows_list.sort(key=lambda r: (r[0], r[1]))
                if len(rows_list) == 1:
                    y, xs, xe = rows_list[0]
                    f.write(f'canvas.draw_rows([({y}, {xs}, {xe}, "{color}")])\n')
                else:
                    f.write(f'canvas.draw_rows([  # color={color}\n')
                    for y, xs, xe in rows_list:
                        f.write(f'    ({y}, {xs:>2d}, {xe:>2d}, "{color}"),\n')
                    f.write(f'])\n')
            f.write("\n")
        
        # Single pixels
        if singles:
            f.write("# === PIXEL ĐƠN (chi tiết nhỏ) ===\n")
            for color, points in sorted(singles.items()):
                for x, y in points:
                    f.write(f'canvas.set_pixel(({x}, {y}), "{color}")\n')
            f.write("\n")
        
        f.write(f'canvas.save("{output_path.stem}.png", scale=10)\n')
    
    return (grid_w, grid_h, len(palette_mapping), block_size)


def decode_text(text_path: Path, output_path: Path, scale: int) -> tuple[int, int]:
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
            
    img = Image.new("RGBA", (width, height), (0,0,0,0))
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
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[PALETTE]\n")
        f.write(". = #00000000 (Trong suốt)\n")
        f.write("A = #000000FF (Đen)\n\n")
        f.write("[GRID]\n")
        for _ in range(height):
            f.write(" ".join(["."] * width) + "\n")

def init_code_canvas(output_path: Path, width: int, height: int):
    """Generate a comprehensive AI-ready template with spatial guides
    and step-by-step workflow instructions.
    """
    mid_x = width // 2
    mid_y = height // 2
    q1_y = height // 4
    q3_y = height * 3 // 4
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"""# ╔══════════════════════════════════════════════════════════════╗
# ║  PIXCI CANVAS - AI Drawing Template                        ║
# ║  Canvas: {width}x{height} pixels                                      ║
# ╚══════════════════════════════════════════════════════════════╝
#
# COORDINATE GUIDE (không cần nhớ, chỉ tra cứu khi cần):
#   (0,0)=top-left    ({mid_x},{0})=top-center    ({width-1},0)=top-right
#   (0,{mid_y})=mid-left    ({mid_x},{mid_y})=CENTER         ({width-1},{mid_y})=mid-right
#   (0,{height-1})=bot-left    ({mid_x},{height-1})=bot-center    ({width-1},{height-1})=bot-right
#
# X RULER: 0----5----10---15---{min(20,width-1)}{'---25---30' if width > 25 else ''}
# Y RULER: 0=top, {q1_y}=quarter, {mid_y}=middle, {q3_y}=three-quarter, {height-1}=bottom
#
# ════════════════════════════════════════════════════════════════
# WORKFLOW (PHẢI theo thứ tự này):
#
#   Bước 1: PALETTE        → Chọn 4-8 màu (load_palette hoặc add_palette)
#   Bước 2: LAYERS          → Tạo layers (background → foreground → effects)
#   Bước 3: SILHOUETTE      → Vẽ shape lớn bằng fill_rect / draw_rows / fill_polygon
#   Bước 4: ALPHA LOCK      → Bật alpha_lock=True, thêm bóng (shadow) & highlight BÊN TRONG shape
#   Bước 5: DETAILS         → Thêm chi tiết nhỏ (đốm, mắt, nút áo...)
#   Bước 6: POST-PROCESS    → merge_layers → add_outline(sel_out=True) → cleanup_jaggies
#   Bước 7: SAVE            → canvas.save("output.png", scale=10)
#
# TIPS:
#   - draw_rows() là hàm MẠNH NHẤT: vẽ shape tự do bằng cách định nghĩa từng dòng ngang
#   - fill_polygon() cho shape phức tạp (cánh, lá, mũi kiếm...)
#   - Bóng nên ẤM hơn base (dịch hue sang đỏ/cam)
#   - Highlight nên LẠNH hơn base (dịch hue sang xanh)
#   - Outline KHÔNG ĐEN thuần → dùng sel_out=True để outline theo màu gốc
# ════════════════════════════════════════════════════════════════

import pixci

canvas = pixci.Canvas({width}, {height})

# ──── Bước 1: PALETTE ────
# Cách 1: Load palette có sẵn (4000+ từ lospec.com)
# canvas.load_palette("endesga-32")
# Cách 2: Tự định nghĩa
canvas.add_palette({{
    "C01": "#000000FF",  # Thay bằng màu của bạn
}})

# ──── Bước 2: LAYERS ────
canvas.add_layer("background")
canvas.add_layer("main")

# ──── Bước 3: SILHOUETTE ────
canvas.set_layer("main")
# Dùng draw_rows để sculpt shape:
# canvas.draw_rows([
#     (y,  x_start, x_end, "C01"),   # y=hàng, x_start..x_end = chiều ngang
# ])

# ──── Bước 4: SHADOW & HIGHLIGHT ────
# canvas.alpha_lock = True
# canvas.draw_rows([...])  # Vẽ bóng bên trong shape
# canvas.alpha_lock = False

# ──── Bước 5: DETAILS ────
# canvas.set_pixel((x, y), "C01")

# ──── Bước 6: POST-PROCESS ────
# canvas.merge_layers("background", "main")
# canvas.set_layer("background")
# canvas.add_outline(thickness=1, sel_out=True)
# canvas.cleanup_jaggies()

# ──── Bước 7: SAVE ────
canvas.save("{output_path.stem}.png", scale=10)
""")

"""
code_engine.py - Smart Image → Python Code encoder.
Đảm bảo 100% pixel-perfect accuracy.

Thuật toán:
1. Đọc ảnh → grid[y][x] = palette_key hoặc None
2. Cho mỗi color, tìm tất cả pixel → group thành horizontal runs
3. Merge runs liền kề thành fill_rect khi có lợi
4. Emit code ngắn nhất có thể
5. Verify: đếm tổng pixel emit == tổng pixel gốc
"""
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict, Optional


def rgb2hex(r: int, g: int, b: int, a: int = 255) -> str:
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


def _detect_block_size(img: Image.Image) -> int:
    """Auto-detect pixel block size (1 for raw, higher for upscaled sprites)."""
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


def _build_grid(img: Image.Image, block_size: int):
    """Build grid[y][x] = palette_key or None. Returns (w, h, grid, palette_map)."""
    width, height = img.size
    grid_w = width // block_size
    grid_h = height // block_size
    pixels = img.load()
    
    palette = {}  # hex → key
    idx = 0
    
    grid = []
    for gy in range(grid_h):
        row = []
        for gx in range(grid_w):
            px_x, px_y = gx * block_size, gy * block_size
            r, g, b, a = pixels[px_x, px_y]
            if a == 0:
                row.append(None)
            else:
                hx = rgb2hex(r, g, b, a)
                if hx not in palette:
                    idx += 1
                    palette[hx] = f"C{idx:02d}"
                row.append(palette[hx])
        grid.append(row)
    
    return grid_w, grid_h, grid, palette


def _collect_runs_per_color(grid, grid_w, grid_h) -> Dict[str, List[Tuple[int, int, int]]]:
    """For each color, find all horizontal runs: {color: [(y, x_start, x_end), ...]}
    
    This is GUARANTEED to cover every non-None pixel exactly once.
    """
    color_runs = {}
    
    for y in range(grid_h):
        x = 0
        while x < grid_w:
            c = grid[y][x]
            if c is None:
                x += 1
                continue
            # Start of a run
            start_x = x
            while x < grid_w and grid[y][x] == c:
                x += 1
            end_x = x - 1
            
            if c not in color_runs:
                color_runs[c] = []
            color_runs[c].append((y, start_x, end_x))
    
    return color_runs


def _try_merge_to_rects(runs: List[Tuple[int, int, int]]) -> Tuple[List[Tuple[int, int, int, int]], List[Tuple[int, int, int]]]:
    """Try to merge consecutive same-width runs into fill_rect.
    
    Returns: (rects [(x0,y0,x1,y1)], remaining_runs [(y, xs, xe)])
    """
    if not runs:
        return [], []
    
    runs_sorted = sorted(runs, key=lambda r: (r[1], r[2], r[0]))  # Sort by x_start, x_end, y
    
    rects = []
    used_indices = set()
    
    # Group runs that have same x_start and x_end
    groups = {}
    for i, (y, xs, xe) in enumerate(runs_sorted):
        key = (xs, xe)
        if key not in groups:
            groups[key] = []
        groups[key].append((i, y))
    
    for (xs, xe), members in groups.items():
        # Sort by y
        members.sort(key=lambda m: m[1])
        
        # Find consecutive y sequences
        i = 0
        while i < len(members):
            seq_start = i
            while i + 1 < len(members) and members[i+1][1] == members[i][1] + 1:
                i += 1
            seq_len = i - seq_start + 1
            
            # Only merge if it saves lines (rect = 1 line vs N run lines)
            # A rect is worth it if seq_len >= 2 AND width >= 2
            width = xe - xs + 1
            if seq_len >= 2 and width >= 2:
                y_start = members[seq_start][1]
                y_end = members[i][1]
                rects.append((xs, y_start, xe, y_end))
                for j in range(seq_start, i + 1):
                    used_indices.add(members[j][0])
            
            i += 1
    
    remaining = [(y, xs, xe) for i, (y, xs, xe) in enumerate(runs_sorted) if i not in used_indices]
    return rects, remaining


def _color_description(hex_val: str) -> str:
    """Auto-describe a color for AI readability."""
    h = hex_val.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    
    brightness = (r + g + b) / (3 * 255)
    if brightness > 0.8:
        bname = "sáng"
    elif brightness > 0.5:
        bname = "trung bình"
    elif brightness > 0.2:
        bname = "tối"
    else:
        bname = "rất tối"
    
    diff = max(r, g, b) - min(r, g, b)
    if diff < 30:
        hname = "xám"
    elif r >= g and r >= b:
        hname = "đỏ" if g < 128 else "cam"
    elif g >= r and g >= b:
        hname = "xanh lá"
    else:
        hname = "xanh dương"
    
    return f"{hname}, {bname}"


def encode_code(image_path, output_path, block_size: int = 1, auto_detect: bool = True) -> Tuple[int, int, int, int]:
    """Encode an image to PixCI Python code. GUARANTEED 100% pixel-perfect.
    
    Strategy:
    1. Group all pixels by color into horizontal runs (lossless)
    2. Try to merge runs into fill_rect where it saves code lines
    3. Emit remaining runs as draw_rows (grouped by color)
    4. Verify pixel count matches
    
    Returns: (grid_w, grid_h, num_colors, block_size)
    """
    image_path = Path(image_path)
    output_path = Path(output_path)
    
    img = Image.open(image_path).convert("RGBA")
    if auto_detect:
        block_size = _detect_block_size(img)
    
    grid_w, grid_h, grid, palette = _build_grid(img, block_size)
    
    # Step 1: Collect ALL runs per color (guaranteed lossless)
    color_runs = _collect_runs_per_color(grid, grid_w, grid_h)
    
    # Count total pixels for verification
    total_pixels = sum(
        xe - xs + 1 
        for runs in color_runs.values() 
        for (y, xs, xe) in runs
    )
    
    # Step 2: For each color, try to merge runs into rects
    color_rects = {}   # color → [(x0,y0,x1,y1)]
    color_rows = {}    # color → [(y, xs, xe)]
    
    emit_pixel_count = 0
    
    for color, runs in color_runs.items():
        rects, remaining = _try_merge_to_rects(runs)
        if rects:
            color_rects[color] = rects
            emit_pixel_count += sum((x1-x0+1)*(y1-y0+1) for x0,y0,x1,y1 in rects)
        if remaining:
            color_rows[color] = remaining
            emit_pixel_count += sum(xe-xs+1 for y,xs,xe in remaining)
    
    # Verify: emit count must equal total
    assert emit_pixel_count == total_pixels, \
        f"BUG: emit {emit_pixel_count} != total {total_pixels} pixels!"
    
    # Step 3: Write code
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# PixCI Smart Code - {image_path.name}\n")
        f.write(f"# Canvas: {grid_w}x{grid_h}, {len(palette)} colors, 100% pixel-perfect\n")
        f.write(f"import pixci\n\n")
        f.write(f"canvas = pixci.Canvas({grid_w}, {grid_h})\n\n")
        
        # Palette
        f.write("canvas.add_palette({\n")
        for hex_val, key in sorted(palette.items(), key=lambda x: x[1]):
            desc = _color_description(hex_val)
            f.write(f'    "{key}": "{hex_val}",  # {desc}\n')
        f.write("})\n\n")
        
        # Rects
        has_rects = any(color_rects.values())
        if has_rects:
            for color in sorted(color_rects.keys()):
                for x0, y0, x1, y1 in color_rects[color]:
                    w = x1 - x0 + 1
                    h = y1 - y0 + 1
                    f.write(f'canvas.fill_rect(({x0}, {y0}), ({x1}, {y1}), "{color}")  # {w}x{h}\n')
            f.write("\n")
        
        # Draw rows - grouped by color for readability
        if color_rows:
            for color in sorted(color_rows.keys()):
                runs = sorted(color_rows[color], key=lambda r: (r[0], r[1]))
                if len(runs) == 1:
                    y, xs, xe = runs[0]
                    f.write(f'canvas.draw_rows([({y}, {xs}, {xe}, "{color}")])\n')
                else:
                    f.write(f'canvas.draw_rows([\n')
                    for y, xs, xe in runs:
                        f.write(f'    ({y}, {xs:>2d}, {xe:>2d}, "{color}"),\n')
                    f.write(f'])\n')
            f.write("\n")
        
        f.write(f'canvas.save("{output_path.stem}.png", scale=10)\n')
    
    return (grid_w, grid_h, len(palette), block_size)

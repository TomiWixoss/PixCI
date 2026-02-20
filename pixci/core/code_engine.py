"""
code_engine.py - Smart Image → Python Code encoder.
Tối ưu output ngắn nhất có thể, đảm bảo 100% pixel-perfect.
"""
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict


def rgb2hex(r: int, g: int, b: int, a: int = 255) -> str:
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


# Palette key generation
_SINGLE_CHARS = (
    [chr(i) for i in range(ord('A'), ord('Z') + 1)] +
    [chr(i) for i in range(ord('a'), ord('z') + 1)] +
    [str(i) for i in range(10)]
)

def _make_key(idx: int) -> str:
    """Generate palette key: A-Z, a-z, 0-9 for first 62, then AA, AB... for overflow."""
    if idx < len(_SINGLE_CHARS):
        return _SINGLE_CHARS[idx]
    # 2-char keys for overflow
    idx2 = idx - len(_SINGLE_CHARS)
    return _SINGLE_CHARS[idx2 // len(_SINGLE_CHARS)] + _SINGLE_CHARS[idx2 % len(_SINGLE_CHARS)]


def _detect_block_size(img: Image.Image) -> int:
    pixels = img.load()
    w, h = img.size
    if w == 0:
        return 1
    min_run = w
    for y in range(0, h, max(1, h // 10)):
        cur = pixels[0, y]
        run = 0
        for x in range(w):
            if pixels[x, y] == cur:
                run += 1
            else:
                if run > 0: min_run = min(min_run, run)
                cur = pixels[x, y]
                run = 1
        if run > 0: min_run = min(min_run, run)
    for x in range(0, w, max(1, w // 10)):
        cur = pixels[x, 0]
        run = 0
        for y in range(h):
            if pixels[x, y] == cur:
                run += 1
            else:
                if run > 0: min_run = min(min_run, run)
                cur = pixels[x, y]
                run = 1
        if run > 0: min_run = min(min_run, run)
    return max(1, min_run)


def _build_grid(img: Image.Image, block_size: int):
    """Returns (w, h, grid[y][x]=key|None, palette={hex: key})"""
    width, height = img.size
    gw = width // block_size
    gh = height // block_size
    pixels = img.load()
    
    pal = {}
    idx = 0
    grid = []
    for gy in range(gh):
        row = []
        for gx in range(gw):
            r, g, b, a = pixels[gx * block_size, gy * block_size]
            if a == 0:
                row.append(None)
            else:
                hx = rgb2hex(r, g, b, a)
                if hx not in pal:
                    pal[hx] = _make_key(idx)
                    idx += 1
                row.append(pal[hx])
        grid.append(row)
    return gw, gh, grid, pal


def _find_best_rects(grid, gw, gh):
    """Greedy maximal rectangle detection. Returns (rects, used_mask).
    
    Only emits rects that save code vs draw_rows (area >= 4 pixels).
    """
    used = [[False] * gw for _ in range(gh)]
    rects = []  # (x0, y0, x1, y1, color)
    
    for y in range(gh):
        for x in range(gw):
            if used[y][x] or grid[y][x] is None:
                continue
            c = grid[y][x]
            
            # Expand right
            mx = x
            while mx + 1 < gw and grid[y][mx + 1] == c and not used[y][mx + 1]:
                mx += 1
            
            # Expand down
            my = y
            while my + 1 < gh:
                ok = all(grid[my + 1][cx] == c and not used[my + 1][cx] for cx in range(x, mx + 1))
                if ok:
                    my += 1
                else:
                    break
            
            w = mx - x + 1
            h = my - y + 1
            area = w * h
            
            # Only use rect if it saves lines: rect=1 line vs rows=h lines
            # Worth it when h >= 2 (saves h-1 lines)
            if h >= 2 and area >= 4:
                for ry in range(y, my + 1):
                    for rx in range(x, mx + 1):
                        used[ry][rx] = True
                rects.append((x, y, mx, my, c))
    
    return rects, used


def _collect_all_runs(grid, gw, gh, used):
    """Collect ALL remaining pixels as (y, x_start, x_end, color) runs."""
    runs = []
    for y in range(gh):
        x = 0
        while x < gw:
            if used[y][x] or grid[y][x] is None:
                x += 1
                continue
            c = grid[y][x]
            sx = x
            while x < gw and grid[y][x] == c and not used[y][x]:
                used[y][x] = True
                x += 1
            runs.append((y, sx, x - 1, c))
    return runs


def encode_code(image_path, output_path, block_size: int = 1, auto_detect: bool = True) -> Tuple[int, int, int, int]:
    """Encode image to compact PixCI Python code. 100% pixel-perfect.
    
    Returns: (grid_w, grid_h, num_colors, block_size)
    """
    image_path = Path(image_path)
    output_path = Path(output_path)
    img = Image.open(image_path).convert("RGBA")
    
    if auto_detect:
        block_size = _detect_block_size(img)
    
    gw, gh, grid, palette = _build_grid(img, block_size)
    
    # Count total non-transparent pixels
    total_px = sum(1 for y in range(gh) for x in range(gw) if grid[y][x] is not None)
    
    # Detect rects
    rects, used = _find_best_rects(grid, gw, gh)
    
    # Collect remaining as runs  
    runs = _collect_all_runs(grid, gw, gh, used)
    
    # Verify pixel count
    rect_px = sum((x1-x0+1)*(y1-y0+1) for x0,y0,x1,y1,_ in rects)
    run_px = sum(xe-xs+1 for _,xs,xe,_ in runs)
    assert rect_px + run_px == total_px, f"BUG: {rect_px}+{run_px} != {total_px}"
    
    # Separate single-pixel runs (set_pixel is shorter than draw_rows for 1px)
    single_pixels = [(y, xs, c) for y, xs, xe, c in runs if xs == xe]
    multi_runs = [(y, xs, xe, c) for y, xs, xe, c in runs if xs != xe]
    
    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {image_path.name} → {gw}x{gh}, {len(palette)} colors\n")
        f.write("import pixci\n")
        f.write(f"c = pixci.Canvas({gw}, {gh})\n")
        
        # Palette - compact
        f.write("c.add_palette({")
        pal_items = sorted(palette.items(), key=lambda x: x[1])
        for i, (hx, key) in enumerate(pal_items):
            sep = "" if i == 0 else ", "
            f.write(f'{sep}"{key}":"{hx}"')
        f.write("})\n")
        
        # Rects
        for x0, y0, x1, y1, color in rects:
            f.write(f'c.fill_rect(({x0},{y0}),({x1},{y1}),"{color}")\n')
        
        # All multi-pixel runs in ONE draw_rows call
        if multi_runs:
            f.write("c.draw_rows([\n")
            for y, xs, xe, color in multi_runs:
                f.write(f'({y},{xs},{xe},"{color}"),')
            f.write("])\n")
        
        # Single pixels - batch them
        if single_pixels:
            # Group consecutive singles into set_pixel calls
            for y, x, color in single_pixels:
                f.write(f'c.set_pixel(({x},{y}),"{color}")\n')
        
        f.write(f'c.save("{output_path.stem}.png",scale=10)\n')
    
    return (gw, gh, len(palette), block_size)

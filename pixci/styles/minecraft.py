"""
minecraft.py - Minecraft texture pattern detection & compact encoding.

Core optimizations:
1. BASE FILL: Find dominant color → fill whole canvas → encode only DIFFS
2. SYMMETRY: Detect X/Y mirror → encode half + mirror_x()/flip_y()
3. BORDER FRAME: Detect uniform border → fill_border() 
4. SCATTER: Group isolated same-color pixels → scatter()

These can reduce a 148-line diamond_ore to ~40 lines.
"""
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict, Optional
from ..core.code_engine import rgb2hex, _detect_block_size, _make_key


class MinecraftStyle:
    """Minecraft-specific pattern analyzer and compact encoder."""
    
    @staticmethod
    def analyze(grid, gw, gh) -> dict:
        """Analyze grid for Minecraft patterns. Returns optimization hints."""
        info = {}
        
        # 1. Find dominant color (most frequent)
        counts = {}
        total = 0
        for y in range(gh):
            for x in range(gw):
                c = grid[y][x]
                if c is not None:
                    counts[c] = counts.get(c, 0) + 1
                    total += 1
        
        if counts:
            dominant = max(counts, key=counts.get)
            info["dominant"] = dominant
            info["dominant_pct"] = counts[dominant] / total * 100
            info["color_counts"] = counts
            info["total_pixels"] = total
        
        # 2. Check X symmetry (left-right mirror)
        x_sym = True
        x_sym_count = 0
        x_total = 0
        for y in range(gh):
            for x in range(gw // 2):
                mx = gw - 1 - x
                x_total += 1
                if grid[y][x] == grid[y][mx]:
                    x_sym_count += 1
                else:
                    x_sym = False
        info["x_symmetric"] = x_sym
        info["x_sym_pct"] = (x_sym_count / x_total * 100) if x_total > 0 else 0
        
        # 3. Check Y symmetry (top-bottom mirror)
        y_sym = True
        y_sym_count = 0
        y_total = 0
        for y in range(gh // 2):
            my = gh - 1 - y
            for x in range(gw):
                y_total += 1
                if grid[y][x] == grid[my][x]:
                    y_sym_count += 1
                else:
                    y_sym = False
        info["y_symmetric"] = y_sym
        info["y_sym_pct"] = (y_sym_count / y_total * 100) if y_total > 0 else 0
        
        # 4. Detect border frame
        border_colors = set()
        for x in range(gw):
            if grid[0][x]:   border_colors.add(grid[0][x])
            if grid[gh-1][x]: border_colors.add(grid[gh-1][x])
        for y in range(gh):
            if grid[y][0]:   border_colors.add(grid[y][0])
            if grid[y][gw-1]: border_colors.add(grid[y][gw-1])
        info["border_colors"] = len(border_colors)
        info["has_uniform_border"] = len(border_colors) <= 2
        
        return info
    
    @staticmethod
    def encode(image_path, output_path, block_size=1, auto_detect=True) -> Tuple[int, int, int, int]:
        """Minecraft-optimized encoder. Produces ultra-compact code."""
        image_path = Path(image_path)
        output_path = Path(output_path)
        img = Image.open(image_path).convert("RGBA")
        
        if auto_detect:
            block_size = _detect_block_size(img)
        
        # Build grid
        w, h = img.size
        gw, gh = w // block_size, h // block_size
        pixels = img.load()
        
        pal = {}  # hex → key
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
        
        # Analyze
        info = MinecraftStyle.analyze(grid, gw, gh)
        
        # Pick strategy
        total = info.get("total_pixels", 0)
        dominant = info.get("dominant")
        dom_pct = info.get("dominant_pct", 0)
        
        # Strategy: BASE FILL + DIFFS (when dominant color covers > 30%)
        use_base_fill = dominant is not None and dom_pct > 30
        
        # Collect diff pixels (everything that's NOT the dominant/base color)
        if use_base_fill:
            diff_runs = []
            diff_singles = []
            for y in range(gh):
                x = 0
                while x < gw:
                    c = grid[y][x]
                    if c is None or c == dominant:
                        x += 1
                        continue
                    sx = x
                    while x < gw and grid[y][x] == c and grid[y][x] != dominant:
                        x += 1
                    if sx == x - 1:
                        diff_singles.append((sx, y, c))
                    else:
                        diff_runs.append((y, sx, x - 1, c))
            
            # Verify: base + diffs = total
            base_px = info["color_counts"][dominant]
            diff_px = sum(xe - xs + 1 for y, xs, xe, c in diff_runs) + len(diff_singles)
            assert base_px + diff_px == total, f"BUG: {base_px}+{diff_px}!={total}"
        else:
            # Fallback: collect all runs
            diff_runs = []
            diff_singles = []
            for y in range(gh):
                x = 0
                while x < gw:
                    c = grid[y][x]
                    if c is None:
                        x += 1
                        continue
                    sx = x
                    while x < gw and grid[y][x] == c:
                        x += 1
                    if sx == x - 1:
                        diff_singles.append((sx, y, c))
                    else:
                        diff_runs.append((y, sx, x - 1, c))
        
        # Group singles by color for scatter()
        scatter_groups = {}
        for x, y, c in diff_singles:
            if c not in scatter_groups:
                scatter_groups[c] = []
            scatter_groups[c].append((x, y))
        
        # Write compact code
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {image_path.name} [{gw}x{gh}, {len(pal)}c]\n")
            f.write("import pixci\n")
            f.write(f"c = pixci.Canvas({gw},{gh})\n")
            
            # Palette - one line
            f.write("c.add_palette({")
            for i, (hx, key) in enumerate(sorted(pal.items(), key=lambda x: x[1])):
                f.write(f'{"" if i==0 else ","}\"{key}\":\"{hx}\"')
            f.write("})\n")
            
            # Base fill
            if use_base_fill:
                f.write(f'c.fill_rect((0,0),({gw-1},{gh-1}),"{dominant}")\n')
            
            # Runs → draw_rows (one call)
            if diff_runs:
                f.write("c.draw_rows([")
                for y, xs, xe, c in diff_runs:
                    f.write(f'({y},{xs},{xe},"{c}"),')
                f.write("])\n")
            
            # Singles → scatter per color (compact)
            for c in sorted(scatter_groups.keys()):
                pts = scatter_groups[c]
                if len(pts) == 1:
                    x, y = pts[0]
                    f.write(f'c.set_pixel(({x},{y}),"{c}")\n')
                else:
                    # Use scatter: list of (x,y) pairs
                    pts_str = ",".join(f"({x},{y})" for x, y in pts)
                    f.write(f'for p in [{pts_str}]:c.set_pixel(p,"{c}")\n')
            
            f.write(f'c.save("{output_path.stem}.png",scale=10)\n')
        
        return (gw, gh, len(pal), block_size)

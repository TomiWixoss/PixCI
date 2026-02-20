"""
minecraft.py - Minecraft texture pattern detection & ultra-compact encoding.

Mathematical optimizations used:
1. SYMMETRY: Detect X/Y mirror. If symmetric, only encode the minimum unique quadrant/half.
2. BASE FILL: Detect dominant color. Fill canvas, then only encode differences.
3. VECTORIZED EMIT: Combine ALL remaining diff runs AND single pixels into a single 
   `c.draw_rows` payload to completely eliminate loop/function-call overhead.
"""
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict, Any
from ..core.code_engine import rgb2hex, _detect_block_size, _make_key


class MinecraftStyle:
    """Minecraft-specific pattern analyzer and ultra-compact encoder."""
    
    @staticmethod
    def analyze(grid: List[List[Any]], gw: int, gh: int) -> dict:
        info = {}
        
        # 1. Color counts & Dominic color
        counts = {}
        total = 0
        for y in range(gh):
            for x in range(gw):
                c = grid[y][x]
                counts[c] = counts.get(c, 0) + 1
                total += 1
        
        if counts:
            dominant = max(counts, key=counts.get)
            info["dominant"] = dominant
            info["dominant_pct"] = counts[dominant] / total * 100
            info["color_counts"] = counts
            info["total_pixels"] = total
        else:
            info["dominant"] = None
        
        # 2. X Symmetry (Left == Right mirrored)
        x_sym = True
        for y in range(gh):
            for x in range(gw // 2):
                if grid[y][x] != grid[y][gw - 1 - x]:
                    x_sym = False
                    break
            if not x_sym:
                break
        info["x_symmetric"] = x_sym
        
        # 3. Y Symmetry (Top == Bottom mirrored)
        y_sym = True
        for x in range(gw):
            for y in range(gh // 2):
                if grid[y][x] != grid[gh - 1 - y][x]:
                    y_sym = False
                    break
            if not y_sym:
                break
        info["y_symmetric"] = y_sym
        
        return info
    
    @staticmethod
    def encode(image_path, output_path, block_size=1, auto_detect=True) -> Tuple[int, int, int, int]:
        image_path = Path(image_path)
        output_path = Path(output_path)
        img = Image.open(image_path).convert("RGBA")
        
        if auto_detect:
            block_size = _detect_block_size(img)
        
        w, h = img.size
        gw, gh = w // block_size, h // block_size
        pixels = img.load()
        
        pal = {}
        idx = 0
        grid = []
        for gy in range(gh):
            row = []
            for gx in range(gw):
                r, g, b, a = pixels[gx * block_size, gy * block_size]
                hx = rgb2hex(r, g, b, a)
                if hx not in pal:
                    pal[hx] = _make_key(idx)
                    idx += 1
                row.append(pal[hx])
            grid.append(row)
        
        info = MinecraftStyle.analyze(grid, gw, gh)
        
        # Determine encoded area bounds based on symmetry
        max_y = ((gh + 1) // 2) if info.get("y_symmetric") else gh
        max_x = ((gw + 1) // 2) if info.get("x_symmetric") else gw
        
        dominant = info.get("dominant")
        dom_pct = info.get("dominant_pct", 0)
        use_base_fill = dominant is not None and dom_pct > 25
        
        # Extract runs only within the target bounds
        diff_runs = []
        for y in range(max_y):
            x = 0
            while x < max_x:
                c = grid[y][x]
                # If using base fill, skip dominant color
                if (use_base_fill and c == dominant):
                    x += 1
                    continue
                sx = x
                while x < max_x and grid[y][x] == c and (not use_base_fill or grid[y][x] != dominant):
                    x += 1
                diff_runs.append((y, sx, x - 1, c))
        
        # Write extreme compact code
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# {image_path.name} [{gw}x{gh}, {len(pal)}c, sym_x={info.get('x_symmetric')}, sym_y={info.get('y_symmetric')}]\n")
            f.write("import pixci\n")
            f.write(f"c=pixci.Canvas({gw},{gh})\n")
            
            # Palette
            f.write("c.add_palette({")
            for i, (hx, key) in enumerate(sorted(pal.items(), key=lambda x: x[1])):
                f.write(f'{"" if i==0 else ","}"{key}":"{hx}"')
            f.write("})\n")
            
            # Base Fill
            if use_base_fill:
                f.write(f'c.fill_rect((0,0),({gw-1},{gh-1}),"{dominant}")\n')
            
            # Master draw_rows containing everything
            if diff_runs:
                # Group by color for slight compression if it was needed, but
                # packing all into one list actually saves more lines/bytes
                f.write("c.draw_rows([")
                for i, (y, xs, xe, c) in enumerate(diff_runs):
                    f.write(f'({y},{xs},{xe},"{c}"),')
                f.write("])\n")
            
            # Apply symmetries
            if info.get("x_symmetric"):
                f.write("c.mirror_x()\n")
            if info.get("y_symmetric"):
                f.write("c.mirror_y()\n")
                
            f.write(f'c.save("{output_path.stem}.png",scale=10)\n')
        
        return (gw, gh, len(pal), block_size)

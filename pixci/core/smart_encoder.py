"""
smart_encoder.py - Ultra-optimized PXVG encoder
Sử dụng scikit-image, opencv, scipy để phát hiện shapes tối ưu nhất
"""
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict
from skimage import morphology, measure
from skimage.morphology import convex_hull_image
from scipy import ndimage


def _merge_consecutive_rows_to_rects(multi_runs):
    """Gộp rows liên tiếp thành rects."""
    if not multi_runs:
        return [], []
    
    sorted_runs = sorted(multi_runs, key=lambda r: (r[3], r[1], r[2], r[0]))
    new_rects, remaining_rows = [], []
    
    i = 0
    while i < len(sorted_runs):
        y, x1, x2, color = sorted_runs[i]
        consecutive = [sorted_runs[i]]
        j = i + 1
        
        while j < len(sorted_runs):
            ny, nx1, nx2, nc = sorted_runs[j]
            if nc == color and nx1 == x1 and nx2 == x2 and ny == consecutive[-1][0] + 1:
                consecutive.append(sorted_runs[j])
                j += 1
            else:
                break
        
        if len(consecutive) >= 3:
            y_start, y_end = consecutive[0][0], consecutive[-1][0]
            w, h = x2 - x1 + 1, y_end - y_start + 1
            new_rects.append((x1, y_start, x1 + w - 1, y_end, color))
            i = j
        else:
            remaining_rows.extend(consecutive)
            i = j
    
    return new_rects, remaining_rows


def _collect_columns(grid, gw, gh, used):
    """Thu thập cột dọc."""
    columns = []
    
    for x in range(gw):
        y = 0
        while y < gh:
            if used[y][x] or grid[y][x] is None:
                y += 1
                continue
            
            c, sy = grid[y][x], y
            while y < gh and grid[y][x] == c and not used[y][x]:
                used[y][x] = True
                y += 1
            
            if y - sy >= 3:
                columns.append((x, sy, y - 1, c))
            else:
                for ry in range(sy, y):
                    used[ry][x] = False
                y = sy + 1
    
    return columns


def _find_contours_for_color(grid, gw, gh, color):
    """Tìm contours cho một màu."""
    mask = np.zeros((gh, gw), dtype=np.uint8)
    for y in range(gh):
        for x in range(gw):
            if grid[y][x] == color:
                mask[y, x] = 255
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, mask


def _analyze_shape(contour, mask):
    """Phân tích shape và trả về loại tối ưu nhất."""
    area = cv2.contourArea(contour)
    if area < 4:
        return None
    
    perimeter = cv2.arcLength(contour, True)
    if perimeter == 0:
        return None
    
    # 1. Kiểm tra Circle
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if circularity > 0.7:
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if 1.5 <= radius <= 50:
            return ('circle', int(x), int(y), int(radius))
    
    # 2. Kiểm tra Rectangle
    x, y, w, h = cv2.boundingRect(contour)
    rect_area = w * h
    if rect_area > 0 and area / rect_area > 0.8 and w >= 2 and h >= 2:
        return ('rect', x, y, w, h)
    
    # 3. Kiểm tra Ellipse
    if len(contour) >= 5:
        try:
            (cx, cy), (ew, eh), angle = cv2.fitEllipse(contour)
            ellipse_area = np.pi * (ew/2) * (eh/2)
            if ellipse_area > 0 and 0.7 < area / ellipse_area < 1.3:
                if ew >= 3 and eh >= 3:
                    return ('ellipse', int(cx), int(cy), max(1, int(ew/2)), max(1, int(eh/2)))
        except:
            pass
    
    # 4. Polygon approximation
    epsilon = 0.04 * perimeter
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    if 3 <= len(approx) <= 8 and area >= 4:
        points = [(int(pt[0][0]), int(pt[0][1])) for pt in approx]
        return ('polygon', points)
    
    return None


def smart_encode_pxvg(image_path: Path, output_path: Path, block_size: int = 1, auto_detect: bool = True) -> Tuple[int, int, int, int]:
    """
    Ultra-optimized PXVG encoder using scikit-image + opencv.
    Tự động phát hiện shapes tối ưu nhất.
    """
    from .code_engine import _detect_block_size, _build_grid, _find_best_rects, _collect_all_runs
    
    image_path = Path(image_path)
    output_path = Path(output_path)
    img = Image.open(image_path).convert("RGBA")
    
    if auto_detect:
        block_size = _detect_block_size(img)
    
    gw, gh, grid, palette = _build_grid(img, block_size)
    used = [[False] * gw for _ in range(gh)]
    
    # Lưu shapes phát hiện được
    shapes = []
    
    # Xử lý từng màu với computer vision
    for hex_color, color_key in sorted(palette.items(), key=lambda x: x[1]):
        contours, mask = _find_contours_for_color(grid, gw, gh, color_key)
        
        for contour in contours:
            shape_info = _analyze_shape(contour, mask)
            
            if shape_info is None:
                continue
            
            shape_type = shape_info[0]
            
            if shape_type == 'circle':
                _, cx, cy, r = shape_info
                shapes.append(('circle', cx, cy, r, color_key))
                # Đánh dấu pixels
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx*dx + dy*dy <= r*r:
                            x, y = cx + dx, cy + dy
                            if 0 <= x < gw and 0 <= y < gh and grid[y][x] == color_key:
                                used[y][x] = True
            
            elif shape_type == 'rect':
                _, x, y, w, h = shape_info
                shapes.append(('rect', x, y, w, h, color_key))
                for dy in range(h):
                    for dx in range(w):
                        if 0 <= x+dx < gw and 0 <= y+dy < gh and grid[y+dy][x+dx] == color_key:
                            used[y+dy][x+dx] = True
            
            elif shape_type == 'ellipse':
                _, cx, cy, rx, ry = shape_info
                shapes.append(('ellipse', cx, cy, rx, ry, color_key))
                for dy in range(-ry, ry + 1):
                    for dx in range(-rx, rx + 1):
                        if rx > 0 and ry > 0 and (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) <= 1:
                            x, y = cx + dx, cy + dy
                            if 0 <= x < gw and 0 <= y < gh and grid[y][x] == color_key:
                                used[y][x] = True
            
            elif shape_type == 'polygon':
                _, points = shape_info
                shapes.append(('polygon', points, color_key))
                # Đánh dấu pixels trong polygon
                poly_mask = np.zeros((gh, gw), dtype=np.uint8)
                pts = np.array(points, dtype=np.int32)
                cv2.fillPoly(poly_mask, [pts], 255)
                for y in range(gh):
                    for x in range(gw):
                        if poly_mask[y, x] > 0 and grid[y][x] == color_key:
                            used[y][x] = True
    
    # Thu thập pixels còn lại
    rects, used = _find_best_rects(grid, gw, gh)
    runs = _collect_all_runs(grid, gw, gh, used)
    
    single_pixels = [(y, xs, c) for y, xs, xe, c in runs if xs == xe]
    multi_runs = [(y, xs, xe, c) for y, xs, xe, c in runs if xs != xe]
    
    extra_rects, optimized_rows = _merge_consecutive_rows_to_rects(multi_runs)
    all_rects = rects + extra_rects
    
    # Columns
    for y, x, _ in single_pixels:
        used[y][x] = False
    columns = _collect_columns(grid, gw, gh, used)
    
    # Dots còn lại
    final_dots = [(y, x, c) for y, x, c in single_pixels if not used[y][x]]
    
    # Ghi file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(f'<pxvg w="{gw}" h="{gh}" xmlns="http://pixci.dev/pxvg">\n')
        
        f.write('  <palette>\n')
        for hx, key in sorted(palette.items(), key=lambda x: x[1]):
            f.write(f'    <color k="{key}" hex="{hx}" />\n')
        f.write('  </palette>\n')
        
        f.write('  <layer id="main">\n')
        
        # Shapes phát hiện được
        for shape in shapes:
            if shape[0] == 'circle':
                _, cx, cy, r, color = shape
                f.write(f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="true" c="{color}" />\n')
            elif shape[0] == 'ellipse':
                _, cx, cy, rx, ry, color = shape
                f.write(f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="true" c="{color}" />\n')
            elif shape[0] == 'rect':
                _, x, y, w, h, color = shape
                f.write(f'    <rect x="{x}" y="{y}" w="{w}" h="{h}" c="{color}" />\n')
            elif shape[0] == 'polygon':
                _, points, color = shape
                pts_str = " ".join([f"{x},{y}" for x, y in points])
                f.write(f'    <polygon pts="{pts_str}" c="{color}" />\n')
        
        # Rects
        for x0, y0, x1, y1, color in all_rects:
            w, h = x1 - x0 + 1, y1 - y0 + 1
            f.write(f'    <rect x="{x0}" y="{y0}" w="{w}" h="{h}" c="{color}" />\n')
        
        # Columns
        for x, y1, y2, color in columns:
            f.write(f'    <column x="{x}" y1="{y1}" y2="{y2}" c="{color}" />\n')
        
        # Rows
        for y, xs, xe, color in optimized_rows:
            f.write(f'    <row y="{y}" x1="{xs}" x2="{xe}" c="{color}" />\n')
        
        # Dots
        dots_by_color = {}
        for y, x, color in final_dots:
            dots_by_color.setdefault(color, []).append(f"{x},{y}")
        
        for color, pts in sorted(dots_by_color.items()):
            f.write(f'    <dots c="{color}" pts="{" ".join(pts)}" />\n')
        
        f.write('  </layer>\n')
        f.write('</pxvg>\n')
    
    return (gw, gh, len(palette), block_size)

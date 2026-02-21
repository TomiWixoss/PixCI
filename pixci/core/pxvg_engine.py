import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from typing import Tuple

from .canvas import Canvas
from .code_engine import _detect_block_size, _build_grid, _find_best_rects, _collect_all_runs

def decode_pxvg(text_path: Path, output_path: Path, scale: int = 1) -> Tuple[int, int]:
    """Decode a .pxvg (XML) file into a PNG image."""
    try:
        tree = ET.parse(text_path)
    except ET.ParseError as e:
        raise ValueError(f"Lỗi cú pháp XML trong file PXVG: {e}")
        
    root = tree.getroot()
    
    # Optional namespace clearing if present
    def strip_ns(tag):
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    # 1. Canvas setup
    width = int(root.attrib.get('w', root.attrib.get('width', '32')))
    height = int(root.attrib.get('h', root.attrib.get('height', '32')))
    
    canvas = Canvas(width, height)
    
    # 2. Iterate tags
    for child in root:
        tag = strip_ns(child.tag).lower()
        
        if tag == 'palette':
            load_name = child.attrib.get('load')
            if load_name:
                canvas.load_palette(load_name)
            for color in child.findall('*'):
                ctag = strip_ns(color.tag).lower()
                if ctag == 'color':
                    k = color.attrib.get('k', color.attrib.get('key'))
                    hx = color.attrib.get('hex')
                    if k and hx:
                        canvas.add_color(k, hx)
                        
        elif tag == 'layer':
            layer_id = child.attrib.get('id', 'default')
            canvas.add_layer(layer_id)
            canvas.set_layer(layer_id)
            
            # Parse primitives within layer
            for shape in child:
                stag = strip_ns(shape.tag).lower()
                attr = shape.attrib
                
                c = attr.get('c', attr.get('color'))
                
                if stag == 'rect':
                    x = int(attr.get('x', 0))
                    y = int(attr.get('y', 0))
                    w = int(attr.get('w', attr.get('width', 1)))
                    h = int(attr.get('h', attr.get('height', 1)))
                    canvas.fill_rect((x, y), (x + w - 1, y + h - 1), c)
                elif stag == 'row':
                    y = int(attr.get('y', 0))
                    x1 = int(attr.get('x1', attr.get('start-x', 0)))
                    x2 = int(attr.get('x2', attr.get('end-x', 0)))
                    canvas.draw_rows([(y, x1, x2, c)])
                elif stag == 'circle':
                    cxv = attr.get('cx')
                    cyv = attr.get('cy')
                    center_str = attr.get('center')
                    if center_str:
                        cxv, cyv = center_str.split(',')
                    r = int(attr.get('r', attr.get('radius', 1)))
                    canvas.fill_circle((int(cxv), int(cyv)), r, c)
                elif stag == 'polygon':
                    pts_str = attr.get('pts', attr.get('points', ''))
                    pts = []
                    for pt in pts_str.split():
                        px, py = pt.split(',')
                        pts.append((int(px), int(py)))
                    if pts:
                        canvas.fill_polygon(pts, c)
                elif stag == 'dome':
                    cx = int(attr.get('cx', attr.get('center-x', 0)))
                    y = int(attr.get('y', attr.get('base-y', 0)))
                    w = int(attr.get('w', attr.get('width', 1)))
                    h = int(attr.get('h', attr.get('height', 1)))
                    canvas.draw_dome(cx, y, w, h, c)
                elif stag == 'taper':
                    cx = int(attr.get('cx', attr.get('center-x', 0)))
                    y1 = int(attr.get('y1', attr.get('top-y', 0)))
                    y2 = int(attr.get('y2', attr.get('bottom-y', 0)))
                    w1 = int(attr.get('w1', attr.get('top-width', 1)))
                    w2 = int(attr.get('w2', attr.get('bottom-width', 1)))
                    canvas.draw_taper(cx, y1, y2, w1, w2, c)
                elif stag == 'blob':
                    cxv = attr.get('cx')
                    cyv = attr.get('cy')
                    center_str = attr.get('center')
                    if center_str:
                        cxv, cyv = center_str.split(',')
                    rx = int(attr.get('rx', attr.get('radius-x', 1)))
                    ry = int(attr.get('ry', attr.get('radius-y', 1)))
                    noise = float(attr.get('noise', 0.15))
                    canvas.draw_blob((int(cxv), int(cyv)), rx, ry, c, noise)
                elif stag == 'dot':
                    x = int(attr.get('x', 0))
                    y = int(attr.get('y', 0))
                    canvas.set_pixel((x, y), c)
                elif stag == 'line':
                    x1 = int(attr.get('x1', 0))
                    y1 = int(attr.get('y1', 0))
                    x2 = int(attr.get('x2', 0))
                    y2 = int(attr.get('y2', 0))
                    canvas.draw_line((x1, y1), (x2, y2), c)
                    
        elif tag == 'postprocess':
            # Pre-merge all layers before postprocess as standard procedure
            canvas.merge_all()
            for pp in child:
                ptag = strip_ns(pp.tag).lower()
                attr = pp.attrib
                if ptag == 'outline':
                    sel_out = str(attr.get('sel-out', attr.get('sel_out', 'false'))).lower() == 'true'
                    thickness = int(attr.get('thickness', 1))
                    color = attr.get('color', '#000000FF')
                    canvas.add_outline(color=color, thickness=thickness, sel_out=sel_out)
                elif ptag in ['shadow', 'directional-shadow']:
                    d = attr.get('dir', attr.get('light-dir', 'top_left'))
                    i = float(attr.get('intensity', 0.3))
                    canvas.apply_directional_shadow(light_dir=d, intensity=i)
                elif ptag in ['jaggies', 'jaggies-cleanup']:
                    canvas.cleanup_jaggies()
                    
    canvas.save(str(output_path), scale=scale)
    return (width, height)


def encode_pxvg(image_path: Path, output_path: Path, block_size: int = 1, auto_detect: bool = True) -> Tuple[int, int, int, int]:
    """Encode an image to an ultra-compact PXVG XML format."""
    image_path = Path(image_path)
    output_path = Path(output_path)
    img = Image.open(image_path).convert("RGBA")
    
    if auto_detect:
        block_size = _detect_block_size(img)
        
    gw, gh, grid, palette = _build_grid(img, block_size)
    
    rects, used = _find_best_rects(grid, gw, gh)
    runs = _collect_all_runs(grid, gw, gh, used)
    
    single_pixels = [(y, xs, c) for y, xs, xe, c in runs if xs == xe]
    multi_runs = [(y, xs, xe, c) for y, xs, xe, c in runs if xs != xe]
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(f'<pxvg w="{gw}" h="{gh}" xmlns="http://pixci.dev/pxvg">\n')
        
        f.write('  <palette>\n')
        pal_items = sorted(palette.items(), key=lambda x: x[1])
        for hx, key in pal_items:
            f.write(f'    <color k="{key}" hex="{hx}" />\n')
        f.write('  </palette>\n')
        
        f.write('  <layer id="main">\n')
        
        for x0, y0, x1, y1, color in rects:
            w = x1 - x0 + 1
            h = y1 - y0 + 1
            f.write(f'    <rect x="{x0}" y="{y0}" w="{w}" h="{h}" c="{color}" />\n')
            
        for y, xs, xe, color in multi_runs:
            f.write(f'    <row y="{y}" x1="{xs}" x2="{xe}" c="{color}" />\n')
            
        for y, x, color in single_pixels:
            f.write(f'    <dot x="{x}" y="{y}" c="{color}" />\n')
            
        f.write('  </layer>\n')
        f.write('</pxvg>\n')
        
    return (gw, gh, len(palette), block_size)

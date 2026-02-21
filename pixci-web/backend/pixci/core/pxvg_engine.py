import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from typing import Tuple, Dict, List
from copy import deepcopy

from .canvas import Canvas
from .code_engine import _detect_block_size, _build_grid, _find_best_rects, _collect_all_runs

def _parse_drawing_tags(canvas: Canvas, parent_element: ET.Element, strip_ns):
    """Hàm phụ trợ để tái sử dụng logic vẽ cho cả Layer, Group và Frame"""
    for shape in parent_element:
        stag = strip_ns(shape.tag).lower()
        attr = shape.attrib
        
        c = attr.get('c', attr.get('color', '#00000000'))
        
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
        elif stag == 'column':
            x = int(attr.get('x', 0))
            y1 = int(attr.get('y1', attr.get('start-y', 0)))
            y2 = int(attr.get('y2', attr.get('end-y', 0)))
            # Vẽ column bằng cách vẽ từng pixel dọc
            for y in range(y1, y2 + 1):
                canvas.set_pixel((x, y), c)
        elif stag == 'circle':
            cx = int(attr.get('cx', 0))
            cy = int(attr.get('cy', 0))
            center_str = attr.get('center')
            if center_str:
                cx, cy = map(int, center_str.split(','))
            r = int(attr.get('r', attr.get('radius', 1)))
            fill = str(attr.get('fill', 'true')).lower() == 'true'
            if fill:
                canvas.fill_circle((cx, cy), r, c)
            else:
                canvas.draw_circle((cx, cy), r, c, pixel_perfect=True)
        elif stag == 'ellipse':
            cx = int(attr.get('cx', 0))
            cy = int(attr.get('cy', 0))
            center_str = attr.get('center')
            if center_str:
                cx, cy = map(int, center_str.split(','))
            rx = int(attr.get('rx', 1))
            ry = int(attr.get('ry', 1))
            fill = str(attr.get('fill', 'true')).lower() == 'true'
            if fill:
                canvas.fill_ellipse((cx, cy), rx, ry, c)
            else:
                canvas.draw_ellipse((cx, cy), rx, ry, c, pixel_perfect=True)
        elif stag == 'rounded-rect':
            x = int(attr.get('x', 0))
            y = int(attr.get('y', 0))
            w = int(attr.get('w', 1))
            h = int(attr.get('h', 1))
            r = int(attr.get('r', 0))
            canvas.fill_rounded_rect((x, y), (x + w - 1, y + h - 1), r, c)
        elif stag == 'curve':
            start = tuple(map(int, attr.get('start', '0,0').split(',')))
            ctrl = tuple(map(int, attr.get('ctrl', '0,0').split(',')))
            end = tuple(map(int, attr.get('end', '0,0').split(',')))
            thickness = int(attr.get('thickness', attr.get('t', 1)))
            canvas.draw_curve(start, ctrl, end, c, thickness=thickness)
        elif stag == 'cubic-curve':
            p0 = tuple(map(int, attr.get('p0', '0,0').split(',')))
            p1 = tuple(map(int, attr.get('p1', '0,0').split(',')))
            p2 = tuple(map(int, attr.get('p2', '0,0').split(',')))
            p3 = tuple(map(int, attr.get('p3', '0,0').split(',')))
            thickness = int(attr.get('thickness', attr.get('t', 1)))
            canvas.draw_cubic_curve(p0, p1, p2, p3, c, thickness=thickness)
        elif stag == 'bucket':
            x = int(attr.get('x', 0))
            y = int(attr.get('y', 0))
            canvas.fill_bucket((x, y), c)
        elif stag == 'dither':
            x = int(attr.get('x', 0))
            y = int(attr.get('y', 0))
            w = int(attr.get('w', 1))
            h = int(attr.get('h', 1))
            c2 = attr.get('c2', '#00000000')
            pattern = attr.get('pattern', 'checkered')
            ratio = float(attr.get('ratio', 0.5))
            canvas.fill_dither((x, y, x + w - 1, y + h - 1), c, c2, pattern, ratio)
        elif stag == 'alpha-lock':
            canvas.alpha_lock = str(attr.get('v', 'true')).lower() == 'true'
        elif stag == 'translate':
            canvas.translate(int(attr.get('dx', 0)), int(attr.get('dy', 0)))
        elif stag == 'flip-x':
            canvas.flip_x()
        elif stag == 'flip-y':
            canvas.flip_y()
        elif stag == 'mirror-x':
            canvas.mirror_x()
        elif stag == 'mirror-y':
            canvas.mirror_y()
        elif stag == 'polygon':
            pts_str = attr.get('pts', attr.get('points', ''))
            pts = []
            for pt in pts_str.split():
                if ',' in pt:
                    px, py = pt.split(',')
                    pts.append((int(px), int(py)))
            if pts:
                canvas.fill_polygon(pts, c)

        elif stag == 'dot':
            x = int(attr.get('x', 0))
            y = int(attr.get('y', 0))
            canvas.set_pixel((x, y), c)
        elif stag == 'dots':
            pts_str = attr.get('pts', attr.get('points', ''))
            if pts_str:
                for pt in pts_str.split():
                    if ',' in pt:
                        px, py = pt.split(',')
                        canvas.set_pixel((int(px), int(py)), c)
        elif stag == 'line':
            x1 = int(attr.get('x1', 0))
            y1 = int(attr.get('y1', 0))
            x2 = int(attr.get('x2', 0))
            y2 = int(attr.get('y2', 0))
            thickness = int(attr.get('thickness', attr.get('t', 1)))
            canvas.draw_line((x1, y1), (x2, y2), c, thickness=thickness)
        elif stag == 'gradient':
            x = int(attr.get('x', 0))
            y = int(attr.get('y', 0))
            w = int(attr.get('w', 1))
            h = int(attr.get('h', 1))
            mode = attr.get('mode', 'vertical')
            pal_str = attr.get('palette', c)
            pal = pal_str.split(',') if ',' in pal_str else [pal_str]
            canvas.fill_gradient((x, y, x + w - 1, y + h - 1), pal, mode=mode)
        elif stag == 'noise':
            x = int(attr.get('x', 0))
            y = int(attr.get('y', 0))
            w = int(attr.get('w', 1))
            h = int(attr.get('h', 1))
            density = float(attr.get('density', 0.5))
            pal_str = attr.get('palette', c)
            pal = pal_str.split(',') if ',' in pal_str else [pal_str]
            canvas.fill_noise((x, y, x + w - 1, y + h - 1), pal, density=density)


def decode_pxvg(text_path: Path, output_path: Path, scale: int = 1) -> Tuple[int, int]:
    """Decode a .pxvg (XML) file into a PNG image or Spritesheet."""
    try:
        tree = ET.parse(text_path)
    except ET.ParseError as e:
        raise ValueError(f"Lỗi cú pháp XML trong file PXVG: {e}")
        
    root = tree.getroot()
    
    def strip_ns(tag):
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    width = int(root.attrib.get('w', root.attrib.get('width', '32')))
    height = int(root.attrib.get('h', root.attrib.get('height', '32')))
    
    # --- BƯỚC 1: PARSE PALETTE ---
    master_palette = {}
    pal_tag = root.find('.//palette')
    if pal_tag is None:
        for child in root:
            if strip_ns(child.tag).lower() == 'palette':
                pal_tag = child
                break
                
    if pal_tag is not None:
        temp_canvas = Canvas(1, 1)
        if 'load' in pal_tag.attrib:
            temp_canvas.load_palette(pal_tag.attrib['load'])
        for color in pal_tag.findall('*'):
            if strip_ns(color.tag).lower() == 'color':
                k = color.attrib.get('k', color.attrib.get('key'))
                hx = color.attrib.get('hex')
                if k and hx: 
                    temp_canvas.add_color(k, hx)
        master_palette = temp_canvas.palette

    # --- BƯỚC 2: PARSE DEFS (LƯU VÀO BỘ NHỚ) ---
    definitions: Dict[str, ET.Element] = {}
    defs_tag = root.find('.//defs')
    if defs_tag is None:
        for child in root:
            if strip_ns(child.tag).lower() == 'defs':
                defs_tag = child
                break
                
    if defs_tag is not None:
        for group in defs_tag.findall('*'):
            if strip_ns(group.tag).lower() == 'group' and 'id' in group.attrib:
                definitions[group.attrib['id']] = group

    # --- BƯỚC 3: KIỂM TRA MODE (SINGLE IMAGE vs ANIMATION) ---
    anim_tag = root.find('.//animation')
    if anim_tag is None:
        for child in root:
            if strip_ns(child.tag).lower() == 'animation':
                anim_tag = child
                break
    
    if anim_tag is None:
        # CHẾ ĐỘ ẢNH TĨNH BÌNH THƯỜNG
        canvas = Canvas(width, height)
        canvas.palette = master_palette
        
        for child in root:
            tag = strip_ns(child.tag).lower()
            if tag == 'layer':
                layer_id = child.attrib.get('id', 'default')
                canvas.add_layer(layer_id)
                canvas.set_layer(layer_id)
                _parse_drawing_tags(canvas, child, strip_ns)
                
        # Postprocess
        post_tag = root.find('.//postprocess')
        if post_tag is None:
            for child in root:
                if strip_ns(child.tag).lower() == 'postprocess':
                    post_tag = child
                    break
        if post_tag is not None:
            canvas.merge_all()
            for pp in post_tag:
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
                elif ptag == 'internal-aa':
                    canvas.apply_internal_aa()
                elif ptag == 'shadow-mask':
                    cx = int(attr.get('cx', 0))
                    cy = int(attr.get('cy', 0))
                    r = int(attr.get('r', 1))
                    d = attr.get('dir', attr.get('light-dir', 'top_left'))
                    i = float(attr.get('intensity', 0.5))
                    canvas.apply_shadow_mask((cx, cy), r, light_dir=d, intensity=i)
                elif ptag == 'highlight-edge':
                    d = attr.get('dir', attr.get('light-dir', 'top_left'))
                    i = float(attr.get('intensity', 0.2))
                    canvas.add_highlight_edge(light_dir=d, intensity=i)
                    
        canvas.save(str(output_path), scale=scale)
        return (width, height)
        
    else:
        # CHẾ ĐỘ ANIMATION (SPRITESHEET)
        frames_tags = [f for f in anim_tag if strip_ns(f.tag).lower() == 'frame']
        num_frames = len(frames_tags)
        
        if num_frames == 0:
            raise ValueError("Không tìm thấy thẻ <frame> nào trong <animation>")
            
        columns = int(anim_tag.attrib.get('columns', num_frames))
        rows = (num_frames + columns - 1) // columns
        
        # Hình ảnh Spritesheet tổng
        spritesheet = Image.new("RGBA", (width * columns, height * rows), (0, 0, 0, 0))
        frames_list = []
        
        for idx, frame_tag in enumerate(frames_tags):
            # Mỗi frame là một canvas độc lập
            fc = Canvas(width, height)
            fc.palette = master_palette
            
            # Xử lý các thẻ bên trong Frame
            for elem in frame_tag:
                etag = strip_ns(elem.tag).lower()
                if etag == 'use':
                    ref = elem.attrib.get('ref')
                    if ref in definitions:
                        # Tạo 1 canvas nháp để vẽ cái group này
                        temp_c = Canvas(width, height)
                        temp_c.palette = master_palette
                        _parse_drawing_tags(temp_c, definitions[ref], strip_ns)
                        
                        # Copy từ nháp dán sang frame chính kèm theo offset X, Y
                        offset_x = int(elem.attrib.get('x', 0))
                        offset_y = int(elem.attrib.get('y', 0))
                        flip_x = str(elem.attrib.get('flip-x', 'false')).lower() == 'true'
                        
                        if flip_x: 
                            temp_c.flip_x()
                        
                        data = temp_c.copy_region((0, 0), (width - 1, height - 1))
                        fc.paste_region(data, (offset_x, offset_y), skip_transparent=True)
                else:
                    # Nếu AI vẽ trực tiếp trong frame (thay vì dùng use)
                    _parse_drawing_tags(fc, [elem], strip_ns)
            
            # Xử lý Postprocess cho CÁ NHÂN frame này
            post_tag = root.find('.//postprocess')
            if post_tag is None:
                for child in root:
                    if strip_ns(child.tag).lower() == 'postprocess':
                        post_tag = child
                        break
                        
            if post_tag is not None:
                fc.merge_all()
                for pp in post_tag:
                    ptag = strip_ns(pp.tag).lower()
                    attr = pp.attrib
                    if ptag == 'outline':
                        sel_out = str(attr.get('sel-out', attr.get('sel_out', 'false'))).lower() == 'true'
                        thickness = int(attr.get('thickness', 1))
                        color = attr.get('color', '#000000FF')
                        fc.add_outline(color=color, thickness=thickness, sel_out=sel_out)
                    elif ptag in ['shadow', 'directional-shadow']:
                        d = attr.get('dir', attr.get('light-dir', 'top_left'))
                        i = float(attr.get('intensity', 0.3))
                        fc.apply_directional_shadow(light_dir=d, intensity=i)
                    elif ptag in ['jaggies', 'jaggies-cleanup']:
                        fc.cleanup_jaggies()
                    elif ptag == 'internal-aa':
                        fc.apply_internal_aa()
                    elif ptag == 'shadow-mask':
                        cx = int(attr.get('cx', 0))
                        cy = int(attr.get('cy', 0))
                        r = int(attr.get('r', 1))
                        d = attr.get('dir', attr.get('light-dir', 'top_left'))
                        i = float(attr.get('intensity', 0.5))
                        fc.apply_shadow_mask((cx, cy), r, light_dir=d, intensity=i)
                    elif ptag == 'highlight-edge':
                        d = attr.get('dir', attr.get('light-dir', 'top_left'))
                        i = float(attr.get('intensity', 0.2))
                        fc.add_highlight_edge(light_dir=d, intensity=i)
            
            # Render frame này ra PIL Image
            fc.merge_all()
            frame_img = Image.new("RGBA", (width, height))
            pixels = frame_img.load()
            flat = fc.flatten()
            for x in range(width):
                for y in range(height):
                    pixels[x, y] = flat[x][y]
                    
            # Dán vào Spritesheet
            grid_x = idx % columns
            grid_y = idx // columns
            spritesheet.paste(frame_img, (grid_x * width, grid_y * height))
            
            # Cất frame (scale lên nếu có) vào list để xuất GIF
            if scale > 1:
                frame_img = frame_img.resize((width * scale, height * scale), Image.NEAREST)
            frames_list.append(frame_img)
            
        # Lưu file Spritesheet
        if scale > 1:
            spritesheet = spritesheet.resize(
                (width * columns * scale, height * rows * scale), 
                Image.NEAREST
            )
        
        spritesheet.save(str(output_path))
        
        # Lưu thêm file GIF động chứa cả quá trình
        if frames_list:
            fps = float(anim_tag.attrib.get('fps', 10))
            duration = int(1000 / fps)
            gif_path = output_path.with_suffix('.gif')
            
            frames_list[0].save(
                str(gif_path),
                format='GIF',
                save_all=True,
                append_images=frames_list[1:],
                duration=duration,
                loop=0,
                disposal=2 # Xoá frame cũ trước khi vẽ frame mới để ko bị dồn hình (transparent)
            )
        
        return (width * columns, height * rows)


def encode_pxvg(image_path: Path, output_path: Path, block_size: int = 1, auto_detect: bool = True) -> Tuple[int, int, int, int]:
    """
    Ultra-optimized PXVG encoder - Kết hợp tất cả kỹ thuật tốt nhất.
    Đảm bảo 100% pixel-perfect với số thẻ tối thiểu.
    """
    from .smart_encoder import smart_encode_pxvg
    return smart_encode_pxvg(image_path, output_path, block_size, auto_detect)

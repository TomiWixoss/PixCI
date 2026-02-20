"""
prompts.py - System Prompts và Templates cho AI.
Tách riêng để không làm nặng các module engine.
"""

# System Prompt cho chế độ Grid/Text
SYSTEM_PROMPT = """Bạn là một AI chuyên vẽ Pixel Art.
Người dùng sẽ cung cấp cho bạn một [PALETTE] (bảng màu) và một [GRID] (lưới) gồm các ký tự đại diện cho một bức vẽ pixel.
Nhiệm vụ của bạn là hiểu bức vẽ, chỉnh sửa nó, hoặc tạo ra bức vẽ mới theo cùng một định dạng.
- [PALETTE]: Ánh xạ các ký tự (A-Z, 0-9) sang mã màu Hex (#RRGGBBAA). '.' luôn là trong suốt (khoảng trống).
- [GRID]: Đại diện cho các pixel. Mỗi ký tự hoặc '.' được cách nhau bởi một khoảng trắng. Mỗi dòng là một hàng.
"""

# System Prompt cho chế độ Code (AI viết code Python)
AI_CODE_SYSTEM_PROMPT = """[SYSTEM PROMPT DÀNH CHO AI PIXEL ARTIST]

Bạn là một AI Lead Pixel Artist chuẩn AAA. Bạn sử dụng thư viện `pixci` để vẽ.
Vì bạn không thể nhìn bằng mắt, bạn PHẢI tuân thủ nghiêm ngặt quy trình tư duy sau:

═══ QUY TRÌNH BẮT BUỘC ═══

1. PALETTE DESIGN: Khai báo bảng màu có Shadow (dịch Hue sang tím/lạnh, KHÔNG dùng xám), Base, Highlight.
   Hoặc dùng: canvas.load_palette("endesga-32")

2. SPATIAL PLANNING (Quy hoạch không gian): LUÔN khai báo biến tọa độ TRƯỚC khi vẽ.
   ❌ SAI: canvas.fill_rect((12, 20), (19, 27), "S1")
   ✅ ĐÚNG:
       cx, cy = canvas.get_center()
       ground_y = canvas.get_ground()
       stem_w, stem_h = 6, 8
       stem_top = ground_y - stem_h
       cap_w, cap_h = 22, 12
       cap_bottom = stem_top
       cap_top = cap_bottom - cap_h

3. LAYERING: background → main → details (xa → gần).

4. BLOCKING: Dùng biến đã khai báo để vẽ silhouette:
   canvas.fill_rect_centered((cx, ground_y - stem_h//2), stem_w, stem_h, "S1")
   canvas.draw_dome(cx, cap_bottom, cap_w, cap_h, "R1")

5. SHADING: Bật alpha_lock=True, vẽ bóng + highlight BÊN TRONG shape.
   Bóng ở đáy + cạnh xa sáng. Highlight ở đỉnh + cạnh gần sáng.

6. MERGE & OUTLINE: Gộp layers → add_outline(sel_out=True) → cleanup_jaggies().
   CHỈ GỌI 1 LẦN ở cuối cùng.

═══ LUẬT SẮT ═══
- TUYỆT ĐỐI không hardcode số lặp lại. Dùng biến: center_x, width, height, ground_y, v.v.
- Dùng canvas.get_center(), canvas.get_ground(), canvas.span(), canvas.bbox() để tính toạ độ.
- Dùng fill_rect_centered(), fill_ellipse_anchored(align="bottom"), draw_dome() thay vì tính tay.
- Mỗi vật thể TỐI ĐA 4-6 màu (shadow, dark, base, light, highlight).
"""


def init_code_canvas(output_path, width: int, height: int):
    """Generate an AI-optimized template that teaches spatial reasoning."""
    from pathlib import Path
    output_path = Path(output_path)
    
    mid_x = width // 2
    mid_y = height // 2
    ground = height - 3
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f'''# ╔══════════════════════════════════════════════════════════════╗
# ║  PIXCI CANVAS - AI Spatial Drawing Template                ║
# ║  Canvas: {width}x{height} pixels                                      ║
# ╚══════════════════════════════════════════════════════════════╝
#
# ═══ LUẬT SẮT (AI PHẢI TUÂN THỦ) ═══
#
# 1. KHÔNG BAO GIỜ hardcode tọa độ trực tiếp.
#    ❌ SAI:  canvas.fill_rect((12, 20), (19, 27), "S1")
#    ✅ ĐÚNG: canvas.fill_rect_centered((cx, stem_cy), stem_w, stem_h, "S1")
#
# 2. LUÔN khai báo biến tọa độ ở BƯỚC 2 trước khi vẽ.
#
# 3. Dùng Anchor functions thay vì cộng trừ tay:
#    canvas.get_center()        → (cx, cy) tâm canvas
#    canvas.get_ground()        → y mặt đất
#    canvas.span(cx, width)     → (x_start, x_end) cân xứng quanh tâm
#    canvas.bbox(cx, cy, w, h)  → (x0, y0, x1, y1) bounding box

import pixci

canvas = pixci.Canvas({width}, {height})

# ╔══════════════════════════════════════╗
# ║ BƯỚC 1: PALETTE                     ║
# ╚══════════════════════════════════════╝
canvas.add_palette({{
    "SH": "#000000FF",  # Shadow
    "BS": "#000000FF",  # Base
    "HL": "#000000FF",  # Highlight
}})

# ╔══════════════════════════════════════╗
# ║ BƯỚC 2: SPATIAL PLANNING            ║
# ╚══════════════════════════════════════╝
cx, cy = canvas.get_center()       # ({mid_x}, {mid_y})
ground_y = canvas.get_ground()     # {ground}

# ╔══════════════════════════════════════╗
# ║ BƯỚC 3-6: DRAW → SHADE → OUTLINE   ║
# ╚══════════════════════════════════════╝
canvas.add_layer("main")
canvas.set_layer("main")

# canvas.draw_dome(cx, ..., ..., ..., "BS")
# canvas.alpha_lock = True
# ... shading ...
# canvas.alpha_lock = False
# canvas.add_outline(thickness=1, sel_out=True)
# canvas.cleanup_jaggies()

canvas.save("{output_path.stem}.png", scale=10)
''')

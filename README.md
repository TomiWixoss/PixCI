# TÀI LIỆU CÔNG CỤ: PIXCI
**Tên dự án:** PixCI (Pixel CLI & Coding Interface)
**Phiên bản:** 3.0.0 (Core CLI + Pro Python Library)
**Mô tả:** Bộ công cụ toàn diện (CLI + Python Library) giúp làm cầu nối giữa ảnh Pixel Art và AI (LLMs). Cho phép AI đọc hiểu, khởi tạo và chỉnh sửa ảnh pixel thông qua Văn bản (Grid) hoặc Lập trình Lệnh (Procedural Python Code) với độ chính xác tuyệt đối.

---

## 1. TỔNG QUAN
PixCI giải quyết vấn đề LLM gặp "ảo giác" khi xử lý không gian 2D bằng 2 chế độ:
1.  **Chế độ Cơ bản (Grid/Text):** Chuyển ảnh thành ma trận ký tự để AI nhìn tổng quan nhanh chóng.
2.  **Chế độ Nâng cao (Python Package):** Biến PixCI thành một thư viện Python. AI sẽ **viết code gọi các hàm của PixCI** (như toạ độ `(x, y)`, `fill_rect`, `draw_line`). Tool PixCI sau đó sẽ chạy đoạn code này để render ra ảnh cuối cùng.

---

## 2. CÀI ĐẶT
Yêu cầu: Python 3.9+

```bash
pip install -e .
```

---

## 3. THIẾT KẾ CLI (TRẢI NGHIỆM NGƯỜI DÙNG)

Các lệnh mà người dùng sẽ gõ trên Terminal của họ:

```bash
# === PHẦN CƠ BẢN (Grid Mode) ===
# 1. Chuyển ảnh thành Text Grid
pixci encode sprite.png -f grid -o output.txt

# 2. Chuyển Text Grid thành Ảnh
pixci decode output.txt --scale 10 -o result.png


# === PHẦN NÂNG CẤP (Code Mode) ===
# 3. Biến một ảnh PNG có sẵn thành Code Python
pixci encode sprite.png -f code -o generated_sprite.py

# 4. Khởi tạo một dự án Code trống cho AI
pixci init --size 32x32 -f code -o blank_canvas.py

# 5. Chạy file Python của AI để kết xuất thành ảnh PNG
pixci run ai_script.py --scale 10
```

---

## 4. TÀI LIỆU API CHO AI (System Prompt)

Để AI có thể sử dụng PixCI, bạn chỉ cần ném cho AI đoạn tài liệu dưới đây. Đoạn này được thiết kế ngắn gọn nhưng đủ để AI vẽ được ảnh pixel art chất lượng cao.

### ⭐ SYSTEM PROMPT GỬI AI:

```
Bạn là một Pixel Artist bậc thầy. Hãy dùng thư viện `pixci` bằng Python để vẽ.
TIẾ NẠP TƯ DUY:
- Hệ toạ độ: (0,0) = góc trên bên trái. X tăng sang phải, Y tăng xuống dưới.
- Luôn dùng Layer để tách phần (background, character, effects).
- Bật alpha_lock=True trước khi thêm bóng/highlight để không vẽ ra ngoài shape.
- Ưu tiên draw_rows() thay vì nhiều draw_line() liên tiếp khi sculpt shape phức tạp.
- Dùng fill_polygon() cho hình dạng tự do (lá, cánh, mũ nấm bất đối xứng).
- Cuối cùng mới add_outline() và cleanup_jaggies(). LUÔN dùng sel_out=True cho outline tự nhiên.
- Post-process cuối: apply_shadow_mask() cho vật tròn, apply_directional_shadow() cho vật phẳng/dọc.

THƯ VIỆN PIXCI HỖ TRỢ:

1. Canvas & Layer:
   canvas = pixci.Canvas(32, 32)
   canvas.add_layer("name")           # Thêm layer mới
   canvas.set_layer("name")           # Chuyển layer
   canvas.merge_layers("base", "top") # Gộp 2 layer
   canvas.alpha_lock = True/False     # Chỉ vẽ lên pixel có sẵn

2. Bảng màu (hỗ trợ 4000+ palette từ Lospec!):
   canvas.add_palette({"R1": "#E62E2D", "R2": "#B31C26"})
   canvas.load_palette("endesga-32")           # Fetch từ lospec.com, tự cache offline
   canvas.load_palette("pico-8")               # Slug name = tên trên Lospec URL
   canvas.load_palette("oil-6", prefix="O_")   # Dùng prefix tránh trùng key
   ramp = canvas.generate_ramp("#E62E2D", 5, "hue_shift")  # Tạo dải màu chuyên nghiệp
   shades = canvas.auto_shade("#E62E2D", 2)   # Tạo shadow+highlight variants

3. Vẽ hình cơ bản:
   canvas.set_pixel((x, y), "R1")
   canvas.draw_line((x0,y0), (x1,y1), "R1")
   canvas.fill_rect((x0,y0), (x1,y1), "R1")
   canvas.fill_rounded_rect((x0,y0), (x1,y1), radius, "R1")
   canvas.fill_circle(center, radius, "R1")
   canvas.fill_ellipse(center, rx, ry, "R1")

4. Vẽ shape nâng cao:
   canvas.draw_rows([(y, x_start, x_end, "R1"), ...])     # Sculpt shape từng dòng (GỢI Ý DÙNG NHIỀU)
   canvas.fill_polygon([(x,y), ...], "R1")                 # Đa giác đặc ruột
   canvas.draw_curve(start, control, end, "R1")             # Bezier bậc 2
   canvas.draw_cubic_curve(p0, p1, p2, p3, "R1")           # Bezier bậc 3
   canvas.draw_arc(center, radius, start_deg, end_deg, "R1") # Cung tròn
   canvas.draw_polyline(points, "R1", closed=True)          # Nối nhiều điểm

5. Semantic Shapes (AI-friendly, MÔ TẢ hình dạng thay vì toạ độ):
   canvas.draw_dome(center_x, base_y, width, height, "R1")         # Vòm (mũ nấm, đồi, mái)
   canvas.draw_taper(center_x, top_y, bot_y, top_w, bot_w, "S1")   # Thu hẹp (thân cây, cột, sừng)
   canvas.draw_blob(center, rx, ry, "G1", noise=0.15)               # Hình dạng tự nhiên (mây, bụi)
   canvas.draw_star(center, outer_r, inner_r, 5, "Y1")              # Ngôi sao
   canvas.draw_gem(center, w, h, [dark, mid, light, highlight])      # Viên đá quý tự shading

6. Dither & 3D Render:
   canvas.fill_dither(rect_tuple, c1, c2, "checkered"|"25_percent"|"bayer")
   canvas.draw_sphere(center, radius, palette_list, "top_left")
   canvas.draw_half_sphere(center, radius, palette_list, "top_left")
   canvas.fill_cylinder(base, width, height, palette_list, "top_left")

7. Post-process:
   canvas.add_outline(thickness=1, sel_out=True)            # Viền tự nhiên theo màu gốc
   canvas.cleanup_jaggies()                                  # Xoá bậc thang outline
   canvas.apply_shadow_mask(center, radius, "top_left", 0.3) # Bóng cầu (cho vật tròn)
   canvas.apply_directional_shadow("top_left", 0.3)          # Bóng hướng (cho vật phẳng)
   canvas.add_highlight_edge("top_left", intensity=0.2)       # Viền sáng rim-light
   canvas.apply_internal_aa()                                 # Khử răng cưa bên trong

8. Biến đổi:
   canvas.flip_x() / canvas.flip_y()
   canvas.translate(dx, dy)
   canvas.mirror_x()                                          # Đối xứng trái-phải
   canvas.fill_bucket((x,y), "R1")
   canvas.stamp((x0,y0), (x1,y1), (target_x, target_y))     # Copy-paste vùng
   canvas.preview()                                            # Xem lại canvas dưới dạng text

9. Lưu file:
   canvas.save("output.png", scale=10)

QUY TẮC VÀNG CỦA PIXEL ART:
- Bắt đầu từ silhouette (shape lớn) → chi tiết → bóng → highlight → outline.
- Dùng TỐI ĐA 4-6 màu cho mỗi vật thể (bao gồm shadow + highlight).
- Bóng nên ấm hơn (warm) và highlight nên lạnh hơn (cool) so với base color.
- Outline KHÔNG nên đen thuần. Dùng sel_out=True để outline theo màu gốc.
- Tránh "banding" (các dải màu song song). Xen kẽ pixel để tạo texture.
- Mỗi pixel phải có MỤC ĐÍCH. Đừng thêm pixel chỉ vì có chỗ trống.
```

---

## 5. VÍ DỤ CODE AI CHẤT LƯỢNG AAA

```python
import pixci

# 1. Khởi tạo Canvas 32x32
canvas = pixci.Canvas(32, 32)
canvas.add_layer("grass")
canvas.add_layer("mushroom")

# 2. Định nghĩa Bảng màu thủ công
canvas.add_palette({
    "BG": "#00000000",   # Trong suốt
    "R1": "#E62E2D",     # Đỏ cơ bản
    "R2": "#B31C26",     # Đỏ tối (Bóng tối)
    "R3": "#FF6B6B",     # Đỏ sáng (Highlight)
    "W1": "#FFFFFF",     # Trắng tinh
    "W2": "#E0E0E0",     # Trắng xám (Bóng của đốm trắng)
    "S1": "#E8D5C4",     # Màu thân nấm sáng
    "S2": "#B59C8D",     # Màu thân nấm tối
    "G1": "#1E1A20",     # Gầm nấm (Rất tối)
    "C1": "#45B363",     # Cỏ sáng
    "C2": "#2A7A44",     # Cỏ tối
})

# ==========================================
# LAYER: GRASS (Cỏ dưới nền)
# ==========================================
canvas.set_layer("grass")
canvas.draw_rows([
    (28, 6, 26, "C2"),
    (29, 4, 28, "C1"),
    (30, 3, 29, "C1"),
    (31, 4, 28, "C2"),
])
canvas.set_pixel((5, 28), "C1")
canvas.set_pixel((27, 28), "C1")
canvas.fill_dither((5, 29, 27, 30), color1="C1", color2="C2", pattern="checkered")


# ==========================================
# LAYER: MUSHROOM (Sculpt mũ nấm bằng draw_rows)
# ==========================================
canvas.set_layer("mushroom")

# Vẽ Thân nấm
canvas.fill_rect((13, 20), (18, 28), "S1")
canvas.fill_rect((17, 20), (18, 28), "S2")
canvas.set_pixel((12, 28), "S1")
canvas.set_pixel((19, 28), "S2")

# Vẽ Gầm nấm
canvas.fill_ellipse(center=(16, 20), rx=6, ry=1, color="G1")

# Vẽ Mũ nấm - Dùng draw_rows để sculpt chính xác
canvas.draw_rows([
    (6,  13, 18, "R1"),
    (7,  10, 21, "R1"),
    (8,   8, 23, "R1"),
    (9,   6, 25, "R1"),
    (10,  5, 26, "R1"),
    (11,  4, 27, "R1"),
    (12,  4, 27, "R1"),
    (13,  4, 27, "R1"),
    (14,  4, 27, "R1"),
    (15,  4, 27, "R1"),
    (16,  4, 27, "R1"),
    (17,  5, 26, "R1"),
    (18,  6, 25, "R1"),
])

# === Alpha Lock: vẽ bóng, highlight, đốm nằm trong hình ===
canvas.alpha_lock = True

# Bóng đáy và cạnh phải
canvas.draw_rows([
    (18, 6, 25, "R2"),
    (17, 5, 26, "R2"),
])
canvas.fill_rect((24, 11), (27, 16), "R2")
canvas.draw_rows([
    (9,  22, 25, "R2"),
    (10, 24, 26, "R2"),
])

# Highlight bắt sáng
canvas.draw_rows([
    (7,  10, 14, "R3"),
    (8,   8, 12, "R3"),
    (9,   7,  9, "R3"),
])

# Các đốm trắng 
canvas.fill_circle(center=(11, 14), radius=2, color="W1")
canvas.set_pixel((12, 15), "W2")

canvas.fill_circle(center=(21, 15), radius=1, color="W1")
canvas.set_pixel((21, 16), "W2")

# Các đốm dẹt phối cảnh bằng Ellipse
canvas.fill_ellipse(center=(16, 11), rx=1, ry=0, color="W1")
canvas.fill_ellipse(center=(7,  15), rx=0, ry=1, color="W1")
canvas.fill_ellipse(center=(24, 13), rx=0, ry=1, color="W1")

canvas.alpha_lock = False

# ==========================================
# POST-PROCESS
# ==========================================
canvas.apply_shadow_mask(center=(16, 16), radius=14, light_dir="top_left", intensity=0.3, shadow_color="#100010")

# Gộp layer và bọc viền
canvas.merge_layers(base_layer="grass", top_layer="mushroom")
canvas.set_layer("grass")
canvas.add_outline(thickness=1, sel_out=True)
canvas.cleanup_jaggies()

canvas.save("mushroom_aaa.png", scale=10)
```

---

## 6. KIẾN TRÚC CODE

```
pixci/
├── __init__.py          # Export Canvas + grid functions
├── __main__.py          # python -m pixci  
├── cli.py               # Typer CLI (encode/decode/init/run)
└── core/
    ├── canvas.py         # Canvas class (kết hợp tất cả Mixins)
    ├── canvas_base.py    # BaseCanvas: layers, pixel access, save
    ├── grid_engine.py    # Encode/Decode giữa Image ↔ Text/Code
    └── mixins/
        ├── color.py      # Palette (Lospec API + offline), generate_ramp, auto_shade
        ├── geometry.py   # draw_line, fill_rect, fill_polygon, draw_rows, curves, arcs
        ├── render.py     # fill_dither, draw_sphere, fill_cylinder
        ├── postprocess.py# add_outline, shadow_mask, directional_shadow, cleanup_jaggies
        ├── transform.py  # flip, translate, mirror, copy/paste, preview, snapshot
        └── isometric.py  # draw_iso_cube
```

---

## 7. HỆ THỐNG PALETTE

PixCI tích hợp trực tiếp với **Lospec** (lospec.com) - kho 4000+ palette pixel art lớn nhất thế giới.

```python
# Load bất kỳ palette nào bằng slug name (tên trên URL lospec)
canvas.load_palette("endesga-32")      # 32 màu, phổ biến nhất
canvas.load_palette("pico-8")          # 16 màu retro console  
canvas.load_palette("sweetie-16")      # 16 màu mềm mại
canvas.load_palette("resurrect-64")    # 64 màu đa dạng
canvas.load_palette("oil-6")           # 6 màu minimalist
canvas.load_palette("slso8")           # 8 màu pastel
canvas.load_palette("apollo")          # Palette Apollo
canvas.load_palette("dawnbringer-32")  # DawnBringer 32
```

**Cơ chế hoạt động:** Lospec API → Cache local (`.palette_cache/`) → Offline fallback.

| Palette Offline | Số màu | Mô tả |
|---|---|---|
| `endesga-32` | 32 | Bảng màu pixel art phổ biến nhất |
| `pico-8` | 16 | Retro console |
| `sweetie-16` | 16 | Mềm mại, RPG/platformer |
| `resurrect-64` | 64 | Đa dạng nhất |
| `gameboy` | 4 | Game Boy (4 sắc xanh) |

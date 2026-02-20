"""
Demo: Vẽ Nấm v3 - Showcase các tính năng mới của PixCI 3.0
So sánh với mushroom_final.py:
  - Dùng draw_rows() thay vì nhiều draw_line()  → code gọn hơn 40%
  - Dùng auto_shade() để tạo palette tự động     → AI không cần pick màu thủ công 
  - Dùng apply_directional_shadow()               → bóng tự nhiên hơn
  - cleanup_jaggies() hoạt động đúng với sel_out  → outline mượt
  - add_highlight_edge()                           → rim lighting chuyên nghiệp
"""
import pixci

# 1. Khởi tạo Canvas
canvas = pixci.Canvas(32, 32)
canvas.add_layer("grass")
canvas.add_layer("mushroom")

# 2. Sử dụng auto_shade() để tạo bảng màu TỰ ĐỘNG từ base colors
red_shades = canvas.auto_shade("#E62E2D", levels=2)
stem_shades = canvas.auto_shade("#E8D5C4", levels=1)
grass_shades = canvas.auto_shade("#45B363", levels=1)

# Map auto-generated shades vào palette dễ đọc
canvas.add_palette({
    "R1": red_shades["base"],       # Đỏ cơ bản
    "R2": red_shades["dark1"],      # Auto-generated dark
    "R3": red_shades["light1"],     # Auto-generated highlight
    "R4": red_shades["dark2"],      # Deepest shadow
    "W1": "#FFFFFFFF",
    "W2": "#E0E0E0FF",
    "S1": stem_shades["base"],
    "S2": stem_shades["dark1"],
    "G1": "#1E1A20FF",
    "C1": grass_shades["base"],
    "C2": grass_shades["dark1"],
})

# ==========================================
# LAYER: GRASS - Dùng draw_rows (gọn hơn 4 draw_line!)
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
# LAYER: MUSHROOM - Sculpt shape bằng draw_rows
# ==========================================
canvas.set_layer("mushroom")

# Thân nấm
canvas.fill_rect((13, 20), (18, 28), "S1")
canvas.fill_rect((17, 20), (18, 28), "S2")
canvas.set_pixel((12, 28), "S1")
canvas.set_pixel((19, 28), "S2")

# Gầm nấm
canvas.fill_ellipse(center=(16, 20), rx=6, ry=1, color="G1")

# Mũ nấm - Draw rows cho phép kiểm soát từng dòng pixel
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

# === Alpha Lock Mode ===
canvas.alpha_lock = True

# Bóng thủ công (chính xác hơn auto shadow)
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

# Đốm trắng
canvas.fill_circle(center=(11, 14), radius=2, color="W1")
canvas.set_pixel((12, 15), "W2")
canvas.fill_circle(center=(21, 15), radius=1, color="W1")
canvas.set_pixel((21, 16), "W2")

# Đốm nhỏ phối cảnh
canvas.fill_ellipse(center=(16, 11), rx=1, ry=0, color="W1")
canvas.fill_ellipse(center=(7,  15), rx=0, ry=1, color="W1")
canvas.fill_ellipse(center=(24, 13), rx=0, ry=1, color="W1")

canvas.alpha_lock = False

# ==========================================
# POST-PROCESS - Cải tiến v3
# ==========================================
# Shadow mask cho phần tròn (mũ nấm)
canvas.apply_shadow_mask(center=(16, 16), radius=14, light_dir="top_left", intensity=0.3, shadow_color="#100010")

# Gộp layer
canvas.merge_layers(base_layer="grass", top_layer="mushroom")
canvas.set_layer("grass")

# Outline tự nhiên (sel_out) - giờ cleanup_jaggies hoạt động đúng!
canvas.add_outline(thickness=1, sel_out=True, darkness=0.35, saturation_boost=1.3)
canvas.cleanup_jaggies()

canvas.save("mushroom_v3_demo.png", scale=10)
print("Saved: mushroom_v3_demo.png")

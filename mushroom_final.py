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
canvas.draw_line((6, 28), (26, 28), "C2")
canvas.draw_line((4, 29), (28, 29), "C1")
canvas.draw_line((3, 30), (29, 30), "C1")
canvas.draw_line((4, 31), (28, 31), "C2")
canvas.set_pixel((5, 28), "C1")
canvas.set_pixel((27, 28), "C1")
canvas.fill_dither((5, 29, 27, 30), color1="C1", color2="C2", pattern="checkered")


# ==========================================
# LAYER: MUSHROOM (Nấm nổi lên trên cỏ)
# ==========================================
canvas.set_layer("mushroom")

# Vẽ Thân nấm
canvas.fill_rect((13, 20), (18, 28), "S1")
canvas.fill_rect((17, 20), (18, 28), "S2")
canvas.set_pixel((12, 28), "S1")
canvas.set_pixel((19, 28), "S2")

# Vẽ Gầm nấm (Sử dụng tính năng Ellipse rỗng dẹt)
canvas.fill_ellipse(center=(16, 20), rx=6, ry=1, color="G1")

# Vẽ Mũ nấm (Quét từng dòng kết hợp cắt góc)
canvas.draw_line((13, 6), (18, 6), "R1")
canvas.draw_line((10, 7), (21, 7), "R1")
canvas.draw_line((8, 8),  (23, 8), "R1")
canvas.draw_line((6, 9),  (25, 9), "R1")
canvas.draw_line((5, 10), (26, 10), "R1")
canvas.fill_rect((4, 11), (27, 16), "R1")
# Cắt cong lùi vào ở góc dưới cùng, khử tai dơi
canvas.draw_line((5, 17), (26, 17), "R1")
canvas.draw_line((6, 18), (25, 18), "R1")

# === Bật khóa Alpha để vẽ bóng, highlight và đốm nằm trong Mũ nấm ===
canvas.alpha_lock = True

# Bóng râm ở đáy và 2 bên
canvas.draw_line((6, 18), (25, 18), "R2")
canvas.draw_line((5, 17), (26, 17), "R2")
canvas.fill_rect((24, 11), (27, 16), "R2")
canvas.draw_line((22, 9),  (25, 9), "R2")
canvas.draw_line((24, 10), (26, 10), "R2")

# Highlight bắt sáng
canvas.draw_line((10, 7), (14, 7), "R3")
canvas.draw_line((8, 8),  (12, 8), "R3")
canvas.draw_line((7, 9),  (9,  9), "R3")

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

# Áp dụng shadow mask cho phần thân nấm
canvas.apply_shadow_mask(center=(16, 16), radius=14, light_dir="top_left", intensity=0.3, shadow_color="#100010")

# ==========================================
# GỘP LAYER VÀ BỌC VIỀN DƯỚI CÙNG
# ==========================================
# CHỈ TẠO OUTLINE ĐÚNG 1 LẦN DƯỚI CÙNG
canvas.merge_layers(base_layer="grass", top_layer="mushroom")
canvas.set_layer("grass")
canvas.add_outline(thickness=1, sel_out=True)

# Khử răng cưa
canvas.cleanup_jaggies()

canvas.save("mushroom_final_masterpiece.png", scale=10)

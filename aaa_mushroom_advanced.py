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

# Viền Selective Outline cho lớp cỏ (Lấy màu cỏ làm tối lại)
canvas.add_outline(thickness=1, sel_out=True)


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

# Vẽ Mũ nấm
canvas.draw_half_sphere(center=(16, 18), radius=10, palette=["R2", "R1", "R3"], light_dir="top_left")
canvas.draw_line((7, 18), (6, 19), "R2")
canvas.draw_line((24, 18), (25, 19), "R2")

# Highlight 
canvas.fill_rect((11, 9), (14, 10), "W1") 
canvas.set_pixel((12, 8), "W1")

# Các đốm trắng 
canvas.fill_circle(center=(11, 14), radius=2, color="W1")
canvas.set_pixel((12, 15), "W2")
canvas.fill_circle(center=(21, 15), radius=1, color="W1")
canvas.set_pixel((21, 16), "W2")

# Các đốm dẹt phối cảnh bằng Ellipse thay vì set từng pixel lẻ
canvas.fill_ellipse(center=(16, 11), rx=1, ry=0, color="W1")
canvas.fill_ellipse(center=(7,  15), rx=0, ry=1, color="W1")
canvas.fill_ellipse(center=(24, 13), rx=0, ry=1, color="W1")

# Áp dụng shadow mask cho phần thân và dưới nấm
canvas.apply_shadow_mask(center=(16, 16), radius=14, light_dir="top_left", intensity=0.3, shadow_color="#100010")

# Bao viền Selective Outline cho layer Nấm rời
canvas.add_outline(thickness=1, sel_out=True)

# Khử răng cưa cho toàn thể (Xóa pixel kẽ)
canvas.cleanup_jaggies()

# Dùng save sẽ tự động Flatten (gập layer nấm đè lên layer cỏ có nền trong suốt)
canvas.save("aaa_mushroom_advanced.png", scale=10)

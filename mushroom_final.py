import pixci

# 1. Khởi tạo Canvas 32x32
canvas = pixci.Canvas(32, 32)

# Bảng màu Ghibli / Tự nhiên
canvas.add_palette({
    "BG": "#00000000",   
    "R_HILITE": "#FF8A8A", # Highlight đỏ
    "R_BASE":   "#E63946", # Đỏ nấm
    "R_SHAD":   "#A82030", # Bóng đổ nấm
    "W_BASE":   "#FFF3E0", # Trắng kem (đốm)
    "W_SHAD":   "#D4C4B4", # Bóng đốm
    "S_LITE":   "#F1FAEE", # Sáng thân nấm
    "S_BASE":   "#A8DADC", # Màu thân base (hơi ngả lơ)
    "S_SHAD":   "#457B9D", # Bóng thân
    "GILLS":    "#1D3557", # Gầm nấm cực tối
    "GRASS_1":  "#2A9D8F",
    "GRASS_2":  "#217A6F",
    "OUTLINE":  "#1A1116", # Đen hơi tía
})

# ==========================================
# LAYER: GRASS
# ==========================================
canvas.add_layer("grass")
canvas.set_layer("grass")

# Đổ khối gò đất cong mượt ở hai đầu
canvas.draw_line((4, 28), (27, 28), "GRASS_1")
canvas.fill_rect((2, 29), (29, 31), "GRASS_2")
canvas.draw_line((3, 29), (28, 29), "GRASS_1") # Trộn màu nhẹ

# Điểm xuyết các ngọn cỏ nhô lên thay vì dùng Dither caro
canvas.set_pixel((6, 27), "GRASS_1")
canvas.set_pixel((11, 27), "GRASS_1")
canvas.set_pixel((17, 27), "GRASS_1")
canvas.set_pixel((21, 27), "GRASS_1")
canvas.set_pixel((25, 27), "GRASS_1")


# ==========================================
# LAYER: MUSHROOM
# ==========================================
canvas.add_layer("mushroom")
canvas.set_layer("mushroom")

# 1. Vẽ thân nấm (Thuôn dần mượt mà)
canvas.fill_rect((12, 24), (19, 27), "S_BASE")
canvas.fill_rect((18, 24), (19, 27), "S_SHAD")
canvas.fill_rect((12, 24), (12, 27), "S_LITE")
# Thu nhỏ nhẹ ở trên
canvas.fill_rect((13, 20), (18, 23), "S_BASE")
canvas.fill_rect((17, 20), (18, 23), "S_SHAD")
canvas.fill_rect((13, 20), (13, 23), "S_LITE")

# 2. Gầm nấm (Gills mỏng nhẹ)
canvas.draw_line((9, 19), (22, 19), "GILLS")
canvas.draw_line((11, 20), (20, 20), "GILLS")

# Bóng đổ Cast shadow của gầm nấm đè lên thân nấm (Rất quan trọng)
canvas.draw_line((13, 20), (18, 20), "S_SHAD")
canvas.draw_line((13, 21), (17, 21), "S_BASE")

# 3. Mũ nấm (Xóa bỏ nửa khối cầu máy móc, vẽ thủ công để tạo khối Cúp hoàn hảo)
canvas.draw_line((13, 6), (18, 6), "R_BASE")
canvas.draw_line((10, 7), (21, 7), "R_BASE")
canvas.draw_line((8, 8),  (23, 8), "R_BASE")
canvas.draw_line((6, 9),  (25, 9), "R_BASE")
canvas.draw_line((5, 10), (26, 10), "R_BASE")
canvas.fill_rect((4, 11), (27, 16), "R_BASE")
# Cắt cong lùi vào ở góc dưới cùng, hết bị tai dơi!
canvas.draw_line((5, 17), (26, 17), "R_BASE")
canvas.draw_line((6, 18), (25, 18), "R_BASE")

# 4. KHÓA ALPHA ĐỂ VẼ BÓNG VÀ ĐỐM MÀ KHÔNG TRÀN RA NGOÀI
canvas.alpha_lock = True

# Bóng râm ôm theo cung 3D
canvas.draw_line((6, 18), (25, 18), "R_SHAD")
canvas.draw_line((5, 17), (26, 17), "R_SHAD")
canvas.fill_rect((24, 11), (27, 16), "R_SHAD")
canvas.draw_line((22, 9),  (25, 9), "R_SHAD")
canvas.draw_line((24, 10), (26, 10), "R_SHAD")

# Điểm nhấn Highlight rực rỡ bám góc cong
canvas.draw_line((10, 7), (14, 7), "R_HILITE")
canvas.draw_line((8, 8),  (12, 8), "R_HILITE")
canvas.draw_line((7, 9),  (9,  9), "R_HILITE")

# 5. CÁC ĐỐM TRẮNG TỰ NHIÊN (Lùi vào trong, tránh dính viền)
# Đốm chính (Trái)
canvas.fill_rect((9, 12), (13, 14), "W_BASE")
canvas.draw_line((9, 15), (12, 15), "W_SHAD") # Bóng của đốm
canvas.set_pixel((9, 12), "R_BASE")  # Bo nhẹ góc

# Đốm phụ (Phải)
canvas.fill_rect((19, 13), (22, 14), "W_SHAD")
canvas.set_pixel((19, 13), "W_BASE")

# Đốm nhỏ (Trên cực)
canvas.fill_rect((16, 8), (17, 9), "W_BASE")
canvas.set_pixel((16, 9), "W_SHAD")

# Mở khóa Alpha để tránh ảnh hưởng hệ thống
canvas.alpha_lock = False

# ==========================================
# GỘP VÀ XUẤT
# ==========================================
# Ép Layer Nấm lên Layer Cỏ
canvas.merge_layers(base_layer="grass", top_layer="mushroom")
canvas.set_layer("grass")

# Chồng thêm màu bóng chân nấm dưới lớp cỏ để ăn nhập với mặt đất
canvas.draw_line((12, 28), (19, 28), "GRASS_2")

# Thuật toán Sel-out giờ sẽ hoạt động trơn tru vì các mảng màu đều được làm tròn
canvas.add_outline(thickness=1, sel_out=True)

canvas.save("mushroom_final_masterpiece.png", scale=10)

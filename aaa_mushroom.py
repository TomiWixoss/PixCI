import pixci

# 1. Khởi tạo Canvas 32x32
canvas = pixci.Canvas(32, 32)

# 2. Bảng màu Ghibli / Tự nhiên (Giữ nguyên vì quá đẹp)
canvas.add_palette({
    "BG": "#00000000",   
    "R_HILITE": "#FF8A8A", 
    "R_BASE":   "#E63946", 
    "R_SHAD":   "#A82030", 
    "W_BASE":   "#FFF3E0", 
    "W_SHAD":   "#D4C4B4", 
    "S_LITE":   "#F1FAEE", 
    "S_BASE":   "#A8DADC", 
    "S_SHAD":   "#457B9D", 
    "GILLS":    "#1D3557", 
    "GRASS_1":  "#2A9D8F",
    "GRASS_2":  "#217A6F",
    "OUTLINE":  "#1A1116", 
})

# ==========================================
# 1. VẼ GÒ CỎ TỰ NHIÊN (Không dùng hình chữ nhật lớn)
# ==========================================
# Đổ khối gò đất cong mượt ở hai đầu
canvas.draw_line((4, 28), (27, 28), "GRASS_1")
canvas.fill_rect((2, 29), (29, 31), "GRASS_2")
canvas.draw_line((3, 29), (28, 29), "GRASS_1") # Trộn màu nhẹ
# Điểm xuyết các ngọn cỏ nhô lên
canvas.set_pixel((6, 27), "GRASS_1")
canvas.set_pixel((11, 27), "GRASS_1")
canvas.set_pixel((21, 27), "GRASS_1")
canvas.set_pixel((25, 27), "GRASS_1")

# ==========================================
# 2. VẼ THÂN NẤM (Hình thang thuôn dần lên, không bị gãy góc)
# ==========================================
# Nửa dưới (Rộng hơn)
canvas.fill_rect((12, 24), (19, 27), "S_BASE")
canvas.fill_rect((18, 24), (19, 27), "S_SHAD")
canvas.fill_rect((12, 24), (12, 27), "S_LITE")
# Nửa trên (Hẹp hơn một chút, thuôn mượt)
canvas.fill_rect((13, 20), (18, 23), "S_BASE")
canvas.fill_rect((17, 20), (18, 23), "S_SHAD")
canvas.fill_rect((13, 20), (13, 23), "S_LITE")

# ==========================================
# 3. VẼ GẦM NẤM (Gills - Gọn gàng hơn)
# ==========================================
canvas.draw_line((9, 19), (22, 19), "GILLS")
canvas.draw_line((11, 20), (20, 20), "GILLS")

# ==========================================
# 4. VẼ MŨ NẤM (Khối vòm Dome hoàn hảo)
# ==========================================
# Điêu khắc từng dòng (Scanline) để tạo độ cong Pixel-perfect
canvas.draw_line((13, 6), (18, 6), "R_BASE")
canvas.draw_line((10, 7), (21, 7), "R_BASE")
canvas.draw_line((8, 8),  (23, 8), "R_BASE")
canvas.draw_line((6, 9),  (25, 9), "R_BASE")
canvas.draw_line((5, 10), (26, 10), "R_BASE")
canvas.fill_rect((4, 11), (27, 16), "R_BASE")
# Tém 2 bên mép dưới lùi vào trong để tạo hình ôm (Chữa lỗi "tai nấm")
canvas.draw_line((5, 17), (26, 17), "R_BASE")
canvas.draw_line((6, 18), (25, 18), "R_BASE")

# Đổ bóng (R_SHAD) ôm theo khối vòm
canvas.draw_line((6, 18), (25, 18), "R_SHAD")
canvas.draw_line((5, 17), (26, 17), "R_SHAD")
canvas.fill_rect((24, 11), (27, 16), "R_SHAD")
canvas.draw_line((22, 9),  (25, 9), "R_SHAD")
canvas.draw_line((24, 10), (26, 10), "R_SHAD")

# Highlight bắt sáng (Mượt và tập trung hơn)
canvas.draw_line((10, 7), (14, 7), "R_HILITE")
canvas.draw_line((8, 8),  (12, 8), "R_HILITE")
canvas.draw_line((7, 9),  (9,  9), "R_HILITE")

# ==========================================
# 5. CÁC ĐỐM TRẮNG (Chỉnh lại hình dáng tự nhiên hơn)
# ==========================================
# Đốm chính (Trái)
canvas.fill_rect((9, 12), (13, 14), "W_BASE")
canvas.draw_line((9, 15), (12, 15), "W_SHAD") # Bóng râm
canvas.set_pixel((9, 12), "R_BASE")  # Bo tròn góc

# Đốm phụ (Phải - dẹt do phối cảnh)
canvas.fill_rect((20, 14), (23, 15), "W_SHAD")
canvas.set_pixel((20, 14), "W_BASE")

# Đốm nhỏ (Trên)
canvas.fill_rect((16, 8), (18, 9), "W_BASE")
canvas.set_pixel((16, 9), "W_SHAD")

# ==========================================
# 6. HẬU KỲ XUẤT SẮC
# ==========================================
canvas.add_outline(color="OUTLINE", thickness=1)
canvas.cleanup_jaggies(outline_color="OUTLINE")

# Kỹ thuật bóng đổ (Drop Shadow): Thêm bóng của mũ nấm in lên thân nấm
canvas.draw_line((13, 20), (18, 20), "S_SHAD")
canvas.draw_line((13, 21), (17, 21), "S_BASE")

# Cắm chặt nấm vào cỏ (Sel-out Base)
# Tô đè một đường tối dưới chân nấm để viền không bị cắt ngang cỏ
canvas.draw_line((12, 28), (19, 28), "GRASS_2")

canvas.save("mushroom_final_masterpiece.png", scale=10)
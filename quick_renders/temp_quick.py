import pixci

# 1. Khởi tạo Canvas với kích thước 64x64 cho boss mini
canvas = pixci.Canvas(64, 64)

# 2. Khai báo bảng màu thủ công cho Rồng Máy
canvas.add_palette({
    "bg": "#00000000",        # Nền trong suốt
    "metal_light": "#9BA3AB", # Thép sáng
    "metal_mid": "#5A6570",   # Thép xám (Màu chủ đạo)
    "metal_dark": "#2B323B",  # Thép tối/Bóng râm
    "gun_barrel": "#A37050",  # Đồng/Cam cho nòng súng
    "red_glow": "#FF2020",    # Đỏ rực cho mắt và lõi năng lượng
})

# Lấy các mốc tọa độ hỗ trợ
cx, cy = canvas.get_center()
ground_y = canvas.get_ground(margin=4)

# 3. Bắt đầu vẽ từ lớp xa nhất đến lớp gần nhất
# --- LAYER 1: CHÂN SAU VÀ ĐUÔI ---
canvas.add_layer("back")
# Vẽ đuôi rồng bằng các vòng tròn nhỏ dần (từ gốc ra ngọn)
canvas.fill_circle((cx + 12, cy + 12), 6, "metal_dark")
canvas.fill_circle((cx + 18, cy + 8), 5, "metal_mid")
canvas.fill_circle((cx + 24, cy + 2), 4, "metal_dark")
canvas.fill_circle((cx + 28, cy - 5), 2, "metal_mid")

# Chân sau
canvas.fill_rect((cx - 8, cy + 5), (cx - 1, ground_y), "metal_dark")


# --- LAYER 2: THÂN CHÍNH VÀ GAI LƯNG ---
canvas.add_layer("body")
# Thân chính khom về phía trước, neo ở đáy
canvas.fill_ellipse_anchored((cx, ground_y - 8), 16, 14, "metal_mid", align="bottom")

# Dùng alpha lock để đổ bóng khối trên thân chính
canvas.alpha_lock = True
canvas.fill_circle((cx - 4, cy), 10, "metal_light") # Vùng sáng ngực
canvas.alpha_lock = False

# Gai trên lưng bằng hàm draw_taper (hình thuôn hẹp dần lên trên)
canvas.draw_taper(cx + 4, cy - 20, cy - 10, 0, 5, "metal_mid")
canvas.draw_taper(cx + 10, cy - 16, cy - 8, 0, 4, "metal_dark")
canvas.draw_taper(cx + 15, cy - 10, cy - 4, 0, 3, "metal_mid")


# --- LAYER 3: CỔ VÀ ĐẦU RỒNG ---
canvas.add_layer("head")
# Cổ rồng (dùng đa giác nối từ ngực lên đầu)
canvas.fill_polygon([(cx-5, cy-2), (cx-2, cy+2), (cx-14, cy-10), (cx-10, cy-12)], "metal_mid")

# Đầu rồng (khối sọ)
canvas.fill_polygon([(cx-10, cy-12), (cx-22, cy-10), (cx-20, cy-5), (cx-12, cy-6)], "metal_light")

# Mắt rồng máy
canvas.set_pixel((cx-16, cy-9), "red_glow")
canvas.set_pixel((cx-17, cy-9), "red_glow")

# Hàm dưới há ra
canvas.fill_polygon([(cx-12, cy-5), (cx-18, cy-1), (cx-14, cy+1)], "metal_dark")


# --- LAYER 4: CHÂN TRƯỚC VÀ TAY SÚNG ---
canvas.add_layer("front")
# Chân trước
canvas.fill_rect((cx - 2, cy + 6), (cx + 5, ground_y), "metal_light")
# Bàn chân/móng trước
canvas.fill_polygon([(cx-5, ground_y), (cx+7, ground_y), (cx+2, ground_y-4)], "metal_mid")

# Tay súng (Gun Arm) cực ngầu
# Bệ súng
canvas.fill_rect_centered((cx - 14, cy + 5), 16, 10, "metal_mid")
canvas.fill_rect_centered((cx - 14, cy + 5), 10, 6, "metal_dark")
# Nòng súng
canvas.fill_rect_centered((cx - 25, cy + 5), 8, 6, "gun_barrel")
# Lỗ súng rực đỏ chuẩn bị bắn
canvas.fill_rect_centered((cx - 28, cy + 5), 2, 4, "red_glow")


# 4. Gộp toàn bộ các lớp lại với nhau (từ trên xuống dưới)
canvas.merge_layers("back", "body")
canvas.merge_layers("body", "head")
canvas.merge_layers("head", "front")

# 5. Hậu kỳ (Post-processing)
# Tạo viền tự động bám theo hình dáng boss để ra chất Pixel Art
canvas.add_outline(thickness=1, sel_out=True)
# Thêm chút highlight ngược sáng ở góc trên bên trái
canvas.add_highlight_edge(light_dir="top_left", intensity=0.3)

# 6. Xuất file ảnh (Phóng to gấp 10 lần để dễ nhìn)
canvas.save("mega_mechadragon_pixci.png", scale=10)
import pixci

# 1. Khởi tạo Canvas (Kích thước 128x128 để vẽ Boss Siêu Khổng Lồ)
canvas = pixci.Canvas(128, 128)
cx, cy = canvas.get_center()

# 2. Hệ thống Màu sắc (Xương & Hư vô)
# Xương cổ đại (Trắng xám ám xanh)
bone = canvas.auto_shade("#D0D5E8", levels=3)
# Năng lượng Hư vô (Tím/Hồng Neon)
void = canvas.auto_shade("#B000FF", levels=3)
# Bóng tối vực thẳm
abyss = canvas.auto_shade("#0D0B1A", levels=2)

# Chuyển màu sang list cho các hàm 3D
bone_3d = [bone["dark3"], bone["base"], bone["light2"]]
void_3d = [void["dark3"], void["base"], void["light2"]]

# 3. Tọa độ neo các bộ phận
y_head = 30
y_chest = 60
y_pelvis = 90
y_tail = 115

# 4. Quản lý Layer
canvas.add_layer("aura")
canvas.add_layer("core")
canvas.add_layer("skeleton")
canvas.add_layer("head")
canvas.add_layer("arms")

# ==========================================
# VẼ CHI TIẾT BOSS XƯƠNG
# ==========================================

# --- LAYER 1: HÀO QUANG NĂNG LƯỢNG (AURA) ---
canvas.set_layer("aura")
# Lỗ đen hư vô phía sau lưng Boss
canvas.fill_circle((cx, y_chest), 45, abyss["dark2"])
canvas.fill_circle((cx, y_chest), 35, void["dark2"])
canvas.fill_circle((cx, y_chest), 25, abyss["dark2"]) # Đục rỗng ở giữa

# --- LAYER 2: TRÁI TIM HƯ VÔ (CORE) ---
canvas.set_layer("core")
# Khối pha lê ma thuật đóng vai trò làm tim ngay giữa lồng ngực
canvas.draw_gem((cx, y_chest), 16, 24, void_3d)

# Hai ấn thạch lơ lửng bảo vệ bên dưới
canvas.draw_gem((cx - 25, y_tail - 10), 8, 14, void_3d)
canvas.draw_gem((cx + 25, y_tail - 10), 8, 14, void_3d)

# --- LAYER 3: BỘ KHUNG XƯƠNG (SKELETON) ---
canvas.set_layer("skeleton")
# Cột sống (Chóp nhọn vuốt từ trên ngực xuống đuôi)
canvas.draw_taper(cx, y_head, y_tail, 10, 0, bone["dark1"])

# Các đốt sống (Vertebrae) lồi lên
for y in range(y_head + 15, y_pelvis, 10):
    canvas.fill_rect_centered((cx, y), 16, 4, bone["base"])

# Lồng ngực (Ribs) - Các mảng xương sườn đâm ngang
canvas.draw_taper(cx - 16, y_chest - 15, y_chest + 10, 8, 2, bone["base"])
canvas.draw_taper(cx + 16, y_chest - 15, y_chest + 10, 8, 2, bone["base"])
canvas.draw_taper(cx - 26, y_chest - 8, y_chest + 15, 6, 1, bone["dark1"])
canvas.draw_taper(cx + 26, y_chest - 8, y_chest + 15, 6, 1, bone["dark1"])

# Xương chậu (Pelvis) bay lơ lửng
canvas.fill_rect_centered((cx, y_pelvis), 28, 8, bone["base"])
canvas.draw_taper(cx - 12, y_pelvis + 4, y_pelvis + 16, 6, 0, bone["dark1"])
canvas.draw_taper(cx + 12, y_pelvis + 4, y_pelvis + 16, 6, 0, bone["dark1"])

# --- LAYER 4: HỘP SỌ VÀ SỪNG (HEAD) ---
canvas.set_layer("head")
# Hộp sọ trên (Cranium)
canvas.draw_dome(cx, y_head, 28, 20, bone["base"])
# Khối xương hàm
canvas.fill_rect_centered((cx, y_head + 8), 20, 12, bone["base"])
canvas.fill_rect_centered((cx, y_head + 16), 14, 6, bone["dark1"])

# Hốc mắt sâu thẳm & Con ngươi sáng rực
canvas.fill_rect_centered((cx - 6, y_head + 4), 6, 6, abyss["dark2"])
canvas.fill_rect_centered((cx + 6, y_head + 4), 6, 6, abyss["dark2"])
canvas.fill_circle((cx - 6, y_head + 4), 1, void["light2"])
canvas.fill_circle((cx + 6, y_head + 4), 1, void["light2"])

# Hốc mũi
canvas.fill_circle((cx, y_head + 10), 2, abyss["dark2"])

# Khe răng cưa hắc ám
canvas.draw_line((cx - 6, y_head + 14), (cx + 6, y_head + 14), abyss["dark2"])
canvas.draw_line((cx - 3, y_head + 12), (cx - 3, y_head + 16), abyss["dark2"])
canvas.draw_line((cx + 3, y_head + 12), (cx + 3, y_head + 16), abyss["dark2"])

# Cặp sừng xương cong vút lên trên
canvas.draw_taper(cx - 16, y_head - 8, y_head + 2, 6, 10, bone["dark1"]) # Gốc sừng trái
canvas.draw_taper(cx - 24, y_head - 22, y_head - 6, 0, 8, bone["base"])  # Ngọn sừng trái
canvas.draw_taper(cx + 16, y_head - 8, y_head + 2, 6, 10, bone["dark1"]) # Gốc sừng phải
canvas.draw_taper(cx + 24, y_head - 22, y_head - 6, 0, 8, bone["base"])  # Ngọn sừng phải

# --- LAYER 5: HAI CÁNH TAY XƯƠNG KHỔNG LỒ (ARMS) ---
canvas.set_layer("arms")
# Khớp vai lơ lửng dạng khối cầu 3D
canvas.draw_sphere((cx - 44, y_chest - 15), 14, bone_3d, light_dir="top_left")
canvas.draw_sphere((cx + 44, y_chest - 15), 14, bone_3d, light_dir="top_left")

# Cổ tay đứt đoạn lơ lửng
canvas.fill_circle((cx - 52, y_chest + 15), 10, bone["dark1"])
canvas.fill_circle((cx + 52, y_chest + 15), 10, bone["dark1"])

# Móng vuốt khổng lồ chĩa xuống đất cào xé
# Tay trái
canvas.draw_taper(cx - 60, y_chest + 20, y_chest + 55, 6, 0, bone["base"])
canvas.draw_taper(cx - 50, y_chest + 24, y_chest + 65, 6, 0, bone["light2"]) # Vuốt giữa dài nhất
canvas.draw_taper(cx - 40, y_chest + 20, y_chest + 45, 6, 0, bone["base"])
# Tay phải
canvas.draw_taper(cx + 60, y_chest + 20, y_chest + 55, 6, 0, bone["base"])
canvas.draw_taper(cx + 50, y_chest + 24, y_chest + 65, 6, 0, bone["light2"]) # Vuốt giữa dài nhất
canvas.draw_taper(cx + 40, y_chest + 20, y_chest + 45, 6, 0, bone["base"])


# ==========================================
# 5. HẬU KỲ VÀ XUẤT FILE
# ==========================================
# Gom toàn bộ chi tiết xuống layer thấp nhất (aura)
canvas.merge_layers("aura", "core")
canvas.merge_layers("aura", "skeleton")
canvas.merge_layers("aura", "head")
canvas.merge_layers("aura", "arms")
canvas.set_layer("aura")

# Dọn dẹp cấn góc
canvas.cleanup_jaggies()

# Đánh viền sáng từ hướng trên trái để nổi bật các dải xương sườn và hốc mắt
canvas.add_highlight_edge(light_dir="top_left", intensity=0.35)

# Bọc viền thông minh
canvas.add_outline(thickness=1, sel_out=True)

# Lưu ảnh khổng lồ (scale 10)
canvas.save("void_bone_boss.png", scale=10)
print("Đã triệu hồi thành công Boss Xương Hư Vô: void_bone_boss.png")
import pixci

# 1. Khởi tạo Animation (128x128, 4 Khung hình, Tốc độ 6 FPS)
anim = pixci.Animation(128, 128, columns=4, fps=6)

# Dùng 1 canvas tạm để sinh bảng màu (Palette)
dummy = pixci.Canvas(16, 16)
bone = dummy.auto_shade("#D0D5E8", levels=3)
void = dummy.auto_shade("#B000FF", levels=3)
abyss = dummy.auto_shade("#0D0B1A", levels=2)

bone_3d = [bone["dark3"], bone["base"], bone["light2"]]
void_3d = [void["dark3"], void["base"], void["light2"]]

# Tọa độ gốc
cx, cy = 64, 64
y_head, y_chest, y_pelvis, y_tail = 30, 60, 90, 115

# ==========================================
# 2. TẠO CÁC BỘ PHẬN ĐỘC LẬP (COMPONENTS)
# ==========================================

# --- COMPONENT A: Hào quang & Trái tim ---
cv_core = pixci.Canvas(128, 128)
cv_core.fill_circle((cx, y_chest), 45, abyss["dark2"])
cv_core.fill_circle((cx, y_chest), 35, void["dark2"])
cv_core.fill_circle((cx, y_chest), 25, abyss["dark2"])
cv_core.draw_gem((cx, y_chest), 16, 24, void_3d)
cv_core.draw_gem((cx - 25, y_tail - 10), 8, 14, void_3d)
cv_core.draw_gem((cx + 25, y_tail - 10), 8, 14, void_3d)

# --- COMPONENT B: Khung xương chính (Đầu + Thân) ---
cv_body = pixci.Canvas(128, 128)
# Cột sống & Lồng ngực
cv_body.draw_taper(cx, y_head, y_tail, 10, 0, bone["dark1"])
for y in range(y_head + 15, y_pelvis, 10):
    cv_body.fill_rect_centered((cx, y), 16, 4, bone["base"])
cv_body.draw_taper(cx - 16, y_chest - 15, y_chest + 10, 8, 2, bone["base"])
cv_body.draw_taper(cx + 16, y_chest - 15, y_chest + 10, 8, 2, bone["base"])
cv_body.draw_taper(cx - 26, y_chest - 8, y_chest + 15, 6, 1, bone["dark1"])
cv_body.draw_taper(cx + 26, y_chest - 8, y_chest + 15, 6, 1, bone["dark1"])
# Xương chậu
cv_body.fill_rect_centered((cx, y_pelvis), 28, 8, bone["base"])
cv_body.draw_taper(cx - 12, y_pelvis + 4, y_pelvis + 16, 6, 0, bone["dark1"])
cv_body.draw_taper(cx + 12, y_pelvis + 4, y_pelvis + 16, 6, 0, bone["dark1"])
# Đầu & Sừng
cv_body.draw_dome(cx, y_head, 28, 20, bone["base"])
cv_body.fill_rect_centered((cx, y_head + 8), 20, 12, bone["base"])
cv_body.fill_rect_centered((cx, y_head + 16), 14, 6, bone["dark1"])
cv_body.fill_rect_centered((cx - 6, y_head + 4), 6, 6, abyss["dark2"])
cv_body.fill_rect_centered((cx + 6, y_head + 4), 6, 6, abyss["dark2"])
cv_body.fill_circle((cx - 6, y_head + 4), 1, void["light2"])
cv_body.fill_circle((cx + 6, y_head + 4), 1, void["light2"])
cv_body.fill_circle((cx, y_head + 10), 2, abyss["dark2"])
cv_body.draw_line((cx - 6, y_head + 14), (cx + 6, y_head + 14), abyss["dark2"])
cv_body.draw_taper(cx - 16, y_head - 8, y_head + 2, 6, 10, bone["dark1"]) 
cv_body.draw_taper(cx - 24, y_head - 22, y_head - 6, 0, 8, bone["base"])  
cv_body.draw_taper(cx + 16, y_head - 8, y_head + 2, 6, 10, bone["dark1"]) 
cv_body.draw_taper(cx + 24, y_head - 22, y_head - 6, 0, 8, bone["base"])  

# --- COMPONENT C: Tay Trái ---
cv_l_arm = pixci.Canvas(128, 128)
cv_l_arm.draw_sphere((cx - 44, y_chest - 15), 14, bone_3d, light_dir="top_left")
cv_l_arm.fill_circle((cx - 52, y_chest + 15), 10, bone["dark1"])
cv_l_arm.draw_taper(cx - 60, y_chest + 20, y_chest + 55, 6, 0, bone["base"])
cv_l_arm.draw_taper(cx - 50, y_chest + 24, y_chest + 65, 6, 0, bone["light2"])
cv_l_arm.draw_taper(cx - 40, y_chest + 20, y_chest + 45, 6, 0, bone["base"])

# --- COMPONENT D: Tay Phải ---
cv_r_arm = pixci.Canvas(128, 128)
cv_r_arm.draw_sphere((cx + 44, y_chest - 15), 14, bone_3d, light_dir="top_left")
cv_r_arm.fill_circle((cx + 52, y_chest + 15), 10, bone["dark1"])
cv_r_arm.draw_taper(cx + 60, y_chest + 20, y_chest + 55, 6, 0, bone["base"])
cv_r_arm.draw_taper(cx + 50, y_chest + 24, y_chest + 65, 6, 0, bone["light2"])
cv_r_arm.draw_taper(cx + 40, y_chest + 20, y_chest + 45, 6, 0, bone["base"])


# ==========================================
# 3. LẮP RÁP CÁC KHUNG HÌNH (ANIMATION LOOP)
# ==========================================

# Ma trận thiết lập độ lệch trục Y (offset_y) cho từng bộ phận trong 4 frame
# Số âm = bay lên trên, Số dương = tụt xuống dưới
animation_data = [
    {"body": 0,  "core": 0,  "l_arm": 0,  "r_arm": 4},  # Frame 1
    {"body": -2, "core": -1, "l_arm": 2,  "r_arm": 2},  # Frame 2
    {"body": -4, "core": -2, "l_arm": 4,  "r_arm": 0},  # Frame 3 (Cơ thể lên đỉnh, tay trái tụt đáy)
    {"body": -2, "core": -1, "l_arm": 2,  "r_arm": 2},  # Frame 4
]

for frame_idx, offsets in enumerate(animation_data):
    # Tạo frame mới
    f = anim.add_frame()
    
    # Dán từng bộ phận vào frame kèm theo độ dịch chuyển (x, y)
    f.paste(cv_core, (0, offsets["core"]))
    f.paste(cv_body, (0, offsets["body"]))
    f.paste(cv_l_arm, (0, offsets["l_arm"]))
    f.paste(cv_r_arm, (0, offsets["r_arm"]))
    
    # Xử lý Hậu kỳ (Bắt buộc phải làm cho TỪNG frame riêng biệt)
    f.cleanup_jaggies()
    f.add_highlight_edge(light_dir="top_left", intensity=0.35)
    f.add_outline(thickness=1, sel_out=True)
    
    print(f"Đã render xong Frame {frame_idx + 1}/4")

# ==========================================
# 4. XUẤT FILE ANIMATION
# ==========================================
# Sẽ tạo ra 2 file: 1 file .gif (ảnh động) và 1 file .png (Spritesheet ngang)
anim.save("void_bone_boss_animated.png", scale=8)
print("Hoàn tất! Hãy mở file void_bone_boss_animated.gif để xem Boss chuyển động.")
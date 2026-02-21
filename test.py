import pixci

# 1. Khởi tạo Animation (128x128, 6 Khung hình, Tốc độ 8 FPS cho đòn đánh nhanh)
anim = pixci.Animation(128, 128, columns=6, fps=8)

# Palette
dummy = pixci.Canvas(16, 16)
bone = dummy.auto_shade("#D0D5E8", levels=3)
void = dummy.auto_shade("#B000FF", levels=3)
abyss = dummy.auto_shade("#0D0B1A", levels=2)

bone_3d = [bone["dark3"], bone["base"], bone["light2"]]
void_3d = [void["dark3"], void["base"], void["light2"]]

cx, cy = 64, 64
y_head, y_chest, y_pelvis, y_tail = 30, 60, 90, 115

# ==========================================
# 2. TẠO CÁC COMPONENT (Tái sử dụng)
# ==========================================
# --- COMPONENT A: Lõi & Hào quang ---
cv_core = pixci.Canvas(128, 128)
cv_core.fill_circle((cx, y_chest), 45, abyss["dark2"])
cv_core.fill_circle((cx, y_chest), 35, void["dark2"])
cv_core.draw_gem((cx, y_chest), 16, 24, void_3d)

# --- COMPONENT B: Thân & Đầu ---
cv_body = pixci.Canvas(128, 128)
cv_body.draw_taper(cx, y_head, y_tail, 10, 0, bone["dark1"])
for y in range(y_head + 15, y_pelvis, 10):
    cv_body.fill_rect_centered((cx, y), 16, 4, bone["base"])
cv_body.draw_taper(cx - 16, y_chest - 15, y_chest + 10, 8, 2, bone["base"])
cv_body.draw_taper(cx + 16, y_chest - 15, y_chest + 10, 8, 2, bone["base"])
cv_body.fill_rect_centered((cx, y_pelvis), 28, 8, bone["base"])
# Đầu
cv_body.draw_dome(cx, y_head, 28, 20, bone["base"])
cv_body.fill_rect_centered((cx, y_head + 8), 20, 12, bone["base"])
cv_body.fill_rect_centered((cx, y_head + 16), 14, 6, bone["dark1"])
cv_body.fill_rect_centered((cx - 6, y_head + 4), 6, 6, abyss["dark2"])
cv_body.fill_rect_centered((cx + 6, y_head + 4), 6, 6, abyss["dark2"])
cv_body.fill_circle((cx - 6, y_head + 4), 1, void["light2"])
cv_body.fill_circle((cx + 6, y_head + 4), 1, void["light2"])
cv_body.draw_taper(cx - 16, y_head - 8, y_head + 2, 6, 10, bone["dark1"]) 
cv_body.draw_taper(cx - 24, y_head - 22, y_head - 6, 0, 8, bone["base"])  
cv_body.draw_taper(cx + 16, y_head - 8, y_head + 2, 6, 10, bone["dark1"]) 
cv_body.draw_taper(cx + 24, y_head - 22, y_head - 6, 0, 8, bone["base"])  

# --- COMPONENT C & D: Tay Trái (Nền) & Tay Phải (Vũ khí chính) ---
cv_l_arm = pixci.Canvas(128, 128)
cv_l_arm.draw_sphere((cx - 44, y_chest - 15), 14, bone_3d, light_dir="top_left")
cv_l_arm.draw_taper(cx - 60, y_chest + 20, y_chest + 55, 6, 0, bone["base"])
cv_l_arm.draw_taper(cx - 50, y_chest + 24, y_chest + 65, 6, 0, bone["light2"])
cv_l_arm.draw_taper(cx - 40, y_chest + 20, y_chest + 45, 6, 0, bone["base"])

cv_r_arm = pixci.Canvas(128, 128)
cv_r_arm.draw_sphere((cx + 44, y_chest - 15), 14, bone_3d, light_dir="top_left")
cv_r_arm.draw_taper(cx + 60, y_chest + 20, y_chest + 55, 6, 0, bone["base"])
cv_r_arm.draw_taper(cx + 50, y_chest + 24, y_chest + 65, 6, 0, bone["light2"])
cv_r_arm.draw_taper(cx + 40, y_chest + 20, y_chest + 45, 6, 0, bone["base"])

# --- COMPONENT E: Hiệu ứng Sóng xung kích (Chỉ xuất hiện khi va chạm) ---
cv_fx = pixci.Canvas(128, 128)
# Vẽ vệt chém ngang dưới mặt đất tại vị trí tay phải giáng xuống (X = 114, Y = 125)
cv_fx.fill_ellipse_anchored((110, 125), 24, 6, void["light2"], align="bottom")
cv_fx.fill_ellipse_anchored((110, 125), 14, 8, void["base"], align="bottom")
cv_fx.fill_circle((110, 115), 4, void["light2"]) # Tia lửa bắn lên

# ==========================================
# 3. KỊCH BẢN HÀNH ĐỘNG (ACTION MATRIX)
# ==========================================
# Cấu trúc: [Thân, Lõi, Tay Trái, Tay Phải, Hiệu ứng (True/False)]
# Trục Y: Âm (-) là bay lên cao, Dương (+) là thụt xuống thấp
attack_sequence = [
    {"body": 0,  "core": 0,  "l_arm": 0,   "r_arm": 0,   "fx": False}, # F1: Đứng im chờ đợi
    {"body": -4, "core": -2, "l_arm": +2,  "r_arm": -12, "fx": False}, # F2: LẤY ĐÀ - Nhô người lên, vung tay phải tít lên trời (-12)
    {"body": -6, "core": -3, "l_arm": +4,  "r_arm": -18, "fx": False}, # F3: ĐỈNH ĐIỂM - Tay phải vung cao nhất chuẩn bị chém
    {"body": +4, "core": +2, "l_arm": -4,  "r_arm": +15, "fx": True }, # F4: VA CHẠM - Đập mạnh xuống (+15), cơ thể nén xuống (+4) do phản lực, BẬT FX
    {"body": +2, "core": +1, "l_arm": -2,  "r_arm": +15, "fx": False}, # F5: GIỮ ĐÒN - Tay vẫn ghim dưới đất, dư chấn tàn lụi
    {"body": -2, "core": -1, "l_arm": +2,  "r_arm": +6,  "fx": False}, # F6: THU HỒI - Rút tay lên từ từ về dáng chuẩn
]

for frame_idx, state in enumerate(attack_sequence):
    f = anim.add_frame()
    
    # Layering: Background (Hào quang) -> Thân -> Tay -> FX
    f.paste(cv_core, (0, state["core"]))
    f.paste(cv_body, (0, state["body"]))
    f.paste(cv_l_arm, (0, state["l_arm"]))
    f.paste(cv_r_arm, (0, state["r_arm"]))
    
    # Dán hiệu ứng vụn vỡ nếu là khung hình Va chạm (Frame 4)
    if state["fx"]:
        f.paste(cv_fx, (0, 0)) # FX đã căn chuẩn tọa độ tĩnh
    
    # Hậu kỳ siêu mượt cho từng frame
    f.cleanup_jaggies()
    f.add_highlight_edge(light_dir="top_left", intensity=0.35)
    f.add_outline(thickness=1, sel_out=True)
    
    print(f"Đã render xong Frame Tấn công {frame_idx + 1}/6")

# ==========================================
# 4. XUẤT FILE ANIMATION
# ==========================================
anim.save("void_boss_attack.png", scale=8)
print("Hoàn tất! Hãy mở file void_boss_attack.gif để chiêm ngưỡng cú đập hủy diệt.")
import pixci
import math
import os

# Tạo thư mục để chứa các frame ảnh
output_dir = "boss_animation"
os.makedirs(output_dir, exist_ok=True)

# Cấu hình Animation
num_frames = 8

print("Đang vận nội công rèn 8 khung hình Animation...")

for frame in range(num_frames):
    # LƯU Ý: Phải khởi tạo Canvas MỚI ở mỗi frame để ảnh không bị đè lên nhau
    canvas = pixci.Canvas(96, 96)
    cx, cy = canvas.get_center()

    # 1. TÍNH TOÁN CHUYỂN ĐỘNG (Dùng hàm Sin/Cos để tạo độ nhấp nhô)
    # Tính góc theta từ 0 đến 2*Pi cho một chu kỳ lặp hoàn hảo
    theta = (frame / num_frames) * 2 * math.pi 
    
    # Biên độ dao động (tính bằng pixel)
    bob_y = int(math.sin(theta) * 2)           # Thân nhấp nhô 2px
    crystal_y = int(math.cos(theta) * 3)       # Ngọc bay lệch pha thân 3px
    hands_y = int(math.sin(theta - 1.0) * 2)   # Tay bay trễ nhịp hơn thân
    pulse = int((math.sin(theta * 2) + 1) / 2) # Lõi đập (0 hoặc 1 px)

    # 2. HỆ THỐNG MÀU SẮC (Giữ nguyên độ ngầu)
    armor = canvas.auto_shade("#151520", levels=3)
    glow  = canvas.auto_shade("#FF0055", levels=3)
    gold  = canvas.auto_shade("#D4AF37", levels=2)
    aura  = canvas.auto_shade("#4A0080", levels=2)

    armor_3d = [armor["dark3"], armor["base"], armor["light2"]]
    gold_3d  = [gold["dark2"], gold["base"], gold["light2"]]
    glow_3d  = [glow["dark3"], glow["base"], glow["light2"]]

    # 3. TỌA ĐỘ NEO (Áp dụng chuyển động)
    y_ground = canvas.get_ground(margin=6)     # Mặt đất CỐ ĐỊNH
    y_waist = 60 + bob_y                       # Eo nhấp nhô
    y_neck = 35 + bob_y                        # Cổ nhấp nhô

    # 4. QUẢN LÝ LAYER
    canvas.add_layer("aura")
    canvas.add_layer("body")
    canvas.add_layer("head")
    canvas.add_layer("arms")

    # ==========================================
    # --- LAYER 1: HÀO QUANG & TINH THỂ BAY ---
    canvas.set_layer("aura")
    # Bóng dưới đất không di chuyển, chỉ co giãn nhẹ theo frame (tạo cảm giác thở)
    shadow_w = 28 + int(math.sin(theta)*2)
    canvas.fill_ellipse_anchored((cx, y_ground), shadow_w, 6, armor["dark3"], align="bottom")

    # Hào quang dính theo cổ
    canvas.fill_circle((cx, y_neck + 5), 26, aura["dark2"])
    canvas.fill_circle((cx, y_neck + 5), 22, aura["base"])
    canvas.fill_circle((cx, y_neck + 5), 18, armor["dark3"])

    # Tinh thể ma thuật (áp dụng crystal_y)
    canvas.draw_gem((cx - 40, y_neck - 5 + crystal_y), 8, 14, glow_3d)
    canvas.draw_gem((cx + 40, y_neck - 5 + crystal_y), 8, 14, glow_3d)

    # --- LAYER 2: THÂN TRUNG TÂM ---
    canvas.set_layer("body")
    # Vòi rồng: Đáy bám đất, đỉnh nối với eo đang nhấp nhô
    canvas.draw_taper(cx, y_waist, y_ground - 4, 18, 0, armor["dark2"])
    
    # Thân trên
    canvas.draw_taper(cx, y_neck, y_waist, 44, 20, armor["base"])

    # Cầu vai
    canvas.draw_dome(cx - 26, y_neck + 10, 28, 20, armor["dark1"])
    canvas.draw_dome(cx + 26, y_neck + 10, 28, 20, armor["dark1"])

    # Gai nhọn
    canvas.draw_taper(cx - 26, y_neck - 23, y_neck + 5, 0, 8, gold["base"])
    canvas.draw_taper(cx + 26, y_neck - 23, y_neck + 5, 0, 8, gold["base"])

    # Lõi năng lượng (áp dụng nhịp đập Pulse làm lõi to nhỏ)
    core_y = y_neck + 13
    canvas.fill_circle((cx, core_y), 10, armor["dark3"]) 
    canvas.draw_gem((cx, core_y), 8 + pulse, 10 + pulse, glow_3d)

    # --- LAYER 3: ĐẦU & VƯƠNG MIỆN ---
    canvas.set_layer("head")
    canvas.fill_circle((cx, y_neck - 9), 11, armor["dark2"])
    canvas.fill_rect_centered((cx, y_neck - 11), 14, 4, glow["light2"])

    # Vương miện
    canvas.draw_taper(cx, y_neck - 29, y_neck - 17, 0, 4, gold["light2"])       
    canvas.draw_taper(cx - 8, y_neck - 25, y_neck - 13, 0, 4, gold["base"])    
    canvas.draw_taper(cx + 8, y_neck - 25, y_neck - 13, 0, 4, gold["base"])    

    # --- LAYER 4: HAI TAY LƠ LỬNG ---
    canvas.set_layer("arms")
    arm_y = y_waist + hands_y # Áp dụng hands_y
    
    canvas.draw_sphere((cx - 36, arm_y), 12, armor_3d, light_dir="top_left")
    canvas.draw_sphere((cx + 36, arm_y), 12, armor_3d, light_dir="top_left")

    canvas.draw_taper(cx - 42, arm_y + 8, arm_y + 24, 6, 0, gold["base"])
    canvas.draw_taper(cx - 30, arm_y + 8, arm_y + 20, 5, 0, gold["base"])
    canvas.draw_taper(cx + 42, arm_y + 8, arm_y + 24, 6, 0, gold["base"])
    canvas.draw_taper(cx + 30, arm_y + 8, arm_y + 20, 5, 0, gold["base"])

    # ==========================================
    # 5. HẬU KỲ VÀ LƯU FRAME
    # ==========================================
    canvas.merge_layers("aura", "body")
    canvas.merge_layers("aura", "arms")
    canvas.merge_layers("aura", "head")
    canvas.set_layer("aura")

    canvas.cleanup_jaggies()
    canvas.add_highlight_edge(light_dir="top_left", intensity=0.3)
    canvas.add_outline(thickness=1, sel_out=True)

    # Lưu định dạng frame_00.png, frame_01.png...
    filename = f"{output_dir}/frame_{frame:02d}.png"
    canvas.save(filename, scale=8) # Phóng to x8
    print(f"  -> Đã xuất: {filename}")

print("HOÀN TẤT! Hãy mở thư mục 'boss_animation' và xem lướt qua các ảnh.")
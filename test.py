import pixci

# 1. Khởi tạo Canvas (48x48 - Kích thước chuẩn cho icon HD Minecraft)
canvas = pixci.Canvas(48, 48)

# 2. Hệ thống Màu (Magma & Obsidian Theme)
# Màu lưỡi kiếm: Hợp kim đen + Dung nham
obsidian = canvas.auto_shade("#2A1C35", levels=2) 
lava     = canvas.auto_shade("#FF4500", levels=3) # Cam đỏ rực
gold     = canvas.auto_shade("#FFD700", levels=2) # Vàng lót tay
wood     = canvas.auto_shade("#5D4037", levels=2) # Gỗ tay cầm

# 3. Hàm hỗ trợ vẽ đường chéo "Bậc thang" (Pixel-Perfect Diagonal)
def draw_diagonal_block(start_x, start_y, length, color, offset_x=0, offset_y=0):
    """
    Vẽ một dải pixel chéo từ trái-dưới lên phải-trên.
    offset_x, offset_y: Dùng để làm dày thanh kiếm.
    """
    for i in range(length):
        # Tọa độ chéo: x tăng, y giảm
        px = start_x + i + offset_x
        py = start_y - i + offset_y
        canvas.set_pixel((px, py), color)

# ==========================================
# THIẾT KẾ KIẾM CHÉO (MC STYLE)
# ==========================================

# Điểm gốc bắt đầu vẽ (Góc dưới bên trái)
base_x, base_y = 10, 38

# --- BƯỚC 1: TAY CẦM (HANDLE) ---
# Vẽ lõi tay cầm
draw_diagonal_block(base_x, base_y, 9, wood["base"])
# Vẽ bóng đổ phía dưới tay cầm (để tạo khối tròn)
draw_diagonal_block(base_x + 1, base_y, 8, wood["dark1"], offset_x=0, offset_y=0)

# Đốc kiếm (Pommel) - Khối tròn ở đuôi
canvas.fill_rect((base_x - 2, base_y + 1), (base_x + 1, base_y + 4), gold["dark1"])
canvas.set_pixel((base_x - 1, base_y + 2), gold["light1"]) # Điểm sáng

# --- BƯỚC 2: KIẾM CÁCH (CROSSGUARD - CÁNH CHẮN) ---
# Điểm giao nhau giữa tay cầm và lưỡi kiếm
guard_x = base_x + 9
guard_y = base_y - 9

# Vẽ thanh chắn chéo ngược lại (Vuông góc với kiếm)
# Cánh trên (hướng lên góc 10h)
for i in range(1, 6):
    canvas.set_pixel((guard_x - i, guard_y - i), gold["base"])
    canvas.set_pixel((guard_x - i + 1, guard_y - i), gold["light1"]) # Viền sáng

# Cánh dưới (hướng xuống góc 4h)
for i in range(1, 6):
    canvas.set_pixel((guard_x + i, guard_y + i), gold["base"])
    canvas.set_pixel((guard_x + i, guard_y + i - 1), gold["dark1"]) # Viền tối

# Ngọc tâm kiếm cách
canvas.fill_rect((guard_x - 1, guard_y - 1), (guard_x + 2, guard_y + 2), lava["dark2"])
canvas.set_pixel((guard_x, guard_y), lava["light2"])

# --- BƯỚC 3: LƯỠI KIẾM (BLADE) ---
# Điểm bắt đầu lưỡi kiếm
blade_start_x = guard_x + 2
blade_start_y = guard_y - 2
blade_len = 16

# Layer 1: Lưỡi sắc cạnh trên (Highlight - Màu sáng nhất)
draw_diagonal_block(blade_start_x, blade_start_y, blade_len, obsidian["light2"], offset_y=-1)

# Layer 2: Thân kiếm chính (Core - Màu nền)
draw_diagonal_block(blade_start_x, blade_start_y, blade_len + 1, obsidian["base"])

# Layer 3: Sống kiếm (Shadow - Màu tối nhất tạo độ dày)
draw_diagonal_block(blade_start_x, blade_start_y, blade_len, obsidian["dark1"], offset_x=1)

# --- BƯỚC 4: HIỆU ỨNG DUNG NHAM (LAVA RUNES) ---
# Vẽ các đường nứt magma rực sáng trên thân kiếm
# Cách vẽ: Chọn ngẫu nhiên hoặc cố định một số điểm trên thân kiếm để tô màu cam
rune_positions = [2, 5, 6, 9, 10, 13] # Các đốt trên thân kiếm sẽ phát sáng
for i in rune_positions:
    rx = blade_start_x + i
    ry = blade_start_y - i
    # Vẽ đốm lửa vào chính giữa thân kiếm
    canvas.set_pixel((rx, ry), lava["light1"])
    # Hiệu ứng lan tỏa nhẹ ra xung quanh
    if i % 2 == 0:
        canvas.set_pixel((rx + 1, ry), lava["base"]) # Lan sang phải

# --- BƯỚC 5: MŨI KIẾM (TIP) ---
# Làm nhọn mũi kiếm kiểu pixel
tip_x = blade_start_x + blade_len
tip_y = blade_start_y - blade_len
canvas.set_pixel((tip_x, tip_y - 1), obsidian["light2"]) # Đỉnh nhọn
canvas.set_pixel((tip_x + 1, tip_y), obsidian["dark1"])  # Cạnh dưới

# ==========================================
# 4. HẬU KỲ (POST-PROCESSING)
# ==========================================
# Khử răng cưa (Quan trọng cho đường chéo pixel)
canvas.cleanup_jaggies()

# Thêm vầng sáng bao quanh kiếm (Enchanted effect)
canvas.add_outline(thickness=1, sel_out=True) 

# Lưu file (Scale 12 để nhìn rõ từng pixel khối vuông vức)
canvas.save("mc_style_magma_blade.png", scale=12)
print("Đã chế tác xong: mc_style_magma_blade.png")
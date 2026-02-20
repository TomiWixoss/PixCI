"""
Demo: Cây nấm viết theo kiểu AI-native (Semantic Variables + Anchor Points)
Con người đọc code này sẽ thấy dài dòng, nhưng AI tạo ra nó sẽ KHÔNG BAO GIỜ bị lệch tọa độ.

So sánh với mushroom_final.py (hardcode):
  - mushroom_final.py: fill_rect((13, 20), (18, 28), "S1")  → AI dễ quên 13, 18 là gì
  - demo_ai_native.py: fill_rect_centered((cx, stem_cy), stem_w, stem_h, "S1") → AI hiểu rõ ràng
"""
import pixci

# ╔══════════════════════════╗
# ║ BƯỚC 1: PALETTE          ║
# ╚══════════════════════════╝
canvas = pixci.Canvas(32, 32)
canvas.add_layer("grass")
canvas.add_layer("mushroom")

canvas.add_palette({
    "R1": "#E62E2D",     # Đỏ base
    "R2": "#B31C26",     # Đỏ shadow (warmer/darker) 
    "R3": "#FF6B6B",     # Đỏ highlight (cooler/lighter)
    "W1": "#FFFFFF",     # Trắng tinh
    "W2": "#E0E0E0",     # Trắng shadow
    "S1": "#E8D5C4",     # Thân nấm sáng
    "S2": "#B59C8D",     # Thân nấm tối
    "G1": "#1E1A20",     # Gầm nấm
    "C1": "#45B363",     # Cỏ sáng
    "C2": "#2A7A44",     # Cỏ tối
})

# ╔══════════════════════════════════════╗
# ║ BƯỚC 2: SPATIAL PLANNING             ║
# ║ Khai báo TẤT CẢ vị trí bằng biến    ║
# ╚══════════════════════════════════════╝
cx, cy = canvas.get_center()       # (16, 16)
ground_y = canvas.get_ground()     # 29

# -- Cỏ --
grass_y_start = ground_y - 1       # 28
grass_y_end = 31
grass_half_w = 13

# -- Thân nấm --
stem_w = 6
stem_h = 9
stem_bottom = ground_y            # Thân chạm mặt đất
stem_top = stem_bottom - stem_h   # Đỉnh thân = 20
stem_cy = stem_bottom - stem_h // 2

# -- Mũ nấm --
cap_w = 24
cap_h = 13
cap_bottom = stem_top              # Mũ đặt trên đỉnh thân
cap_top = cap_bottom - cap_h + 1   # Đỉnh mũ = 8

# -- Gầm nấm --
gill_y = stem_top                  # Nằm tại đỉnh thân
gill_rx = 6

# -- Light direction --
light_dir = "top_left"  # Nguồn sáng: góc trên-trái

# ╔══════════════════════════════════════╗
# ║ BƯỚC 3+4: LAYERS + BLOCKING          ║
# ╚══════════════════════════════════════╝

# --- Layer: Cỏ ---
canvas.set_layer("grass")
canvas.draw_rows([
    (grass_y_start,     cx - grass_half_w,     cx + grass_half_w - 1, "C2"),
    (grass_y_start + 1, cx - grass_half_w - 2, cx + grass_half_w + 1, "C1"),
    (grass_y_start + 2, cx - grass_half_w - 3, cx + grass_half_w + 2, "C1"),
    (grass_y_end,       cx - grass_half_w - 2, cx + grass_half_w + 1, "C2"),
])
canvas.set_pixel((cx - grass_half_w + 2, grass_y_start), "C1")   # Điểm sáng cạnh trái
canvas.set_pixel((cx + grass_half_w,     grass_y_start), "C1")   # Điểm sáng cạnh phải
canvas.fill_dither(
    (cx - grass_half_w + 2, grass_y_start + 1, cx + grass_half_w, grass_y_start + 2),
    color1="C1", color2="C2", pattern="checkered"
)

# --- Layer: Nấm ---
canvas.set_layer("mushroom")

# Thân nấm - dùng fill_rect_centered tự tính tọa độ từ tâm
canvas.fill_rect_centered((cx, stem_cy), stem_w, stem_h, "S1")
# Nửa phải tối hơn
stem_left, stem_right = canvas.span(cx, stem_w)
canvas.fill_rect((cx + 1, stem_top), (stem_right, stem_bottom), "S2")
# Chân toe ra
canvas.set_pixel((stem_left - 1, stem_bottom), "S1")
canvas.set_pixel((stem_right + 1, stem_bottom), "S2")

# Gầm nấm
canvas.fill_ellipse(center=(cx, gill_y), rx=gill_rx, ry=1, color="G1")

# Mũ nấm - dùng draw_dome (semantic shape)
canvas.draw_dome(center_x=cx, base_y=cap_bottom, width=cap_w, height=cap_h, color="R1")

# ╔══════════════════════════════════════╗
# ║ BƯỚC 5: SHADING & HIGHLIGHT          ║
# ╚══════════════════════════════════════╝
canvas.alpha_lock = True

# Shadow ở đáy mũ nấm + cạnh PHẢI (xa nguồn sáng top_left)
canvas.draw_rows([
    (cap_bottom,     cx - 5, cx + 9, "R2"),   # Đáy = shadow
    (cap_bottom - 1, cx - 4, cx + 10, "R2"),  # Gần đáy
])
# Shadow cạnh phải
shadow_x_start = cx + 8
canvas.fill_rect((shadow_x_start, cap_top + 3), (shadow_x_start + 3, cap_bottom - 2), "R2")
canvas.draw_rows([
    (cap_top + 1, cx + 6, cx + 9,  "R2"),
    (cap_top + 2, cx + 8, cx + 10, "R2"),
])

# Highlight ở đỉnh + cạnh TRÁI (gần nguồn sáng)
canvas.draw_rows([
    (cap_top + 1, cx - 6, cx - 2, "R3"),   # Đỉnh sáng
    (cap_top + 2, cx - 8, cx - 4, "R3"),   # Band sáng rộng
    (cap_top + 3, cx - 9, cx - 7, "R3"),   # Nhỏ dần
])

# Đốm trắng (chi tiết đặc trưng nấm)
canvas.fill_circle(center=(cx - 5, cap_bottom - 4), radius=2, color="W1")
canvas.set_pixel((cx - 4, cap_bottom - 3), "W2")  # Shadow của đốm

canvas.fill_circle(center=(cx + 5, cap_bottom - 3), radius=1, color="W1")
canvas.set_pixel((cx + 5, cap_bottom - 2), "W2")

# Đốm nhỏ phối cảnh
canvas.fill_ellipse(center=(cx, cap_top + 5), rx=1, ry=0, color="W1")
canvas.fill_ellipse(center=(cx - 9, cap_bottom - 3), rx=0, ry=1, color="W1")
canvas.fill_ellipse(center=(cx + 8, cap_bottom - 5), rx=0, ry=1, color="W1")

canvas.alpha_lock = False

# ╔══════════════════════════════════════╗
# ║ BƯỚC 6+7: POST-PROCESS & SAVE        ║
# ╚══════════════════════════════════════╝
canvas.apply_shadow_mask(
    center=(cx, cy), radius=14, 
    light_dir=light_dir, intensity=0.3, shadow_color="#100010"
)

canvas.merge_layers(base_layer="grass", top_layer="mushroom")
canvas.set_layer("grass")
canvas.add_outline(thickness=1, sel_out=True, darkness=0.35, saturation_boost=1.3)
canvas.cleanup_jaggies()

canvas.save("mushroom_ai_native.png", scale=10)
print("Saved: mushroom_ai_native.png")

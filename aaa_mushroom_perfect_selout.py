import pixci

canvas = pixci.Canvas(32, 32)
canvas.add_layer("grass")
canvas.add_layer("mushroom")

# Bảng màu
canvas.add_palette({
    "BG": "#00000000",   
    "R1": "#E62E2D", "R2": "#B31C26", "R3": "#FF6B6B", 
    "W1": "#FFFFFF", "W2": "#E0E0E0", 
    "S1": "#E8D5C4", "S2": "#B59C8D", 
    "G1": "#1E1A20", 
    "C1": "#45B363", "C2": "#2A7A44", 
})

# ==========================================
# LAYER: GRASS
# ==========================================
canvas.set_layer("grass")
canvas.draw_line((6, 28), (26, 28), "C2")
canvas.draw_line((4, 29), (28, 29), "C1")
canvas.draw_line((3, 30), (29, 30), "C1")
canvas.draw_line((4, 31), (28, 31), "C2")
canvas.set_pixel((5, 28), "C1")
canvas.set_pixel((27, 28), "C1")
canvas.fill_dither((5, 29, 27, 30), color1="C1", color2="C2", pattern="checkered")

# KHÔNG TẠO OUTLINE Ở ĐÂY NỮA!

# ==========================================
# LAYER: MUSHROOM
# ==========================================
canvas.set_layer("mushroom")

# Thân nấm
canvas.fill_rect((13, 20), (18, 28), "S1")
canvas.fill_rect((17, 20), (18, 28), "S2")

# Gầm nấm
canvas.fill_ellipse(center=(16, 20), rx=6, ry=1, color="G1")

# Mũ nấm
canvas.draw_half_sphere(center=(16, 18), radius=10, palette=["R2", "R1", "R3"], light_dir="top_left")
canvas.draw_line((7, 18), (6, 19), "R2")
canvas.draw_line((24, 18), (25, 19), "R2")

# Highlight và đốm
canvas.fill_rect((11, 9), (14, 10), "W1") 
canvas.set_pixel((12, 8), "W1")
canvas.fill_circle(center=(11, 14), radius=2, color="W1")
canvas.fill_circle(center=(21, 15), radius=1, color="W1")
canvas.fill_ellipse(center=(16, 11), rx=1, ry=0, color="W1")
canvas.fill_ellipse(center=(7,  15), rx=0, ry=1, color="W1")

# Shadow mask
canvas.apply_shadow_mask(center=(16, 16), radius=14, light_dir="top_left", intensity=0.3, shadow_color="#100010")

# ==========================================
# GỘP LAYER VÀ POST-PROCESS 
# ==========================================
# Ép (Merge) toàn bộ layer "mushroom" xuống layer "grass"
canvas.merge_layers(base_layer="grass", top_layer="mushroom")

# Trỏ cọ vẽ về lại layer "grass" (bây giờ đã chứa toàn bộ bức tranh)
canvas.set_layer("grass")

# CHỈ TẠO OUTLINE ĐÚNG 1 LẦN DƯỚI CÙNG
# Sử dụng Sel-out mới (Hue-shifted), đảm bảo không còn bị màu bùn đất!
canvas.add_outline(thickness=1, sel_out=True)

# Khử răng cưa
canvas.cleanup_jaggies()

canvas.save("aaa_mushroom_perfect_selout.png", scale=10)

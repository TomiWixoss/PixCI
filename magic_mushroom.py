import pixci

# 1. Khởi tạo Canvas 32x32
canvas = pixci.Canvas(32, 32)

# 2. Sinh dải màu (Hue-shifted) từ Đỏ và Trắng
red_ramp = canvas.generate_ramp(base_color="#FF3333", steps=4, mode="hue_shift")
white_ramp = canvas.generate_ramp(base_color="#FFFFFF", steps=4)

# 3. Vẽ thân nấm (Hình trụ)
canvas.fill_cylinder(base=(16, 28), width=8, height=10, palette=white_ramp, light_dir="top_right")

# 4. Vẽ mũ nấm (Nửa khối cầu 3D, tự động có bóng râm)
canvas.draw_half_sphere(center=(16, 16), radius=12, palette=red_ramp, light_dir="top_right")

# 5. Thêm các đốm trắng trên mũ nấm (Dùng pixel_perfect để tròn trịa)
canvas.draw_circle(center=(12, 12), radius=2, color="#FFFFFF", pixel_perfect=True)
canvas.draw_circle(center=(20, 15), radius=3, color="#FFFFFF", pixel_perfect=True)

# 6. Thêm texture cỏ dưới chân bằng Dithering
canvas.fill_dither(rect=(4, 28, 28, 32), color1="#2ECC71", color2="#27AE60", pattern="checkered")

# 7. Bước cuối cùng: Bọc viền đen toàn bộ Sprite để ra chất Game Retro
canvas.add_outline(color="#000000", thickness=1)

# Lưu thành Nấm hoàn chỉnh
canvas.save("magic_mushroom.png", scale=10)

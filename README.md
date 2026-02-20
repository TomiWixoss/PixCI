# TÀI LIỆU CÔNG CỤ: PIXCI
**Tên dự án:** PixCI (Pixel CLI & Coding Interface)
**Phiên bản:** 2.0.0 (Bao gồm Core CLI & Core Package)
**Mô tả:** Bộ công cụ toàn diện (CLI + Python Library) giúp làm cầu nối giữa ảnh Pixel Art và AI (LLMs). Cho phép AI đọc hiểu, khởi tạo và chỉnh sửa ảnh pixel thông qua Văn bản (Grid) hoặc Lập trình Lệnh (Procedural Python Code) với độ chính xác tuyệt đối.

---

## 1. TỔNG QUAN
PixCI giải quyết vấn đề LLM gặp "ảo giác" khi xử lý không gian 2D bằng 2 chế độ:
1.  **Chế độ Cơ bản (Grid/Text):** Chuyển ảnh thành ma trận ký tự để AI nhìn tổng quan nhanh chóng.
2.  **Chế độ Nâng cao (Python Package):** Biến PixCI thành một thư viện Python. AI sẽ **viết code gọi các hàm của PixCI** (như toạ độ `(x, y)`, `fill_rect`, `draw_line`). Tool PixCI sau đó sẽ chạy đoạn code này để render ra ảnh cuối cùng.

---

## 2. CÀI ĐẶT
Yêu cầu: Python 3.9+

```bash
pip install -e .
```

---

## 3. THIẾT KẾ CLI (TRẢI NGHIỆM NGƯỜI DÙNG)

Các lệnh mà người dùng sẽ gõ trên Terminal của họ:

```bash
# === PHẦN CƠ BẢN ===
# 1. Chuyển ảnh thành Text Grid
pixci encode sprite.png -f grid -o output.txt

# 2. Chuyển Text Grid thành Ảnh
pixci decode output.txt --scale 10 -o result.png


# === PHẦN NÂNG CẤP (Procedural Generation) ===
# 3. Biến một ảnh PNG có sẵn thành Code Python
pixci encode sprite.png -f code -o generated_sprite.py
# (Output là 1 file code chứa các lệnh set_pixel() tái hiện lại ảnh)

# 4. Khởi tạo một dự án Code trống cho AI
pixci init --size 32x32 -f code -o blank_canvas.py
# (Mở file này ra, copy ném cho AI nhờ vẽ thêm)

# 5. Chạy file Python của AI để kết xuất thành ảnh PNG
pixci run ai_script.py --scale 10
# (Lệnh này sẽ import thư viện pixci, chạy file script và lưu ảnh)
```

---

## 4. TÀI LIỆU API CHO AI (Dùng để mớm Prompt)

Để AI có thể sử dụng PixCI, bạn chỉ cần ném cho AI đoạn tài liệu ngắn gọn này (System Prompt):

> **System Prompt gửi AI:**
> "Bạn là một Pixel Artist bậc thầy. Hãy dùng thư viện `pixci` bằng Python để vẽ.
> Thư viện `pixci` hỗ trợ các hàm nâng cao:
> 1. Sinh dải màu tự động: `generate_ramp(base_color, steps, mode="hue_shift")`
> 2. Khối 3D có ánh sáng: `draw_sphere(center, radius, palette, light_dir)`, `draw_half_sphere`, `fill_cylinder`
> 3. Hình học 2D: `fill_rect`, `draw_circle(..., pixel_perfect=True)`, `draw_line`, `draw_curve(..., pixel_perfect=True)`
> 4. Tạo hiệu ứng sần sùi: `fill_dither(rect, color1, color2, pattern="25_percent" | "50_percent")`
> 5. Bọc viền đen toàn bộ: `add_outline(color, thickness)`
> Hãy viết code để tạo tác phẩm."

**Ví dụ Code AI (Vẽ Nấm Ma Thuật):**
```python
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
```

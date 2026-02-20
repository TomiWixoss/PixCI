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

**Ví dụ Code AI (Vẽ Nấm Ma Thuật chuẩn AAA):**
```python
import pixci

# 1. Khởi tạo Canvas 32x32
canvas = pixci.Canvas(32, 32)

# 2. Định nghĩa Bảng màu thủ công
canvas.add_palette({
    "BG": "#00000000",   # Trong suốt
    "R1": "#E62E2D",     # Đỏ cơ bản
    "R2": "#B31C26",     # Đỏ tối (Bóng tối)
    "R3": "#FF6B6B",     # Đỏ sáng (Highlight)
    "W1": "#FFFFFF",     # Trắng tinh
    "W2": "#E0E0E0",     # Trắng xám (Bóng của đốm trắng)
    "S1": "#E8D5C4",     # Màu thân nấm sáng
    "S2": "#B59C8D",     # Màu thân nấm tối
    "G1": "#1E1A20",     # Gầm nấm (Rất tối)
    "C1": "#45B363",     # Cỏ sáng
    "C2": "#2A7A44",     # Cỏ tối
})

# 3. Vẽ bãi cỏ (Organic Shape thay vì hình chữ nhật)
canvas.draw_line((6, 28), (26, 28), "C2")
canvas.draw_line((4, 29), (28, 29), "C1")
canvas.draw_line((3, 30), (29, 30), "C1")
canvas.draw_line((4, 31), (28, 31), "C2")
canvas.set_pixel((5, 28), "C1")
canvas.set_pixel((27, 28), "C1")
canvas.fill_dither((5, 29, 27, 30), color1="C1", color2="C2", pattern="checkered")

# 4. Vẽ Thân nấm (Có độ cong nhẹ ở gốc)
canvas.fill_rect((13, 20), (18, 28), "S1")
canvas.fill_rect((17, 20), (18, 28), "S2")
canvas.set_pixel((12, 28), "S1")
canvas.set_pixel((19, 28), "S2")

# 5. Vẽ Gầm nấm (Gills - Tạo chiều sâu 3D)
canvas.draw_line((10, 20), (21, 20), "G1")
canvas.draw_line((8, 19), (23, 19), "G1")

# 6. Vẽ Mũ nấm (Sử dụng half_sphere nhưng làm phẳng đáy)
canvas.draw_half_sphere(center=(16, 18), radius=10, palette=["R2", "R1", "R3"], light_dir="top_left")
canvas.draw_line((7, 18), (6, 19), "R2")
canvas.draw_line((24, 18), (25, 19), "R2")

# Điểm xuyết Highlight
canvas.fill_rect((11, 9), (14, 10), "W1") 
canvas.set_pixel((12, 8), "W1")

# 7. Vẽ các đốm trắng (Dùng fill_circle thay vì draw_circle để đặc ruột)
canvas.fill_circle(center=(11, 14), radius=2, color="W1")
canvas.set_pixel((12, 15), "W2")
canvas.fill_circle(center=(21, 15), radius=1, color="W1")
canvas.set_pixel((21, 16), "W2")
canvas.set_pixel((16, 11), "W1")
canvas.set_pixel((7, 15), "W1")
canvas.set_pixel((24, 13), "W1")

# 8. Áp dụng lớp phủ bóng đổ (Post-process)
canvas.apply_shadow_mask(center=(16, 16), radius=14, light_dir="top_left", intensity=0.3, shadow_color="#100010")

# 9. Bao viền (Outline) và xóa răng cưa
canvas.add_outline(color="#110B11", thickness=1)
canvas.cleanup_jaggies(outline_color="#110B11")

# 10. Xuất file
canvas.save("aaa_mushroom.png", scale=10)
```

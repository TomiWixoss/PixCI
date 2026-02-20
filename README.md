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

```python
# HƯỚNG DẪN SỬ DỤNG THƯ VIỆN PIXCI CHO AI
import pixci

# 1. Khởi tạo
canvas = pixci.Canvas(width=32, height=32)

# 2. Định nghĩa màu (Hex/RGBA)
canvas.add_palette({
    "1": "#000000", # Đen viền
    "2": "#FF0000", # Đỏ
})

# 3. Vẽ bằng tọa độ (Gốc 0,0 ở góc trái trên cùng)
canvas.set_pixel((15, 15), "2")
canvas.fill_rect((0, 0), (5, 5), "1") # Hình chữ nhật
canvas.draw_line((0, 0), (10, 10), "2") # Đường chéo

# 4. Lưu lại
canvas.save("result", scale=10) # Lưu file result.png
```

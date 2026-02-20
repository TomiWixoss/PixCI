# PixCI Smart Code - Generated from test_encode_input.png
# Canvas: 16x16 pixels, 3 colors
# Coordinate system: (0,0)=top-left, X→right, Y↓down
#
# X ruler:  0    5    10   15   
# Y ruler: 0=top, 4=quarter, 8=middle, 12=three-quarter, 15=bottom
#
# HƯỚNG DẪN: Mỗi hàm dưới đây vẽ ra MỘT PHẦN của ảnh.
# AI có thể CHỈNH SỬA bất kỳ tham số nào để thay đổi hình dạng, màu sắc, vị trí.
# Xem README.md để biết đầy đủ các hàm PixCI hỗ trợ.

import pixci

canvas = pixci.Canvas(16, 16)

# === BẢNG MÀU ===
canvas.add_palette({
    "C01": "#FF0000FF",  # đỏ/hồng, tối
    "C02": "#00FF00FF",  # xanh lá, tối
    "C03": "#0000FFFF",  # xanh dương/tím, tối
})

# === KHỐI CHỮ NHẬT (vùng đặc) ===
canvas.fill_rect((2, 2), (8, 5), "C01")  # 7x4 block
canvas.fill_rect((4, 7), (12, 10), "C02")  # 9x4 block

# === DÒNG NGANG (sculpt hình dạng) ===
# Format: (y, x_start, x_end, color)
# y tăng = xuống dưới, x tăng = sang phải
canvas.draw_rows([(12, 7, 8, "C03")])

canvas.save("test_encoded.png", scale=10)

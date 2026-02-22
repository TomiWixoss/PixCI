# Hướng dẫn Build PixCI thành File .EXE

Tài liệu này hướng dẫn cách build PixCI thành file .exe để có thể chạy ở mọi nơi trên Windows mà không cần cài đặt Python.

## Yêu cầu

- Python 3.9 trở lên
- Windows OS
- PyInstaller

## Cài đặt Dependencies

```bash
pip install -r build_requirements.txt
```

Hoặc cài đặt trực tiếp:

```bash
pip install pyinstaller pillow typer rich
```

## Build GUI Application

Build PixCI GUI (giao diện đồ họa):

```bash
python build_exe.py --mode gui
```

File output: `dist/PixCI.exe`

## Build CLI Tool

Build PixCI CLI (công cụ dòng lệnh):

```bash
python build_exe.py --mode cli
```

File output: `dist/pixci-cli.exe`

## Build Cả Hai

Build cả GUI và CLI cùng lúc:

```bash
python build_exe.py --mode both
```

Files output:
- `dist/PixCI.exe` (GUI)
- `dist/pixci-cli.exe` (CLI)

## Sử dụng File .EXE

### GUI Application

1. Copy file `PixCI.exe` đến bất kỳ đâu trên máy tính
2. Double-click để chạy
3. Giao diện GUI sẽ hiện ra với các tab:
   - Encode: Chuyển ảnh sang text/PXVG
   - Decode: Chuyển text/PXVG sang ảnh
   - Run Script: Chạy Python script
   - Quick Run: Dán code và render ngay

### CLI Tool

1. Copy file `pixci-cli.exe` đến thư mục bạn muốn
2. Mở Command Prompt hoặc PowerShell tại thư mục đó
3. Chạy các lệnh:

```bash
# Encode ảnh sang text
pixci-cli.exe encode input.png -o output.txt

# Encode sang PXVG
pixci-cli.exe encode input.png -o output.pxvg.xml -f pxvg

# Decode text sang ảnh
pixci-cli.exe decode input.txt -o output.png --scale 10

# Decode PXVG sang ảnh
pixci-cli.exe decode input.pxvg.xml -o output.png --scale 10

# Khởi tạo canvas rỗng
pixci-cli.exe init --size 32x32 -o canvas.txt

# Chạy Python script
pixci-cli.exe run script.py --scale 10
```

## Thêm vào PATH (Optional)

Để có thể chạy `pixci-cli.exe` từ bất kỳ đâu:

1. Copy `pixci-cli.exe` vào một thư mục cố định (VD: `C:\Tools\`)
2. Thêm thư mục đó vào System PATH:
   - Mở System Properties → Advanced → Environment Variables
   - Tìm biến PATH trong System Variables
   - Thêm đường dẫn `C:\Tools\` vào PATH
3. Mở Command Prompt mới và gõ `pixci-cli` từ bất kỳ đâu

## Troubleshooting

### Lỗi "Failed to execute script"

- Đảm bảo tất cả dependencies đã được cài đặt
- Thử build lại với flag `--debug` để xem log chi tiết

### File .exe quá lớn

- File .exe sẽ khoảng 50-100MB vì chứa toàn bộ Python runtime và dependencies
- Đây là bình thường với PyInstaller
- Nếu muốn giảm kích thước, có thể dùng UPX compression:

```bash
pip install pyinstaller[encryption]
```

Sau đó thêm `--upx-dir=path/to/upx` vào build script

### Antivirus cảnh báo

- Một số antivirus có thể cảnh báo file .exe do PyInstaller
- Đây là false positive phổ biến
- Thêm exception trong antivirus hoặc submit file để whitelist

## Build Options Nâng cao

Chỉnh sửa file `build_exe.py` để tùy chỉnh:

- `--onefile`: Tạo một file .exe duy nhất (mặc định)
- `--onedir`: Tạo thư mục chứa .exe và dependencies (nhỏ hơn)
- `--windowed`: Không hiện console (cho GUI)
- `--console`: Hiện console (cho CLI)
- `--icon=icon.ico`: Thêm icon cho .exe
- `--add-data`: Thêm file data (textures, palettes, etc.)

## Distribution

Khi phân phối file .exe:

1. Test trên máy Windows sạch (không có Python)
2. Đóng gói cùng README và LICENSE
3. Có thể tạo installer bằng NSIS hoặc Inno Setup
4. Upload lên GitHub Releases hoặc website

## Notes

- File .exe chỉ chạy trên Windows
- Để build cho macOS/Linux, cần build trên hệ điều hành tương ứng
- PyInstaller không hỗ trợ cross-compilation
- File .exe là standalone, không cần cài Python

## Support

Nếu gặp vấn đề khi build, kiểm tra:

1. Python version >= 3.9
2. Tất cả dependencies đã cài đặt
3. Không có lỗi import trong code
4. PyInstaller version mới nhất

Để debug chi tiết:

```bash
pyinstaller --debug all pixci_gui.py
```

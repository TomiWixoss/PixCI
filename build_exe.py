"""
Build script để tạo file .exe cho PixCI GUI
Sử dụng PyInstaller để đóng gói ứng dụng
"""
import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_gui_exe():
    """Build PixCI GUI thành file .exe"""
    
    # Đường dẫn đến các file cần thiết
    script_path = "pixci_gui.py"
    icon_path = None  # Có thể thêm icon nếu có
    
    # Các tham số cho PyInstaller
    args = [
        script_path,
        '--name=PixCI',
        '--onefile',  # Tạo một file .exe duy nhất
        '--windowed',  # Không hiện console window (GUI app)
        '--clean',
        '--noconfirm',
        
        # Thêm các module cần thiết
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        
        # Thêm pixci module
        '--hidden-import=pixci',
        '--hidden-import=pixci.core',
        '--hidden-import=pixci.core.canvas',
        '--hidden-import=pixci.core.animation',
        '--hidden-import=pixci.core.grid_engine',
        '--hidden-import=pixci.core.code_engine',
        '--hidden-import=pixci.core.pxvg_engine',
        '--hidden-import=pixci.core.prompts',
        '--hidden-import=pixci.core.mixins',
        '--hidden-import=pixci.core.mixins.color',
        '--hidden-import=pixci.styles',
        '--hidden-import=pixci.styles.minecraft',
        
        # Thêm các dependencies
        '--collect-all=pixci',
        
        # Thêm data files nếu cần (palettes, textures, etc.)
        '--add-data=.palette_cache;.palette_cache',
    ]
    
    # Thêm icon nếu có
    if icon_path and os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
    
    print("🚀 Bắt đầu build PixCI.exe...")
    print(f"📦 Script: {script_path}")
    print(f"🎯 Output: dist/PixCI.exe")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print()
        print("✅ Build thành công!")
        print("📁 File .exe được tạo tại: dist/PixCI.exe")
        print()
        print("💡 Bạn có thể copy file PixCI.exe đến bất kỳ đâu và chạy trực tiếp!")
        
    except Exception as e:
        print(f"❌ Lỗi khi build: {e}")
        sys.exit(1)

def build_cli_exe():
    """Build PixCI CLI thành file .exe"""
    
    # Tạo entry point cho CLI
    cli_entry = Path("pixci_cli_entry.py")
    cli_entry.write_text("""
import sys
import os

# Add pixci-web/backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'pixci-web', 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)

from pixci.cli import app

if __name__ == "__main__":
    app()
""")
    
    # Đường dẫn đến pixci module
    pixci_path = Path("pixci-web/backend")
    
    args = [
        str(cli_entry),
        '--name=pixci-cli',
        '--onefile',
        '--console',  # Hiện console cho CLI app
        '--clean',
        '--noconfirm',
        
        # Add paths
        f'--paths={pixci_path}',
        
        # Hidden imports
        '--hidden-import=typer',
        '--hidden-import=rich',
        '--hidden-import=rich.console',
        '--hidden-import=pixci',
        '--hidden-import=pixci.cli',
        '--hidden-import=pixci.core',
        '--hidden-import=pixci.core.canvas',
        '--hidden-import=pixci.core.animation',
        '--hidden-import=pixci.core.grid_engine',
        '--hidden-import=pixci.core.code_engine',
        '--hidden-import=pixci.core.pxvg_engine',
        '--hidden-import=pixci.core.prompts',
        '--hidden-import=pixci.core.mixins',
        '--hidden-import=pixci.core.mixins.color',
        '--hidden-import=pixci.styles',
        '--hidden-import=pixci.styles.minecraft',
        
        # Collect all
        '--collect-all=typer',
        '--collect-all=rich',
        
        # Data files
        '--add-data=.palette_cache;.palette_cache',
        f'--add-data={pixci_path / "pixci"};pixci',
    ]
    
    print("🚀 Bắt đầu build pixci-cli.exe...")
    print(f"📦 Script: {cli_entry}")
    print(f"🎯 Output: dist/pixci-cli.exe")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        cli_entry.unlink()  # Xóa file tạm
        print()
        print("✅ Build CLI thành công!")
        print("📁 File .exe được tạo tại: dist/pixci-cli.exe")
        
    except Exception as e:
        print(f"❌ Lỗi khi build CLI: {e}")
        if cli_entry.exists():
            cli_entry.unlink()
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build PixCI thành file .exe")
    parser.add_argument(
        "--mode",
        choices=["gui", "cli", "both"],
        default="gui",
        help="Chọn loại build: gui (GUI app), cli (CLI tool), hoặc both (cả hai)"
    )
    
    args = parser.parse_args()
    
    if args.mode in ["gui", "both"]:
        build_gui_exe()
        print()
    
    if args.mode in ["cli", "both"]:
        build_cli_exe()
        print()
    
    if args.mode == "both":
        print("🎉 Đã build xong cả GUI và CLI!")
        print("📁 Kiểm tra thư mục dist/ để lấy các file .exe")

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional
from .core.grid_engine import encode_image, encode_code, decode_text, init_canvas, init_code_canvas

app = typer.Typer(
    help="PixCI: Công cụ CLI chuyển đổi Ảnh Pixel sang Text cho LLMs.",
    add_completion=False
)
console = Console()

@app.command()
def encode(
    image_path: Path = typer.Argument(..., help="Đường dẫn file ảnh đầu vào"),
    output: Path = typer.Option(..., "-o", "--output", help="Đường dẫn file text đầu ra"),
    form: str = typer.Option("grid", "-f", "--format", help="Định dạng đầu ra: 'grid' hoặc 'code' (mặc định: grid)"),
    auto: bool = typer.Option(False, "--auto", help="Tự động phát hiện kích thước block"),
    block_size: int = typer.Option(1, "--block-size", help="Chỉ định kích thước block thủ công"),
    style: str = typer.Option("generic", "--style", help="Chế độ encode ('generic' hoặc 'minecraft')")
):
    """Chuyển đổi file ảnh thành dạng file text của PixCI."""
    try:
        if form.lower() == "code":
            if style.lower() == "minecraft":
                from .styles.minecraft import MinecraftStyle
                grid_w, grid_h, num_colors, final_block_size = MinecraftStyle.encode(image_path, output, block_size, auto)
            else:
                grid_w, grid_h, num_colors, final_block_size = encode_code(image_path, output, block_size, auto)
        else:
            grid_w, grid_h, num_colors, final_block_size = encode_image(image_path, output, block_size, auto)
        
        if auto:
            console.print(f"[green]Kích thước block tự động phát hiện: {final_block_size}[/green]")
            
        if grid_w > 64 or grid_h > 64:
            console.print("[yellow]Cảnh báo: Lưới kết quả lớn hơn 64x64. Có thể vượt quá giới hạn token của LLM.[/yellow]")
            
        console.print(f"[green]Đã encode thành công {image_path} sang {output}[/green]")
        console.print(f"Kích thước lưới: {grid_w}x{grid_h}, Số màu duy nhất: {num_colors}")
        
    except Exception as e:
        console.print(f"[red]Lỗi trong quá trình encode: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def decode(
    text_path: Path = typer.Argument(..., help="Đường dẫn file text do AI tạo"),
    output: Path = typer.Option(..., "-o", "--output", help="Đường dẫn file ảnh đầu ra (.png)"),
    scale: int = typer.Option(1, "--scale", help="Phóng to ảnh đầu ra (Thuật toán Nearest Neighbor)")
):
    """Chuyển đổi file text của PixCI ngược lại thành file ảnh."""
    try:
        width, height = decode_text(text_path, output, scale)
        console.print(f"[green]Đã decode thành công sang file {output}[/green]")
        console.print(f"Kích thước lưới gốc: {width}x{height}, Kích thước ảnh xuất ra: {width*scale}x{height*scale}")
        
    except Exception as e:
        console.print(f"[red]Lỗi trong quá trình decode: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def init(
    size: str = typer.Option("16x16", "--size", help="Kích thước lưới (rộng x cao, VD: 16x16)"),
    form: str = typer.Option("grid", "-f", "--format", help="Định dạng đầu ra: 'grid' hoặc 'code' (mặc định: grid)"),
    output: Path = typer.Option(..., "-o", "--output", help="Đường dẫn file text đầu ra")
):
    """Khởi tạo một khung vẽ lưới rỗng để AI bắt đầu vẽ."""
    try:
        w, h = map(int, size.lower().split("x"))
        if form.lower() == "code":
            init_code_canvas(output, w, h)
        else:
            init_canvas(output, w, h)
        console.print(f"[green]Đã khởi tạo thành công khung vẽ rỗng {w}x{h} tại {output}[/green]")
    except Exception as e:
        console.print(f"[red]Lỗi trong quá trình khởi tạo: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def run(
    script_path: Path = typer.Argument(..., help="Đường dẫn file python do AI tạo"),
    scale: int = typer.Option(1, "--scale", help="Phóng to ảnh đầu ra")
):
    """Thực thi trực tiếp file .py do AI viết"""
    try:
        import sys
        import subprocess
        import os
        
        env = os.environ.copy()
        # Ensure we add the project root to PYTHONPATH so `import pixci` works natively
        current_dir = os.getcwd()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{current_dir}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = current_dir

        if scale > 1:
            env["PIXCI_SCALE"] = str(scale)
            
        console.print(f"[cyan]Đang chạy file {script_path}...[/cyan]")
        result = subprocess.run([sys.executable, str(script_path)], env=env, capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[red]Lỗi khi chạy code của AI:[/red]")
            console.print(result.stderr)
            raise typer.Exit(code=1)
            
        console.print("[green]Đã chạy thành công file AI![/green]")
        if result.stdout:
            console.print(result.stdout)
    except Exception as e:
        console.print(f"[red]Lỗi thực thi: {str(e)}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

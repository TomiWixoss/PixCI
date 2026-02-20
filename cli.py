import typer
from rich.console import Console
from pathlib import Path
from typing import Optional
from core import encode_image, decode_text, init_canvas

app = typer.Typer(
    help="PixCI: Công cụ CLI chuyển đổi Ảnh Pixel sang Text cho LLMs.",
    add_completion=False
)
console = Console()

@app.command()
def encode(
    image_path: Path = typer.Argument(..., help="Đường dẫn file ảnh đầu vào"),
    output: Path = typer.Option(..., "-o", "--output", help="Đường dẫn file text đầu ra"),
    auto: bool = typer.Option(False, "--auto", help="Tự động phát hiện kích thước block"),
    block_size: int = typer.Option(1, "--block-size", help="Chỉ định kích thước block thủ công")
):
    """Chuyển đổi file ảnh thành dạng file text của PixCI."""
    try:
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
    output: Path = typer.Option(..., "-o", "--output", help="Đường dẫn file text đầu ra")
):
    """Khởi tạo một khung vẽ lưới rỗng để AI bắt đầu vẽ."""
    try:
        w, h = map(int, size.lower().split("x"))
        init_canvas(output, w, h)
        console.print(f"[green]Đã khởi tạo thành công khung vẽ rỗng {w}x{h} tại {output}[/green]")
    except Exception as e:
        console.print(f"[red]Lỗi trong quá trình khởi tạo: {str(e)}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

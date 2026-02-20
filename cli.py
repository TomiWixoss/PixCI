import typer
from rich.console import Console
from pathlib import Path
from typing import Optional
from core import encode_image, decode_text, init_canvas

app = typer.Typer(help="PixCI: CLI tool for converting Pixel Art to Text for LLMs.")
console = Console()

@app.command()
def encode(
    image_path: Path = typer.Argument(..., help="Path to input image"),
    output: Path = typer.Option(..., "-o", "--output", help="Path to output text file"),
    auto: bool = typer.Option(False, "--auto", help="Auto-detect block size"),
    block_size: int = typer.Option(1, "--block-size", help="Specify manual block size")
):
    """Convert an image to a PixCI text file."""
    try:
        grid_w, grid_h, num_colors, final_block_size = encode_image(image_path, output, block_size, auto)
        
        if auto:
            console.print(f"[green]Auto-detected block size: {final_block_size}[/green]")
            
        if grid_w > 64 or grid_h > 64:
            console.print("[yellow]Warning: Target grid is over 64x64. This may exceed LLM token limits.[/yellow]")
            
        console.print(f"[green]Successfully encoded {image_path} to {output}[/green]")
        console.print(f"Grid size: {grid_w}x{grid_h}, Unique colors: {num_colors}")
        
    except Exception as e:
        console.print(f"[red]Error during encoding: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def decode(
    text_path: Path = typer.Argument(..., help="Path to AI generated text file"),
    output: Path = typer.Option(..., "-o", "--output", help="Path to output png file"),
    scale: int = typer.Option(1, "--scale", help="Scale up the output image (Nearest Neighbor)")
):
    """Convert a PixCI text file back to an image."""
    try:
        width, height = decode_text(text_path, output, scale)
        console.print(f"[green]Successfully decoded to {output}[/green]")
        console.print(f"Original Grid size: {width}x{height}, Output size: {width*scale}x{height*scale}")
        
    except Exception as e:
        console.print(f"[red]Error during decoding: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def init(
    size: str = typer.Option("16x16", "--size", help="Grid size (width x height)"),
    output: Path = typer.Option(..., "-o", "--output", help="Output text file path")
):
    """Initialize an empty grid for the AI to start drawing."""
    try:
        w, h = map(int, size.lower().split("x"))
        init_canvas(output, w, h)
        console.print(f"[green]Successfully initialized empty {w}x{h} canvas to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Error during initialization: {str(e)}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

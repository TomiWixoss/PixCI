from typing import List, Optional
from PIL import Image

from .canvas import Canvas
from .canvas_base import hex2rgba

class Animation:
    """
    Hệ thống Animation cho PixCI (Python branch).
    Cho phép tạo các frame độc lập (dạng Canvas) và render thành Spritesheet & GIF.
    """
    def __init__(self, width: int, height: int, columns: Optional[int] = None, fps: float = 10.0):
        self.width = width
        self.height = height
        self.columns = columns
        self.fps = fps
        self.frames: List[Canvas] = []
        self.master_palette = {}
        
    def add_palette(self, palette_dict: dict):
        for k, v in palette_dict.items():
            rgba = hex2rgba(v) if isinstance(v, str) and str(v).startswith("#") else v
            self.master_palette[k] = rgba
        for frame in self.frames:
            frame.palette.update(self.master_palette)
            
    def load_palette(self, name: str, prefix: str = ""):
        # Tạo canvas tạm để gọi logic load_palette đã có
        temp = Canvas(1, 1)
        temp.load_palette(name, prefix)
        self.add_palette(temp.palette)
        
    def auto_shade(self, hex_color: str, levels: int = 2) -> dict:
        temp = Canvas(1, 1)
        return temp.auto_shade(hex_color, levels)
        
    def add_frame(self) -> Canvas:
        """Tạo và trả về một Canvas đại diện cho frame mới."""
        frame = Canvas(self.width, self.height)
        frame.palette = self.master_palette.copy()
        self.frames.append(frame)
        return frame

    def save(self, output_path: str, scale: int = 1):
        """Xuất Animation ra file Spritesheet (.png) và ảnh động (.gif)."""
        num_frames = len(self.frames)
        if num_frames == 0:
            raise ValueError("Không có frame nào để render.")
            
        columns = self.columns if self.columns else num_frames
        rows = (num_frames + columns - 1) // columns
        
        # Hình ảnh Spritesheet tổng
        spritesheet = Image.new("RGBA", (self.width * columns, self.height * rows), (0, 0, 0, 0))
        frames_list = []
        
        for idx, frame in enumerate(self.frames):
            frame.merge_all()
            frame_img = Image.new("RGBA", (self.width, self.height))
            pixels = frame_img.load()
            flat = frame.flatten()
            for x in range(self.width):
                for y in range(self.height):
                    pixels[x, y] = flat[x][y]
                    
            # Dán vào Spritesheet
            grid_x = idx % columns
            grid_y = idx // columns
            spritesheet.paste(frame_img, (grid_x * self.width, grid_y * self.height))
            
            if scale > 1:
                frame_img = frame_img.resize((self.width * scale, self.height * scale), Image.NEAREST)
            frames_list.append(frame_img)
            
        if not output_path.endswith(".png"):
            output_path += ".png"
            
        if scale > 1:
            spritesheet = spritesheet.resize(
                (self.width * columns * scale, self.height * rows * scale), 
                Image.NEAREST
            )
        spritesheet.save(output_path)
        
        if frames_list:
            duration = int(1000 / self.fps)
            gif_path = output_path.replace('.png', '.gif')
            
            frames_list[0].save(
                gif_path,
                format='GIF',
                save_all=True,
                append_images=frames_list[1:],
                duration=duration,
                loop=0,
                disposal=2
            )

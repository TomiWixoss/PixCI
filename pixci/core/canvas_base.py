import os
from PIL import Image
from typing import Tuple, Union

def hex2rgba(hex_str: str) -> Tuple[int, int, int, int]:
    if hex_str.startswith("#"):
        hex_str = hex_str[1:]
    if len(hex_str) == 6:
        hex_str += "FF"
    if len(hex_str) == 8:
        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), int(hex_str[6:8], 16))
    return (0, 0, 0, 0)

class BaseCanvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[(0, 0, 0, 0)] * height for _ in range(width)]
        self.palette = {}

    def _get_color(self, char_or_color: Union[str, Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        if isinstance(char_or_color, str) and char_or_color in self.palette:
            return self.palette[char_or_color]
        if isinstance(char_or_color, tuple) and len(char_or_color) == 4:
            return char_or_color
        if isinstance(char_or_color, str) and char_or_color.startswith("#"):
            return hex2rgba(char_or_color)
        return (0, 0, 0, 0)

    def set_pixel(self, pos: Tuple[int, int], color: Union[str, Tuple[int, int, int, int]]):
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x][y] = self._get_color(color)

    def _get_light_vector(self, light_dir: str) -> Tuple[float, float, float]:
        if light_dir == "top_left": return (-1, -1, 1)
        if light_dir == "top_right": return (1, -1, 1)
        if light_dir == "bottom_left": return (-1, 1, 1)
        if light_dir == "bottom_right": return (1, 1, 1)
        if light_dir == "top": return (0, -1, 1)
        return (0, 0, 1)

    def save(self, output_path: str, scale: int = 1):
        scale_env = os.environ.get("PIXCI_SCALE")
        if scale_env and scale == 1:
            try:
                scale = int(scale_env)
            except ValueError:
                pass
                
        if not output_path.endswith(".png"):
            output_path += ".png"
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        pixels = img.load()
        for x in range(self.width):
            for y in range(self.height):
                pixels[x, y] = self.grid[x][y]
        
        if scale > 1:
            img = img.resize((self.width * scale, self.height * scale), Image.NEAREST)
        img.save(output_path)

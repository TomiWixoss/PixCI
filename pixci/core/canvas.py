from PIL import Image
from typing import Tuple, Dict, Union

def hex2rgba(hex_str: str) -> Tuple[int, int, int, int]:
    if hex_str.startswith("#"):
        hex_str = hex_str[1:]
    if len(hex_str) == 6:
        hex_str += "FF"
    if len(hex_str) == 8:
        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), int(hex_str[6:8], 16))
    return (0, 0, 0, 0)

class Canvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[(0, 0, 0, 0)] * height for _ in range(width)]
        self.palette = {}

    def add_color(self, char: str, color_code: str):
        self.palette[char] = hex2rgba(color_code)

    def add_palette(self, palette_dict: Dict[str, str]):
        for char, color_code in palette_dict.items():
            self.add_color(char, color_code)

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

    def draw_line(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], color: str):
        x0, y0 = start_pos
        x1, y1 = end_pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.set_pixel((x0, y0), color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_rect(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], color: str):
        x0, y0 = top_left
        x1, y1 = bottom_right
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set_pixel((x, y), color)

    def draw_circle(self, center_pos: Tuple[int, int], radius: int, color: str):
        x0, y0 = center_pos
        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x = 0
        y = radius

        self.set_pixel((x0, y0 + radius), color)
        self.set_pixel((x0, y0 - radius), color)
        self.set_pixel((x0 + radius, y0), color)
        self.set_pixel((x0 - radius, y0), color)

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x
            self.set_pixel((x0 + x, y0 + y), color)
            self.set_pixel((x0 - x, y0 + y), color)
            self.set_pixel((x0 + x, y0 - y), color)
            self.set_pixel((x0 - x, y0 - y), color)
            self.set_pixel((x0 + y, y0 + x), color)
            self.set_pixel((x0 - y, y0 + x), color)
            self.set_pixel((x0 + y, y0 - x), color)
            self.set_pixel((x0 - y, y0 - x), color)

    def translate(self, offset_x: int, offset_y: int):
        new_grid = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                nx = x + offset_x
                ny = y + offset_y
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    new_grid[nx][ny] = self.grid[x][y]
        self.grid = new_grid

    def flip_x(self):
        new_grid = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                new_grid[self.width - 1 - x][y] = self.grid[x][y]
        self.grid = new_grid

    def flip_y(self):
        new_grid = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                new_grid[x][self.height - 1 - y] = self.grid[x][y]
        self.grid = new_grid

    def fill_bucket(self, start_pos: Tuple[int, int], color: str):
        x, y = start_pos
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        target_color = self.grid[x][y]
        replacement_color = self._get_color(color)
        if target_color == replacement_color:
            return

        queue = [(x, y)]
        while queue:
            cx, cy = queue.pop(0)
            if self.grid[cx][cy] == target_color:
                self.grid[cx][cy] = replacement_color
                if cx > 0: queue.append((cx - 1, cy))
                if cx < self.width - 1: queue.append((cx + 1, cy))
                if cy > 0: queue.append((cx, cy - 1))
                if cy < self.height - 1: queue.append((cx, cy + 1))

    def save(self, output_path: str, scale: int = 1):
        import os
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

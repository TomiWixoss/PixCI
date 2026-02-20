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
        self.layers = {"default": [[(0, 0, 0, 0)] * height for _ in range(width)]}
        self.layer_order = ["default"]
        self.active_layer = "default"
        self.alpha_lock = False
        self.palette = {}

    @property
    def grid(self):
        return self.layers[self.active_layer]

    @grid.setter
    def grid(self, value):
        self.layers[self.active_layer] = value

    def add_layer(self, name: str):
        if name not in self.layers:
            self.layers[name] = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
            self.layer_order.append(name)
        self.active_layer = name

    def set_layer(self, name: str):
        if name in self.layers:
            self.active_layer = name

    def merge_layers(self, base_layer: str, top_layer: str, mode: str = "normal"):
        if base_layer in self.layers and top_layer in self.layers:
            bg = self.layers[base_layer]
            fg = self.layers[top_layer]
            for x in range(self.width):
                for y in range(self.height):
                    fr, fg_c, fb, fa = fg[x][y]
                    br, bg_c, bb, ba = bg[x][y]
                    
                    if fa == 0:
                        continue
                        
                    if mode == "multiply":
                        mr = int((fr * br) / 255)
                        mg = int((fg_c * bg_c) / 255)
                        mb = int((fb * bb) / 255)
                        fr, fg_c, fb = mr, mg, mb
                    elif mode == "add":
                        ar = min(255, fr + br)
                        ag = min(255, fg_c + bg_c)
                        ab = min(255, fb + bb)
                        fr, fg_c, fb = ar, ag, ab
                        
                    if fa == 255:
                        bg[x][y] = (fr, fg_c, fb, fa)
                    elif fa > 0:
                        alpha = fa / 255.0
                        inv_alpha = 1.0 - alpha
                        out_a = fa + ba * inv_alpha
                        if out_a > 0:
                            out_r = (fr * fa + br * ba * inv_alpha) / out_a
                            out_g = (fg_c * fa + bg_c * ba * inv_alpha) / out_a
                            out_b = (fb * fa + bb * ba * inv_alpha) / out_a
                            bg[x][y] = (int(out_r), int(out_g), int(out_b), int(out_a))

    def flatten(self):
        if not self.layer_order: return [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        flat = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for layer_name in self.layer_order:
            fg = self.layers[layer_name]
            for x in range(self.width):
                for y in range(self.height):
                    fr, fg_c, fb, fa = fg[x][y]
                    if fa == 255:
                        flat[x][y] = fg[x][y]
                    elif fa > 0:
                        br, bg_c, bb, ba = flat[x][y]
                        alpha = fa / 255.0
                        inv_alpha = 1.0 - alpha
                        out_a = fa + ba * inv_alpha
                        if out_a > 0:
                            out_r = (fr * fa + br * ba * inv_alpha) / out_a
                            out_g = (fg_c * fa + bg_c * ba * inv_alpha) / out_a
                            out_b = (fb * fa + bb * ba * inv_alpha) / out_a
                            flat[x][y] = (int(out_r), int(out_g), int(out_b), min(255, int(out_a)))
        return flat

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
            if self.alpha_lock and self.grid[x][y][3] == 0:
                return
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
        flat_grid = self.flatten()
        for x in range(self.width):
            for y in range(self.height):
                pixels[x, y] = flat_grid[x][y]
        
        if scale > 1:
            img = img.resize((self.width * scale, self.height * scale), Image.NEAREST)
        img.save(output_path)

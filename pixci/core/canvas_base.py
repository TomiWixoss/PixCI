import os
from PIL import Image
from typing import Tuple, Union, List, Optional

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
        self._outline_pixels = set()  # Tracked by postprocess

    @property
    def grid(self):
        return self.layers[self.active_layer]

    @grid.setter
    def grid(self, value):
        self.layers[self.active_layer] = value

    def add_layer(self, name: str):
        """Add a new drawing layer and set it as active.
        Layers are drawn bottom-to-top when flattened/saved.
        
        Example:
            canvas.add_layer("background")
            canvas.add_layer("character")
            canvas.add_layer("foreground")
        """
        if name not in self.layers:
            self.layers[name] = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
            self.layer_order.append(name)
        self.active_layer = name

    def set_layer(self, name: str):
        """Switch the active drawing layer without creating a new one."""
        if name in self.layers:
            self.active_layer = name

    def delete_layer(self, name: str):
        """Delete a layer. Cannot delete the last remaining layer."""
        if name in self.layers and len(self.layer_order) > 1:
            del self.layers[name]
            self.layer_order.remove(name)
            if self.active_layer == name:
                self.active_layer = self.layer_order[-1]

    def reorder_layers(self, order: List[str]):
        """Reorder layers. First in list = bottom (drawn first), last = top.
        
        Example:
            canvas.reorder_layers(["background", "shadows", "character", "effects"])
        """
        for name in order:
            if name not in self.layers:
                raise ValueError(f"Layer '{name}' does not exist")
        self.layer_order = order

    def merge_layers(self, base_layer: str, top_layer: str, mode: str = "normal"):
        """Merge top_layer down into base_layer.
        
        Modes: 'normal', 'multiply', 'add'
        """
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
                            
            if top_layer in self.layer_order:
                self.layer_order.remove(top_layer)
            if top_layer in self.layers:
                del self.layers[top_layer]

    def merge_all(self):
        """Merge all layers into a single 'default' layer."""
        flat = self.flatten()
        self.layers = {"default": flat}
        self.layer_order = ["default"]
        self.active_layer = "default"

    def flatten(self):
        if not self.layer_order: return [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        flat = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for layer_name in self.layer_order:
            if layer_name not in self.layers:
                continue
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
        """Set a single pixel at (x, y). Respects alpha_lock."""
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.alpha_lock and self.grid[x][y][3] == 0:
                return
            self.grid[x][y] = self._get_color(color)

    def get_pixel(self, pos: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Get the RGBA color of a pixel at (x, y)."""
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return (0, 0, 0, 0)

    def clear(self, color: Optional[str] = None):
        """Clear the active layer. If color is given, fill with that color."""
        fill = self._get_color(color) if color else (0, 0, 0, 0)
        self.grid = [[fill] * self.height for _ in range(self.width)]

    def _get_light_vector(self, light_dir: str) -> Tuple[float, float, float]:
        if light_dir == "top_left": return (-1, -1, 1)
        if light_dir == "top_right": return (1, -1, 1)
        if light_dir == "bottom_left": return (-1, 1, 1)
        if light_dir == "bottom_right": return (1, 1, 1)
        if light_dir == "top": return (0, -1, 1)
        if light_dir == "left": return (-1, 0, 1)
        if light_dir == "right": return (1, 0, 1)
        if light_dir == "bottom": return (0, 1, 1)
        return (0, 0, 1)

    def save(self, output_path: str, scale: int = 1):
        """Save the canvas to a PNG file.
        
        Args:
            output_path: File path for the output image
            scale: Upscale factor (uses nearest-neighbor for crisp pixels)
        """
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
        
    def load_image(self, image_path: str, position: Tuple[int, int] = (0, 0)):
        """Load an external PNG image onto the current layer."""
        img = Image.open(image_path).convert("RGBA")
        pixels = img.load()
        px, py = position
        for x in range(min(img.width, self.width - px)):
            for y in range(min(img.height, self.height - py)):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    self.set_pixel((px + x, py + y), (r, g, b, a))

    # =================================================================
    # SPATIAL HELPERS - Giúp AI định vị bằng ngữ nghĩa thay vì số
    # =================================================================

    def get_center(self) -> Tuple[int, int]:
        """Trả về tâm của Canvas. AI dùng làm điểm neo chính.
        
        Example:
            cx, cy = canvas.get_center()  # (16, 16) trên canvas 32x32
        """
        return (self.width // 2, self.height // 2)

    def get_ground(self, margin: int = 2) -> int:
        """Trả về y 'mặt đất' (gần đáy canvas). AI dùng để đặt chân nhân vật.
        
        Example:
            ground_y = canvas.get_ground()  # 29 trên canvas 32x32
        """
        return self.height - 1 - margin

    def anchor_above(self, base_y: int, offset: int) -> int:
        """Tính y nằm TRÊN base_y một khoảng offset. Y giảm = lên trên.
        
        Example:
            stem_top = 24
            cap_bottom = canvas.anchor_above(stem_top, 1)  # 23
        """
        return base_y - offset

    def anchor_below(self, base_y: int, offset: int) -> int:
        """Tính y nằm DƯỚI base_y một khoảng offset. Y tăng = xuống dưới."""
        return base_y + offset

    def anchor_left_of(self, base_x: int, offset: int) -> int:
        """Tính x nằm BÊN TRÁI base_x."""
        return base_x - offset

    def anchor_right_of(self, base_x: int, offset: int) -> int:
        """Tính x nằm BÊN PHẢI base_x."""
        return base_x + offset

    def span(self, center: int, size: int) -> Tuple[int, int]:
        """Tính (start, end) từ center và size. AI dùng để tạo bounding box cân xứng.
        
        Example:
            cx = 16
            x_start, x_end = canvas.span(cx, 10)  # (11, 20)
            canvas.fill_rect((x_start, y0), (x_end, y1), "R1")
        """
        half = size // 2
        return (center - half, center + half - (1 if size % 2 == 0 else 0))

    def bbox(self, center_x: int, center_y: int, width: int, height: int) -> Tuple[int, int, int, int]:
        """Tạo bounding box (x0, y0, x1, y1) từ tâm và kích thước.
        AI dùng để quy hoạch vùng vẽ cho từng bộ phận.
        
        Example:
            cap_box = canvas.bbox(cx, 12, 22, 12)  # (5, 6, 26, 17)
            stem_box = canvas.bbox(cx, 24, 6, 8)   # (13, 20, 18, 27)
        """
        x0, x1 = self.span(center_x, width)
        y0, y1 = self.span(center_y, height)
        return (x0, y0, x1, y1)

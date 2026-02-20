import math
import colorsys
import os
from PIL import Image
from typing import Tuple, Dict, Union, List

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

    def generate_ramp(self, base_color: str, steps: int, mode: str = "hue_shift") -> List[str]:
        base_rgba = self._get_color(base_color)
        r, g, b = [x / 255.0 for x in base_rgba[:3]]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        ramp = []
        for i in range(steps):
            t = i / max(1, (steps - 1))
            
            if mode == "hue_shift":
                hue_shift = (t - 0.5) * 0.15
                new_h = (h + hue_shift) % 1.0
                new_s = min(1.0, max(0.0, s * (1.0 if t > 0.5 else 0.8)))
                new_l = min(1.0, max(0.0, l * (0.4 + 1.0 * t)))
            else:
                new_h = h
                new_s = s
                new_l = min(1.0, max(0.0, l * (0.4 + 1.0 * t)))
                
            nr, ng, nb = colorsys.hls_to_rgb(new_h, new_l, new_s)
            hex_val = f"#{int(nr*255):02X}{int(ng*255):02X}{int(nb*255):02X}FF"
            ramp.append(hex_val)
            
        return ramp

    def load_palette(self, name: str):
        pass # Placeholder for external palettes

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

    def draw_curve(self, start_pos: Tuple[int, int], control_pos: Tuple[int, int], end_pos: Tuple[int, int], color: str, pixel_perfect: bool = True):
        pts = []
        x0, y0 = start_pos
        cx, cy = control_pos
        x1, y1 = end_pos
        dist = max(abs(x1-x0), abs(y1-y0)) * 2 + 10
        
        for i in range(dist + 1):
            t = i / dist
            x = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
            y = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
            pts.append((int(round(x)), int(round(y))))
            
        unique_pts = []
        for p in pts:
            if not unique_pts or unique_pts[-1] != p:
                unique_pts.append(p)
                
        if pixel_perfect and len(unique_pts) >= 3:
            clean = [unique_pts[0]]
            for i in range(1, len(unique_pts)-1):
                prev = clean[-1]
                curr = unique_pts[i]
                nxt = unique_pts[i+1]
                dx1, dy1 = curr[0]-prev[0], curr[1]-prev[1]
                dx2, dy2 = nxt[0]-curr[0], nxt[1]-curr[1]
                if (abs(dx1) == 1 and dy1 == 0 and dx2 == 0 and abs(dy2) == 1) or \
                   (dx1 == 0 and abs(dy1) == 1 and abs(dx2) == 1 and dy2 == 0):
                    pass # skip to remove L-shape jaggies
                else:
                    clean.append(curr)
            clean.append(unique_pts[-1])
            unique_pts = clean
            
        for p in unique_pts:
            self.set_pixel(p, color)

    def apply_aa(self, color_1: str, color_2: str):
        pass # Placeholder for AA pass
        
    def fill_rect(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], color: str):
        x0, y0 = top_left
        x1, y1 = bottom_right
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set_pixel((x, y), color)

    def draw_circle(self, center_pos: Tuple[int, int], radius: int, color: str, pixel_perfect: bool = False):
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
            if not pixel_perfect or (f < 0): 
                self.set_pixel((x0 + x, y0 + y), color)
                self.set_pixel((x0 - x, y0 + y), color)
                self.set_pixel((x0 + x, y0 - y), color)
                self.set_pixel((x0 - x, y0 - y), color)
                self.set_pixel((x0 + y, y0 + x), color)
                self.set_pixel((x0 - y, y0 + x), color)
                self.set_pixel((x0 + y, y0 - x), color)
                self.set_pixel((x0 - y, y0 - x), color)

    def fill_dither(self, rect: Tuple[int, int, int, int], color1: str, color2: str, pattern: str = "checkered"):
        x0, y0, x1, y1 = rect
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                if pattern in ["checkered", "50_percent", "50"]:
                    if (x + y) % 2 == 0:
                        self.set_pixel((x, y), color1)
                    else:
                        self.set_pixel((x, y), color2)
                elif pattern == "25_percent":
                    if x % 2 == 0 and y % 2 == 0:
                        self.set_pixel((x, y), color1)
                    else:
                        self.set_pixel((x, y), color2)
                else:
                    self.set_pixel((x, y), color1)

    def _get_light_vector(self, light_dir: str):
        if light_dir == "top_left": return (-1, -1, 1)
        if light_dir == "top_right": return (1, -1, 1)
        if light_dir == "bottom_left": return (-1, 1, 1)
        if light_dir == "bottom_right": return (1, 1, 1)
        if light_dir == "top": return (0, -1, 1)
        return (0, 0, 1)

    def draw_sphere(self, center: Tuple[int, int], radius: int, palette: Union[str, List[str]], light_dir: str = "top_left"):
        xc, yc = center
        lx, ly, lz = self._get_light_vector(light_dir)
        length = math.sqrt(lx*lx + ly*ly + lz*lz)
        lx, ly, lz = lx/length, ly/length, lz/length
        
        is_ramp = isinstance(palette, list)
        for x in range(xc - radius, xc + radius + 1):
            for y in range(yc - radius, yc + radius + 1):
                dx = x - xc
                dy = y - yc
                if dx*dx + dy*dy <= radius*radius:
                    if is_ramp:
                        dz = math.sqrt(max(0, radius*radius - dx*dx - dy*dy))
                        nx, ny, nz = dx/radius, dy/radius, dz/radius
                        dot = nx*lx + ny*ly + nz*lz
                        val = max(0.0, min(1.0, (dot + 1) / 2))
                        idx = int(val * (len(palette) - 1))
                        color = palette[idx]
                    else:
                        color = palette
                    self.set_pixel((x, y), color)

    def draw_half_sphere(self, center: Tuple[int, int], radius: int, palette: Union[str, List[str]], light_dir: str = "top_left"):
        xc, yc = center
        lx, ly, lz = self._get_light_vector(light_dir)
        length = math.sqrt(lx*lx + ly*ly + lz*lz)
        lx, ly, lz = lx/length, ly/length, lz/length
        
        is_ramp = isinstance(palette, list)
        for x in range(xc - radius, xc + radius + 1):
            for y in range(yc - radius, yc + 1):
                dx = x - xc
                dy = y - yc
                if dx*dx + dy*dy <= radius*radius:
                    if is_ramp:
                        dz = math.sqrt(max(0, radius*radius - dx*dx - dy*dy))
                        nx, ny, nz = dx/radius, dy/radius, dz/radius
                        dot = nx*lx + ny*ly + nz*lz
                        val = max(0.0, min(1.0, (dot + 1) / 2))
                        idx = int(val * (len(palette) - 1))
                        color = palette[idx]
                    else:
                        color = palette
                    self.set_pixel((x, y), color)

    def fill_cylinder(self, base: Tuple[int, int], width: int, height: int, palette: Union[str, List[str]], light_dir: str = "top_left"):
        xb, yb = base
        lx, ly, lz = self._get_light_vector(light_dir)
        length = math.sqrt(lx*lx + ly*ly + lz*lz)
        lx, ly, lz = lx/length, ly/length, lz/length
        
        is_ramp = isinstance(palette, list)
        radius = width / 2.0
        
        for y in range(yb - height, yb):
            for x in range(int(xb - radius), int(xb + radius) + 1):
                if is_ramp:
                    nx = (x - xb) / radius
                    nx = max(-1.0, min(1.0, nx))
                    nz = math.sqrt(1 - nx*nx)
                    dot = nx*lx + 0*ly + nz*lz
                    val = max(0.0, min(1.0, (dot + 1) / 2))
                    idx = int(val * (len(palette) - 1))
                    color = palette[idx]
                else:
                    color = palette
                self.set_pixel((x, y), color)

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

    def add_outline(self, color: str = "#000000FF", thickness: int = 1):
        outline_color = self._get_color(color)
        new_grid = [[self.grid[x][y] for y in range(self.height)] for x in range(self.width)]
        
        for t in range(thickness):
            for x in range(self.width):
                for y in range(self.height):
                    if self.grid[x][y][3] == 0: 
                        has_solid_neighbor = False
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.grid[nx][ny][3] != 0:
                                    has_solid_neighbor = True
                                    break
                        if has_solid_neighbor:
                            new_grid[x][y] = outline_color
                            
            self.grid = [[new_grid[x][y] for y in range(self.height)] for x in range(self.width)]

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

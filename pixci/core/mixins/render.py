import math
from typing import Tuple, Union, List
from ..canvas_base import BaseCanvas

class RenderMixin(BaseCanvas):
    def fill_dither(self, rect: Tuple[int, int, int, int], color1: str, color2: str, pattern: str = "checkered", ratio: float = 0.5):
        x0, y0, x1, y1 = rect
        bayer_matrix_4x4 = [
            [ 0,  8,  2, 10],
            [12,  4, 14,  6],
            [ 3, 11,  1,  9],
            [15,  7, 13,  5]
        ]
        
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
                elif pattern == "bayer":
                    threshold = bayer_matrix_4x4[y % 4][x % 4] / 16.0
                    if ratio > threshold:
                        self.set_pixel((x, y), color1)
                    else:
                        self.set_pixel((x, y), color2)
                else:
                    self.set_pixel((x, y), color1)

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

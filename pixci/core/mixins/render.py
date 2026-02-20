import math
from typing import Tuple, Union, List, Optional
from ..canvas_base import BaseCanvas

class RenderMixin(BaseCanvas):
    def fill_dither(self, rect: Tuple[int, int, int, int], color1: str, color2: str, pattern: str = "checkered", ratio: float = 0.5):
        """Fill a rectangle with a dithering pattern.
        
        Patterns: 'checkered'/'50_percent', '25_percent', 'bayer' (uses ratio)
        """
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

    # =================================================================
    # SEMANTIC SHAPE FUNCTIONS - AI chỉ cần nói "gì" thay vì "làm sao"
    # =================================================================

    def draw_dome(self, center_x: int, base_y: int, width: int, height: int, color: str):
        """Draw a dome/cap shape (mũ nấm, đỉnh đồi, mái nhà cong).
        
        AI chỉ cần nói: "vẽ vòm đỏ rộng 20, cao 10 ở giữa canvas"
        
        Args:
            center_x: Tâm X của vòm
            base_y: Y đáy vòm (dòng dưới cùng)
            width: Chiều rộng tối đa  
            height: Chiều cao vòm
            color: Màu base
            
        Example:
            canvas.draw_dome(center_x=16, base_y=18, width=22, height=12, color="R1")
        """
        half_w = width / 2.0
        for row_offset in range(height):
            y = base_y - row_offset
            # Elliptical profile: wider at base, narrower at top
            t = row_offset / max(1, height - 1)  # 0=base, 1=top
            row_half = half_w * math.sqrt(max(0, 1 - t * t))
            x_start = int(round(center_x - row_half))
            x_end = int(round(center_x + row_half))
            if x_end >= x_start:
                for x in range(x_start, x_end + 1):
                    self.set_pixel((x, y), color)

    def draw_taper(self, center_x: int, top_y: int, bottom_y: int, 
                   top_width: int, bottom_width: int, color: str):
        """Draw a shape that tapers (narrows) from one end to the other.
        Good for: thân cây, cột đền, đuôi, sừng, chân, cánh tay.
        
        Args:
            center_x: Tâm X
            top_y: Y đỉnh (dòng trên)
            bottom_y: Y đáy (dòng dưới)
            top_width: Chiều rộng ở đỉnh
            bottom_width: Chiều rộng ở đáy
            color: Màu base
            
        Example - thân nấm (rộng dưới, hẹp trên):
            canvas.draw_taper(center_x=16, top_y=20, bottom_y=28, 
                            top_width=6, bottom_width=8, color="S1")
        """
        total_rows = bottom_y - top_y + 1
        for i in range(total_rows):
            y = top_y + i
            t = i / max(1, total_rows - 1)  # 0=top, 1=bottom
            cur_width = top_width + (bottom_width - top_width) * t
            half = cur_width / 2.0
            x_start = int(round(center_x - half))
            x_end = int(round(center_x + half - 1))
            for x in range(x_start, x_end + 1):
                self.set_pixel((x, y), color)

    def draw_blob(self, center: Tuple[int, int], radius_x: int, radius_y: int, 
                  color: str, noise: float = 0.15, seed: int = 42):
        """Draw an organic, irregular blob shape.
        Good for: clouds, bushes, slimes, blobs, puddles.
        
        Args:
            center: (x, y) center
            radius_x, radius_y: Ellipse radii
            color: Fill color
            noise: How irregular the shape is (0=perfect ellipse, 0.3=very blobby)
            seed: Random seed for reproducible shapes
            
        Example:
            canvas.draw_blob((16, 20), 8, 5, "G1", noise=0.2)
        """
        import random
        rng = random.Random(seed)
        
        # Pre-generate noise for angles
        num_angles = 32
        noise_values = [1.0 + rng.uniform(-noise, noise) for _ in range(num_angles)]
        
        xc, yc = center
        for x in range(xc - radius_x - 1, xc + radius_x + 2):
            for y in range(yc - radius_y - 1, yc + radius_y + 2):
                dx = x - xc
                dy = y - yc
                if radius_x == 0 or radius_y == 0:
                    continue
                # Normalized distance
                ndx = dx / radius_x
                ndy = dy / radius_y
                dist = math.sqrt(ndx * ndx + ndy * ndy)
                
                # Get noise factor for this angle
                angle = math.atan2(dy, dx)
                angle_idx = int((angle / (2 * math.pi) + 0.5) * num_angles) % num_angles
                # Interpolate between noise values
                next_idx = (angle_idx + 1) % num_angles
                frac = ((angle / (2 * math.pi) + 0.5) * num_angles) % 1.0
                radius_mult = noise_values[angle_idx] * (1 - frac) + noise_values[next_idx] * frac
                
                if dist <= radius_mult:
                    self.set_pixel((x, y), color)

    def draw_star(self, center: Tuple[int, int], outer_radius: int, inner_radius: int, 
                  points: int, color: str):
        """Draw a filled star shape.
        
        Args:
            center: (x, y) center
            outer_radius: Radius to star points
            inner_radius: Radius to inner concave points
            points: Number of star points (5=classic star)
            color: Fill color
            
        Example:
            canvas.draw_star((16, 16), 8, 3, 5, "Y1")  # Classic 5-pointed star
        """
        xc, yc = center
        # Generate star vertices
        vertices = []
        for i in range(points * 2):
            angle = math.pi * i / points - math.pi / 2
            r = outer_radius if i % 2 == 0 else inner_radius
            vx = xc + r * math.cos(angle)
            vy = yc + r * math.sin(angle)
            vertices.append((int(round(vx)), int(round(vy))))
        
        self.fill_polygon(vertices, color)

    def draw_gem(self, center: Tuple[int, int], width: int, height: int, 
                 colors: List[str]):
        """Draw a faceted gem/crystal shape with automatic shading.
        
        Args:
            center: (x, y) center  
            width: Total width
            height: Total height
            colors: [dark, mid, light, highlight] - 3-4 colors from dark to light
            
        Example:
            canvas.draw_gem((16, 16), 10, 12, ["#2E1A47", "#5B3A8C", "#8B6CC1", "#C4A5FF"])
        """
        xc, yc = center
        hw = width // 2
        hh = height // 2
        mid_y = yc  # Widest point
        
        # Top half (triangle pointing up)
        for dy in range(0, hh + 1):
            y = yc - dy
            t = dy / max(1, hh)
            row_w = int(hw * (1 - t * 0.7))
            for dx in range(-row_w, row_w + 1):
                # Left side = dark, right side = light
                shade_t = (dx + row_w) / max(1, 2 * row_w)
                idx = int(shade_t * (len(colors) - 1))
                idx = min(idx, len(colors) - 1)
                self.set_pixel((xc + dx, y), colors[idx])
        
        # Bottom half (inverted triangle)
        for dy in range(1, hh + 1):
            y = yc + dy
            t = dy / max(1, hh)
            row_w = int(hw * (1 - t))
            for dx in range(-row_w, row_w + 1):
                shade_t = (dx + row_w) / max(1, 2 * row_w)
                # Bottom is darker
                idx = max(0, int(shade_t * (len(colors) - 2)))
                self.set_pixel((xc + dx, y), colors[idx])

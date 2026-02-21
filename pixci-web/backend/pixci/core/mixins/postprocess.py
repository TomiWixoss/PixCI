import math
import colorsys
from typing import Tuple, List, Optional
from ..canvas_base import BaseCanvas

class PostprocessMixin(BaseCanvas):
    def apply_shadow_mask(self, center: Tuple[int, int], radius: int, light_dir: str = "top_left", intensity: float = 0.5, shadow_color: str = "#201020"):
        """Apply a spherical shadow gradient over existing pixels.
        Good for round objects (fruits, heads, spheres).
        Use apply_directional_shadow() for flat/tall objects.
        """
        xc, yc = center
        lx, ly, lz = self._get_light_vector(light_dir)
        length = math.sqrt(lx*lx + ly*ly + lz*lz)
        lx, ly, lz = lx/length, ly/length, lz/length
        
        sr, sg, sb, _ = self._get_color(shadow_color)
        
        for x in range(xc - radius, xc + radius + 1):
            for y in range(yc - radius, yc + radius + 1):
                dx = x - xc
                dy = y - yc
                if dx*dx + dy*dy <= radius*radius:
                    if 0 <= x < self.width and 0 <= y < self.height:
                        current = self.grid[x][y]
                        if current[3] > 0:
                            dz = math.sqrt(max(0, radius*radius - dx*dx - dy*dy))
                            nx, ny, nz = dx/radius, dy/radius, dz/radius
                            dot = nx*lx + ny*ly + nz*lz
                            if dot < 0.2:
                                shadow_weight = min(1.0, (0.2 - dot) * 1.5) * intensity
                                blend_r = int(current[0] * (1 - shadow_weight) + sr * shadow_weight)
                                blend_g = int(current[1] * (1 - shadow_weight) + sg * shadow_weight)
                                blend_b = int(current[2] * (1 - shadow_weight) + sb * shadow_weight)
                                self.grid[x][y] = (blend_r, blend_g, blend_b, current[3])

    def apply_directional_shadow(self, light_dir: str = "top_left", intensity: float = 0.3, shadow_color: str = "#100818"):
        """Apply a directional shadow across ALL non-transparent pixels on the active layer.
        Better for flat/tall objects (swords, trees, buildings).
        The shadow is strongest on the side opposite to the light.
        
        Example:
            canvas.apply_directional_shadow(light_dir="top_left", intensity=0.4)
        """
        lx, ly, _ = self._get_light_vector(light_dir)
        sr, sg, sb, _ = self._get_color(shadow_color)
        
        # Find bounding box of non-transparent pixels
        min_x, max_x, min_y, max_y = self.width, 0, self.height, 0
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y][3] > 0:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        
        if max_x < min_x:
            return
            
        range_x = max(1, max_x - min_x)
        range_y = max(1, max_y - min_y)
        
        for x in range(self.width):
            for y in range(self.height):
                current = self.grid[x][y]
                if current[3] > 0:
                    # Normalized position within bounding box (0..1)
                    nx = (x - min_x) / range_x  # 0=left, 1=right
                    ny = (y - min_y) / range_y  # 0=top, 1=bottom
                    
                    # Shadow factor: higher when pixel is on the shadow side
                    # lx=-1 means light from left → shadow on right (high nx)
                    shadow_x = nx if lx < 0 else (1 - nx) if lx > 0 else 0.5
                    shadow_y = ny if ly < 0 else (1 - ny) if ly > 0 else 0.5
                    shadow_factor = max(shadow_x, shadow_y) * intensity
                    shadow_factor = min(1.0, shadow_factor)
                    
                    if shadow_factor > 0.05:
                        blend_r = int(current[0] * (1 - shadow_factor) + sr * shadow_factor)
                        blend_g = int(current[1] * (1 - shadow_factor) + sg * shadow_factor)
                        blend_b = int(current[2] * (1 - shadow_factor) + sb * shadow_factor)
                        self.grid[x][y] = (blend_r, blend_g, blend_b, current[3])

    def add_outline(self, color: str = "#000000FF", thickness: int = 1, sel_out: bool = False, 
                    hue_shift_amount: float = 0.05, darkness: float = 0.4, saturation_boost: float = 1.2):
        """Add outline around all non-transparent pixels.
        
        Args:
            color: Outline color (used when sel_out=False)
            thickness: Outline thickness in pixels
            sel_out: If True, outline color is derived from the nearest solid pixel
                     (hue-shifted darker version) for a more natural look.
            hue_shift_amount: How much to shift the hue for sel_out (default 0.05)
            darkness: How dark the sel_out outline is (0=black, 1=original, default 0.4)
            saturation_boost: Saturation multiplier for sel_out (default 1.2)
        """
        outline_color = self._get_color(color)
        new_grid = [[self.grid[x][y] for y in range(self.height)] for x in range(self.width)]
        
        # Flood-fill to find exterior (transparent pixels connected to edges)
        exterior = set()
        queue = []
        for x in range(self.width):
            if self.grid[x][0][3] == 0: queue.append((x, 0))
            if self.grid[x][self.height-1][3] == 0: queue.append((x, self.height-1))
        for y in range(self.height):
            if self.grid[0][y][3] == 0: queue.append((0, y))
            if self.grid[self.width-1][y][3] == 0: queue.append((self.width-1, y))
            
        for qx, qy in queue:
            exterior.add((qx, qy))
            
        idx = 0
        while idx < len(queue):
            cx, cy = queue[idx]
            idx += 1
            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nnx, nny = cx + ddx, cy + ddy
                if 0 <= nnx < self.width and 0 <= nny < self.height:
                    if self.grid[nnx][nny][3] == 0 and (nnx, nny) not in exterior:
                        exterior.add((nnx, nny))
                        queue.append((nnx, nny))
        
        # Track all outline pixels for cleanup_jaggies to use
        self._outline_pixels = set()
                        
        for t in range(thickness):
            for x in range(self.width):
                for y in range(self.height):
                    if self.grid[x][y][3] == 0 and (x, y) in exterior: 
                        solid_neighbors = []
                        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nnx, nny = x + ddx, y + ddy
                            if 0 <= nnx < self.width and 0 <= nny < self.height:
                                if self.grid[nnx][nny][3] != 0:
                                    # Don't count already-placed outlines as source
                                    if (nnx, nny) not in self._outline_pixels:
                                        solid_neighbors.append(self.grid[nnx][nny])
                                    else:
                                        solid_neighbors.append(self.grid[nnx][nny])
                        
                        if solid_neighbors:
                            if sel_out:
                                # Find the darkest non-outline neighbor for better color matching
                                best = solid_neighbors[0]
                                for sn in solid_neighbors:
                                    if (sn[0] + sn[1] + sn[2]) > (best[0] + best[1] + best[2]):
                                        best = sn  # Pick the brightest neighbor as base
                                
                                nc = best
                                h, l, s = colorsys.rgb_to_hls(nc[0] / 255.0, nc[1] / 255.0, nc[2] / 255.0)
                                new_h = (h + hue_shift_amount) % 1.0 
                                new_l = max(0.0, l * darkness) 
                                new_s = min(1.0, s * saturation_boost) 
                                new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, new_s)
                                new_grid[x][y] = (int(new_r * 255), int(new_g * 255), int(new_b * 255), 255)
                            else:
                                new_grid[x][y] = outline_color
                            self._outline_pixels.add((x, y))
                            
            self.grid = [[new_grid[x][y] for y in range(self.height)] for x in range(self.width)]
            
    def cleanup_jaggies(self, outline_color: str = "#000000FF"):
        """Remove single-pixel 'step' jaggies from outlines.
        Now works with both solid-color and sel_out (multi-color) outlines.
        """
        # Use tracked outline pixels if available (from sel_out), else fallback to color match
        if hasattr(self, '_outline_pixels') and self._outline_pixels:
            outline_set = self._outline_pixels
            
            def is_outline(x, y):
                return (x, y) in outline_set
        else:
            oc = self._get_color(outline_color)
            
            def is_outline(x, y):
                if 0 <= x < self.width and 0 <= y < self.height:
                    return self.grid[x][y] == oc
                return False
            
        to_remove = []
        for x in range(self.width):
            for y in range(self.height):
                if is_outline(x, y):
                    neighbors = []
                    if is_outline(x, y-1): neighbors.append((x, y-1))
                    if is_outline(x, y+1): neighbors.append((x, y+1))
                    if is_outline(x-1, y): neighbors.append((x-1, y))
                    if is_outline(x+1, y): neighbors.append((x+1, y))
                    
                    if len(neighbors) == 2:
                        n1, n2 = neighbors
                        if n1[0] != n2[0] and n1[1] != n2[1]:
                            ix, iy = n1[0] + n2[0] - x, n1[1] + n2[1] - y
                            ox, oy = x - (ix - x), y - (iy - y)
                            if 0 <= ox < self.width and 0 <= oy < self.height:
                                if self.grid[ox][oy][3] == 0:
                                    to_remove.append((x, y))
                                    
        for rx, ry in to_remove:
            self.grid[rx][ry] = (0, 0, 0, 0)
            if hasattr(self, '_outline_pixels'):
                self._outline_pixels.discard((rx, ry))
            
    def apply_internal_aa(self):
        """Apply anti-aliasing at internal color boundaries.
        Creates smoother transitions between different colored regions.
        """
        new_grid = [[self.grid[x][y] for y in range(self.height)] for x in range(self.width)]
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                c = self.grid[x][y]
                if c[3] == 0: continue
                
                up = self.grid[x][y-1]
                down = self.grid[x][y+1]
                left = self.grid[x-1][y]
                right = self.grid[x+1][y]
                
                for c1, c2, dx, dy in [(left, down, -1, 1), (right, down, 1, 1), (left, up, -1, -1), (right, up, 1, -1)]:
                    if c1 == c2 and c1 != c and c1[3] > 0 and c[3] > 0:
                        blend_r = int((c[0] + c1[0]) / 2)
                        blend_g = int((c[1] + c1[1]) / 2)
                        blend_b = int((c[2] + c1[2]) / 2)
                        corn_x, corn_y = x + dx, y + dy
                        if 0 <= corn_x < self.width and 0 <= corn_y < self.height:
                            if self.grid[corn_x][corn_y] == c: 
                                new_grid[x][y] = (blend_r, blend_g, blend_b, 255)
                                break
        self.grid = new_grid

    def add_highlight_edge(self, light_dir: str = "top_left", color: Optional[str] = None, intensity: float = 0.3):
        """Add a subtle highlight along the edges facing the light source.
        This creates rim lighting effect common in professional pixel art.
        
        Args:
            light_dir: Direction of light source
            color: Highlight color (default: white)
            intensity: Blend intensity 0-1
            
        Example:
            canvas.add_highlight_edge(light_dir="top_left", intensity=0.2)
        """
        highlight = self._get_color(color) if color else (255, 255, 255, 255)
        hr, hg, hb = highlight[0], highlight[1], highlight[2]
        lx, ly, _ = self._get_light_vector(light_dir)
        
        for x in range(self.width):
            for y in range(self.height):
                current = self.grid[x][y]
                if current[3] == 0:
                    continue
                
                # Check if this pixel is on the edge facing the light
                # A pixel is on the light-facing edge if it has a transparent neighbor
                # in the direction the light comes FROM
                check_x = x + int(lx)
                check_y = y + int(ly)
                
                is_edge = False
                if not (0 <= check_x < self.width and 0 <= check_y < self.height):
                    is_edge = True
                elif self.grid[check_x][check_y][3] == 0:
                    is_edge = True
                
                if is_edge:
                    blend_r = int(current[0] * (1 - intensity) + hr * intensity)
                    blend_g = int(current[1] * (1 - intensity) + hg * intensity)
                    blend_b = int(current[2] * (1 - intensity) + hb * intensity)
                    self.grid[x][y] = (blend_r, blend_g, blend_b, current[3])

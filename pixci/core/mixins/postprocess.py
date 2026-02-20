import math
from typing import Tuple
from ..canvas_base import BaseCanvas

class PostprocessMixin(BaseCanvas):
    def apply_shadow_mask(self, center: Tuple[int, int], radius: int, light_dir: str = "top_left", intensity: float = 0.5, shadow_color: str = "#201020"):
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

    def add_outline(self, color: str = "#000000FF", thickness: int = 1, sel_out: bool = False):
        import colorsys
        outline_color = self._get_color(color)
        new_grid = [[self.grid[x][y] for y in range(self.height)] for x in range(self.width)]
        
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
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[nx][ny][3] == 0 and (nx, ny) not in exterior:
                        exterior.add((nx, ny))
                        queue.append((nx, ny))
                        
        for t in range(thickness):
            for x in range(self.width):
                for y in range(self.height):
                    if self.grid[x][y][3] == 0 and (x, y) in exterior: 
                        solid_neighbors = []
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.grid[nx][ny][3] != 0 and self.grid[nx][ny] != outline_color:
                                    solid_neighbors.append(self.grid[nx][ny])
                        
                        if solid_neighbors:
                            if sel_out:
                                nc = solid_neighbors[0]
                                h, l, s = colorsys.rgb_to_hls(nc[0] / 255.0, nc[1] / 255.0, nc[2] / 255.0)
                                new_h = (h + 0.05) % 1.0 
                                new_l = max(0.0, l * 0.4) 
                                new_s = min(1.0, s * 1.2) 
                                new_r, new_g, new_b = colorsys.hls_to_rgb(new_h, new_l, new_s)
                                new_grid[x][y] = (int(new_r * 255), int(new_g * 255), int(new_b * 255), 255)
                            else:
                                new_grid[x][y] = outline_color
                            
            self.grid = [[new_grid[x][y] for y in range(self.height)] for x in range(self.width)]
            
    def cleanup_jaggies(self, outline_color: str = "#000000FF"):
        oc = self._get_color(outline_color)
        
        def is_oc(x, y):
            if 0 <= x < self.width and 0 <= y < self.height:
                return self.grid[x][y] == oc
            return False
            
        to_remove = []
        for x in range(self.width):
            for y in range(self.height):
                if is_oc(x, y):
                    neighbors = []
                    if is_oc(x, y-1): neighbors.append((x, y-1))
                    if is_oc(x, y+1): neighbors.append((x, y+1))
                    if is_oc(x-1, y): neighbors.append((x-1, y))
                    if is_oc(x+1, y): neighbors.append((x+1, y))
                    
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
            
    def apply_internal_aa(self):
        new_grid = [[self.grid[x][y] for y in range(self.height)] for x in range(self.width)]
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                c = self.grid[x][y]
                if c[3] == 0: continue
                
                up = self.grid[x][y-1]
                down = self.grid[x][y+1]
                left = self.grid[x-1][y]
                right = self.grid[x+1][y]
                
                # Detect inner corner (L-shape) of same color
                # Example: left and down are the SAME color as each other, but DIFFERENT from center
                # And that color is also solid
                for c1, c2, dx, dy in [(left, down, -1, 1), (right, down, 1, 1), (left, up, -1, -1), (right, up, 1, -1)]:
                    if c1 == c2 and c1 != c and c1[3] > 0 and c[3] > 0:
                        # Blend center with c1 to create AA pixel
                        blend_r = int((c[0] + c1[0]) / 2)
                        blend_g = int((c[1] + c1[1]) / 2)
                        blend_b = int((c[2] + c1[2]) / 2)
                        # We apply it to the corner pixel (dx, dy) relative to the intersection point
                        corn_x, corn_y = x + dx, y + dy
                        if 0 <= corn_x < self.width and 0 <= corn_y < self.height:
                            if self.grid[corn_x][corn_y] == c: 
                                new_grid[x][y] = (blend_r, blend_g, blend_b, 255)
                                break
        self.grid = new_grid

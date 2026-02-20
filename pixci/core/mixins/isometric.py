from typing import Tuple
from ..canvas_base import BaseCanvas

class IsometricMixin(BaseCanvas):
    def draw_iso_cube(self, center: Tuple[int, int], width: int, height: int, depth: int, color_top: str, color_left: str, color_right: str):
        xc, yc = center
        
        # We assume center is the bottommost point of the cube
        
        # Calculate vertices
        # Isometric projection logic: 
        # x_iso = (x - z)
        # y_iso = (x + z) / 2 - y
        
        # Here we just draw 3 quads
        
        y_top = yc - height
        
        # Draw Left Face (width x height)
        for dx in range(width):
            for dy in range(height):
                screen_x = xc - dx
                screen_y = yc - dy - (dx // 2)
                self.set_pixel((screen_x, screen_y), color_left)
                
        # Draw Right Face (depth x height)
        for dz in range(depth):
            for dy in range(height):
                screen_x = xc + dz
                screen_y = yc - dy - (dz // 2)
                if dz > 0: # Avoid overdraw on center edge
                    self.set_pixel((screen_x, screen_y), color_right)
                    
        # Draw Top Face (width x depth)
        for dx in range(width):
            for dz in range(depth):
                screen_x = xc - dx + dz
                screen_y = y_top - (dx // 2) - (dz // 2)
                self.set_pixel((screen_x, screen_y), color_top)

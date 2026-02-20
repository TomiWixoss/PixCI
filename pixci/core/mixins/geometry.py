from typing import Tuple
from ..canvas_base import BaseCanvas

class GeometryMixin(BaseCanvas):
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

    def fill_rect(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], color: str):
        x0, y0 = top_left
        x1, y1 = bottom_right
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set_pixel((x, y), color)

    def fill_circle(self, center: Tuple[int, int], radius: int, color: str):
        self.fill_ellipse(center, radius, radius, color)

    def draw_circle(self, center: Tuple[int, int], radius: int, color: str, pixel_perfect: bool = False):
        self.draw_ellipse(center, radius, radius, color, pixel_perfect)

    def fill_ellipse(self, center: Tuple[int, int], rx: int, ry: int, color: str):
        xc, yc = center
        for x in range(xc - rx, xc + rx + 1):
            for y in range(yc - ry, yc + ry + 1):
                dx = x - xc
                dy = y - yc
                if (dx * dx) / max(rx * rx, 1) + (dy * dy) / max(ry * ry, 1) <= 1.0:
                    self.set_pixel((x, y), color)

    def draw_ellipse(self, center: Tuple[int, int], rx: int, ry: int, color: str, pixel_perfect: bool = False):
        xc, yc = center
        x = 0
        y = ry
        d1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
        dx = 2 * ry * ry * x
        dy = 2 * rx * rx * y

        while dx < dy:
            self.set_pixel((xc + x, yc + y), color)
            self.set_pixel((xc - x, yc + y), color)
            self.set_pixel((xc + x, yc - y), color)
            self.set_pixel((xc - x, yc - y), color)
            if d1 < 0:
                x += 1
                dx = dx + (2 * ry * ry)
                d1 = d1 + dx + (ry * ry)
            else:
                x += 1
                y -= 1
                dx = dx + (2 * ry * ry)
                dy = dy - (2 * rx * rx)
                d1 = d1 + dx - dy + (ry * ry)

        d2 = ((ry * ry) * ((x + 0.5) * (x + 0.5))) + ((rx * rx) * ((y - 1) * (y - 1))) - (rx * rx * ry * ry)

        while y >= 0:
            self.set_pixel((xc + x, yc + y), color)
            self.set_pixel((xc - x, yc + y), color)
            self.set_pixel((xc + x, yc - y), color)
            self.set_pixel((xc - x, yc - y), color)
            if d2 > 0:
                y -= 1
                dy = dy - (2 * rx * rx)
                d2 = d2 + (rx * rx) - dy
            else:
                y -= 1
                x += 1
                dx = dx + (2 * ry * ry)
                dy = dy - (2 * rx * rx)
                d2 = d2 + dx - dy + (rx * rx)

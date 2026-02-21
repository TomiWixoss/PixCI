from typing import Tuple, List, Union
from ..canvas_base import BaseCanvas

class GeometryMixin(BaseCanvas):
    def _draw_thick_point(self, pos: Tuple[int, int], color: str, thickness: int = 1):
        if thickness <= 1:
            self.set_pixel(pos, color)
        else:
            self.fill_circle(pos, thickness // 2, color)

    def draw_line(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], color: str, thickness: int = 1):
        """Bresenham line from start_pos to end_pos."""
        x0, y0 = start_pos
        x1, y1 = end_pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self._draw_thick_point((x0, y0), color, thickness)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_rows(self, rows: List[Tuple[int, int, int, str]]):
        """Draw multiple horizontal spans in one call.
        Each row: (y, x_start, x_end, color)
        This is the PREFERRED way for AI to sculpt complex shapes
        like mushroom caps, character bodies, etc.
        
        Example - Drawing a dome:
            canvas.draw_rows([
                (5,  13, 18, "R1"),  # narrow top
                (6,  11, 20, "R1"),  # wider
                (7,   9, 22, "R1"),  # widest band
                (8,   9, 22, "R1"),
                (9,  10, 21, "R1"),  # taper bottom
            ])
        """
        for entry in rows:
            y, x_start, x_end, color = entry
            for x in range(x_start, x_end + 1):
                self.set_pixel((x, y), color)

    def draw_polyline(self, points: List[Tuple[int, int]], color: str, closed: bool = False, thickness: int = 1):
        """Draw connected line segments through a series of points.
        If closed=True, also connects the last point back to the first.
        """
        if len(points) < 2:
            if len(points) == 1:
                self._draw_thick_point(points[0], color, thickness)
            return
        for i in range(len(points) - 1):
            self.draw_line(points[i], points[i + 1], color, thickness)
        if closed:
            self.draw_line(points[-1], points[0], color, thickness)

    def fill_polygon(self, points: List[Tuple[int, int]], color: str):
        """Fill an arbitrary polygon defined by vertex points.
        Uses scanline fill algorithm. Points should be ordered (CW or CCW).
        
        Example - Drawing a leaf shape:
            canvas.fill_polygon([
                (16, 5), (20, 8), (22, 14), (18, 18), (14, 18), (10, 14), (12, 8)
            ], "G1")
        """
        if len(points) < 3:
            return
        
        # Find bounding box
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        
        # Scanline fill
        for y in range(min_y, max_y + 1):
            # Find all intersections with polygon edges
            intersections = []
            n = len(points)
            for i in range(n):
                j = (i + 1) % n
                y0 = points[i][1]
                y1 = points[j][1]
                
                if y0 == y1:
                    continue  # Skip horizontal edges
                
                if min(y0, y1) <= y < max(y0, y1):
                    # Compute x intersection
                    x_intersect = points[i][0] + (y - y0) * (points[j][0] - points[i][0]) / (y1 - y0)
                    intersections.append(x_intersect)
            
            intersections.sort()
            
            # Fill between pairs
            for k in range(0, len(intersections) - 1, 2):
                x_start = int(round(intersections[k]))
                x_end = int(round(intersections[k + 1]))
                x_start = max(x_start, min_x)
                x_end = min(x_end, max_x)
                for x in range(x_start, x_end + 1):
                    self.set_pixel((x, y), color)

    def draw_curve(self, start_pos: Tuple[int, int], control_pos: Tuple[int, int], end_pos: Tuple[int, int], color: str, pixel_perfect: bool = True, thickness: int = 1):
        """Quadratic Bezier curve with optional pixel-perfect cleanup."""
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
                    pass  # skip to remove L-shape jaggies
                else:
                    clean.append(curr)
            clean.append(unique_pts[-1])
            unique_pts = clean
            
        for p in unique_pts:
            self._draw_thick_point(p, color, thickness)

    def draw_cubic_curve(self, p0: Tuple[int, int], p1: Tuple[int, int], p2: Tuple[int, int], p3: Tuple[int, int], color: str, thickness: int = 1):
        """Cubic Bezier curve (4 control points) for smoother curves like S-shapes."""
        x0, y0 = p0
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        dist = max(abs(x3 - x0), abs(y3 - y0)) * 3 + 20
        
        prev_point = None
        for i in range(dist + 1):
            t = i / dist
            nt = 1 - t
            x = nt**3 * x0 + 3 * nt**2 * t * x1 + 3 * nt * t**2 * x2 + t**3 * x3
            y = nt**3 * y0 + 3 * nt**2 * t * y1 + 3 * nt * t**2 * y2 + t**3 * y3
            pt = (int(round(x)), int(round(y)))
            if pt != prev_point:
                self._draw_thick_point(pt, color, thickness)
                prev_point = pt



    def fill_rect(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], color: str):
        x0, y0 = top_left
        x1, y1 = bottom_right
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                self.set_pixel((x, y), color)

    def fill_rounded_rect(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], radius: int, color: str):
        """Fill a rectangle with rounded corners. Radius controls corner rounding.
        
        Example - UI button or item frame:
            canvas.fill_rounded_rect((4, 4), (28, 12), 2, "S1")
        """
        x0, y0 = top_left
        x1, y1 = bottom_right
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
        
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                # Check if we're in a corner region
                corner_x = corner_y = None
                if x < x0 + r and y < y0 + r:
                    corner_x, corner_y = x0 + r, y0 + r
                elif x > x1 - r and y < y0 + r:
                    corner_x, corner_y = x1 - r, y0 + r
                elif x < x0 + r and y > y1 - r:
                    corner_x, corner_y = x0 + r, y1 - r
                elif x > x1 - r and y > y1 - r:
                    corner_x, corner_y = x1 - r, y1 - r
                
                if corner_x is not None:
                    dx = x - corner_x
                    dy = y - corner_y
                    if dx * dx + dy * dy > r * r:
                        continue
                
                self.set_pixel((x, y), color)

    def fill_circle(self, center: Tuple[int, int], radius: int, color: str):
        self.fill_ellipse(center, radius, radius, color)

    def draw_circle(self, center: Tuple[int, int], radius: int, color: str, pixel_perfect: bool = False):
        self.draw_ellipse(center, radius, radius, color, pixel_perfect)

    def _get_ellipse_quadrant(self, rx: int, ry: int) -> List[Tuple[int, int]]:
        if rx == 0 and ry == 0:
            return [(0,0)]
        pts = []
        x = 0
        y = ry
        d1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
        dx = 2 * ry * ry * x
        dy = 2 * rx * rx * y
        while dx < dy:
            pts.append((x, y))
            if d1 < 0:
                x += 1
                dx += 2 * ry * ry
                d1 += dx + ry * ry
            else:
                x += 1
                y -= 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d1 += dx - dy + ry * ry
                
        pts2 = []
        d2 = (ry * ry) * ((x + 0.5) * (x + 0.5)) + (rx * rx) * ((y - 1) * (y - 1)) - (rx * rx * ry * ry)
        while y >= 0:
            pts2.append((x, y))
            if d2 > 0:
                y -= 1
                dy -= 2 * rx * rx
                d2 += rx * rx - dy
            else:
                y -= 1
                x += 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d2 += dx - dy + rx * rx
                
        return pts + pts2

    def fill_ellipse(self, center: Tuple[int, int], rx: int, ry: int, color: str):
        xc, yc = center
        q = self._get_ellipse_quadrant(rx, ry)
        y_to_maxx = {}
        for x, y in q:
            if y not in y_to_maxx or x > y_to_maxx[y]:
                y_to_maxx[y] = x
                
        for y, max_x in y_to_maxx.items():
            for x in range(-max_x, max_x + 1):
                self.set_pixel((xc + x, yc + y), color)
                if y != 0:
                    self.set_pixel((xc + x, yc - y), color)

    def draw_ellipse(self, center: Tuple[int, int], rx: int, ry: int, color: str, pixel_perfect: bool = False):
        xc, yc = center
        q = self._get_ellipse_quadrant(rx, ry)
        
        if pixel_perfect and len(q) > 2:
            clean_q = [q[0]]
            for i in range(1, len(q)-1):
                prev = clean_q[-1]
                curr = q[i]
                nxt = q[i+1]
                dx1, dy1 = curr[0]-prev[0], curr[1]-prev[1]
                dx2, dy2 = nxt[0]-curr[0], nxt[1]-curr[1]
                if (abs(dx1) == 1 and dy1 == 0 and dx2 == 0 and abs(dy2) == 1) or \
                   (dx1 == 0 and abs(dy1) == 1 and abs(dx2) == 1 and dy2 == 0):
                    continue
                clean_q.append(curr)
            clean_q.append(q[-1])
            q = clean_q

        # Add all 4 quadrants
        for x, y in q:
            self.set_pixel((xc + x, yc + y), color)
            self.set_pixel((xc - x, yc + y), color)
            self.set_pixel((xc + x, yc - y), color)
            self.set_pixel((xc - x, yc - y), color)

    # =================================================================
    # ANCHOR-BASED DRAWING - AI vẽ bằng điểm neo thay vì toạ độ thô
    # =================================================================

    def fill_rect_centered(self, center: Tuple[int, int], width: int, height: int, color: str):
        """Fill a rectangle defined by CENTER + SIZE thay vì top-left/bottom-right.
        AI chỉ cần biết "tâm" và "kích thước" → không cần tính toạ độ góc.
        
        Example:
            cx, cy = canvas.get_center()
            canvas.fill_rect_centered((cx, 24), width=6, height=8, color="S1")
        """
        x0, x1 = self.span(center[0], width)
        y0, y1 = self.span(center[1], height)
        self.fill_rect((x0, y0), (x1, y1), color)

    def fill_ellipse_anchored(self, anchor: Tuple[int, int], rx: int, ry: int, color: str, align: str = "center"):
        """Fill an ellipse positioned by ANCHOR POINT + ALIGNMENT.
        AI không cần tính tâm thật, chỉ cần nói "đặt ở đáy của điểm neo".
        
        Args:
            anchor: (x, y) điểm neo
            rx, ry: Bán kính ngang/dọc
            align: 
                "center" → anchor = tâm ellipse
                "bottom" → anchor = đáy ellipse (tâm y dịch lên ry pixel)  
                "top"    → anchor = đỉnh ellipse (tâm y dịch xuống ry pixel)
        
        Example:
            ground_y = canvas.get_ground()
            cx = canvas.get_center()[0]
            # Đặt thân nấm chạm mặt đất
            canvas.fill_ellipse_anchored((cx, ground_y), rx=3, ry=6, color="S1", align="bottom")
            # Đặt mũ nấm đội lên trên thân
            cap_y = ground_y - 12
            canvas.fill_ellipse_anchored((cx, cap_y), rx=10, ry=5, color="R1", align="bottom")
        """
        ax, ay = anchor
        if align == "bottom":
            center = (ax, ay - ry)
        elif align == "top":
            center = (ax, ay + ry)
        else:
            center = (ax, ay)
        self.fill_ellipse(center, rx, ry, color)

    def fill_rect_anchored(self, anchor: Tuple[int, int], width: int, height: int, color: str, align: str = "center"):
        """Fill a rectangle positioned by ANCHOR + ALIGNMENT.
        
        Args:
            anchor: (x, y) điểm neo
            width, height: Kích thước
            align:
                "center"       → anchor = tâm rect
                "bottom"       → anchor = tâm-đáy (bottom-center)
                "top"          → anchor = tâm-đỉnh (top-center)
                "bottom_left"  → anchor = góc dưới trái
                "bottom_right" → anchor = góc dưới phải
        """
        ax, ay = anchor
        half_w = width // 2
        
        if align == "center":
            x0, y0 = ax - half_w, ay - height // 2
        elif align == "bottom":
            x0, y0 = ax - half_w, ay - height + 1
        elif align == "top":
            x0, y0 = ax - half_w, ay
        elif align == "bottom_left":
            x0, y0 = ax, ay - height + 1
        elif align == "bottom_right":
            x0, y0 = ax - width + 1, ay - height + 1
        else:
            x0, y0 = ax - half_w, ay - height // 2
        
        x1 = x0 + width - 1
        y1 = y0 + height - 1
        self.fill_rect((x0, y0), (x1, y1), color)


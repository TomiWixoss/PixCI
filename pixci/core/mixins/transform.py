from typing import Tuple
from ..canvas_base import BaseCanvas

class TransformMixin(BaseCanvas):
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

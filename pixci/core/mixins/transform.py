from typing import Tuple, Optional, List
from ..canvas_base import BaseCanvas

class TransformMixin(BaseCanvas):
    def translate(self, offset_x: int, offset_y: int):
        """Move all pixels on the active layer by (offset_x, offset_y)."""
        new_grid = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                nx = x + offset_x
                ny = y + offset_y
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    new_grid[nx][ny] = self.grid[x][y]
        self.grid = new_grid

    def flip_x(self):
        """Flip the active layer horizontally."""
        new_grid = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                new_grid[self.width - 1 - x][y] = self.grid[x][y]
        self.grid = new_grid

    def flip_y(self):
        """Flip the active layer vertically."""
        new_grid = [[(0, 0, 0, 0)] * self.height for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                new_grid[x][self.height - 1 - y] = self.grid[x][y]
        self.grid = new_grid

    def mirror_x(self):
        """Mirror the left half of the active layer to the right half."""
        for y in range(self.height):
            for x in range(self.width // 2):
                self.grid[self.width - 1 - x][y] = self.grid[x][y]

    def mirror_y(self):
        """Mirror the top half of the active layer to the bottom half."""
        for x in range(self.width):
            for y in range(self.height // 2):
                self.grid[x][self.height - 1 - y] = self.grid[x][y]

    def fill_bucket(self, start_pos: Tuple[int, int], color: str):
        """Flood fill from start_pos with the given color."""
        x, y = start_pos
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        target_color = self.grid[x][y]
        replacement_color = self._get_color(color)
        if target_color == replacement_color:
            return

        queue = [(x, y)]
        visited = set()
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            if self.grid[cx][cy] == target_color:
                self.grid[cx][cy] = replacement_color
                if cx > 0: queue.append((cx - 1, cy))
                if cx < self.width - 1: queue.append((cx + 1, cy))
                if cy > 0: queue.append((cx, cy - 1))
                if cy < self.height - 1: queue.append((cx, cy + 1))

    def copy_region(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int]) -> List[List[Tuple[int, int, int, int]]]:
        """Copy a rectangular region of pixels. Returns the copied data.
        
        Example:
            # Copy a 5x5 region
            copied = canvas.copy_region((0, 0), (4, 4))
            canvas.paste_region(copied, (10, 10))
        """
        x0, y0 = top_left
        x1, y1 = bottom_right
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        
        region = []
        for x in range(x0, x1 + 1):
            col = []
            for y in range(y0, y1 + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    col.append(self.grid[x][y])
                else:
                    col.append((0, 0, 0, 0))
            region.append(col)
        return region

    def paste_region(self, data: List[List[Tuple[int, int, int, int]]], position: Tuple[int, int], skip_transparent: bool = True):
        """Paste previously copied pixel data at the given position.
        
        Args:
            data: Pixel data from copy_region()
            position: (x, y) top-left corner to paste at
            skip_transparent: If True, transparent pixels in data won't overwrite existing pixels
        """
        px, py = position
        for dx, col in enumerate(data):
            for dy, pixel in enumerate(col):
                x = px + dx
                y = py + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    if skip_transparent and pixel[3] == 0:
                        continue
                    if self.alpha_lock and self.grid[x][y][3] == 0:
                        continue
                    self.grid[x][y] = pixel

    def paste(self, canvas: 'BaseCanvas', position: Tuple[int, int] = (0, 0)):
        """Paste another Canvas into this Canvas at the given position.
        
        Example:
            body = Canvas(32, 32)
            # ... draw body ...
            frame.paste(body, (0, -4))
        """
        data = canvas.copy_region((0, 0), (canvas.width - 1, canvas.height - 1))
        self.paste_region(data, position, skip_transparent=True)

    def stamp(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], target: Tuple[int, int]):
        """Copy a region and paste it at target. Shortcut for copy_region + paste_region.
        
        Example:
            # Duplicate a tree at another position
            canvas.stamp((0, 0), (15, 20), (16, 0))
        """
        data = self.copy_region(top_left, bottom_right)
        self.paste_region(data, target)

    def mirror_x(self, axis_x: Optional[int] = None):
        """Mirror the left half of the sprite to the right half (or vice versa).
        Useful for creating symmetrical characters.
        
        Args:
            axis_x: X coordinate of the mirror axis. Default: center of canvas.
            
        Example:
            # Draw only the left half of a face, then mirror
            canvas.mirror_x()
        """
        if axis_x is None:
            axis_x = self.width // 2
        
        for x in range(axis_x):
            mirror_x = self.width - 1 - x
            if 0 <= mirror_x < self.width:
                for y in range(self.height):
                    if self.grid[x][y][3] > 0:
                        self.grid[mirror_x][y] = self.grid[x][y]

    def preview(self) -> str:
        """Return a text-grid representation of the current canvas state.
        This allows AI to 'see' what it has drawn so far.
        
        Transparent pixels are shown as '.', colored pixels as block characters
        with approximate colors indicated.
        
        Returns: Multi-line string showing the canvas grid.
        """
        # Build a simple character representation
        lines = []
        lines.append(f"=== Canvas Preview ({self.width}x{self.height}) ===")
        
        # Map colors to short labels
        reverse_palette = {}
        for key, rgba in self.palette.items():
            reverse_palette[rgba] = key
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                pixel = self.grid[x][y]
                if pixel[3] == 0:
                    row.append(" .")
                elif pixel in reverse_palette:
                    label = reverse_palette[pixel]
                    row.append(f"{label:>2}")
                else:
                    # Unknown color - show as ##
                    row.append(" #")
            lines.append(" ".join(row))
        
        return "\n".join(lines)

    def snapshot(self) -> List[List[Tuple[int, int, int, int]]]:
        """Take a snapshot of the current active layer. Can be restored with restore_snapshot().
        
        Example:
            snap = canvas.snapshot()
            # ... try some edits ...
            canvas.restore_snapshot(snap)  # undo if needed
        """
        return [[self.grid[x][y] for y in range(self.height)] for x in range(self.width)]

    def restore_snapshot(self, snapshot: List[List[Tuple[int, int, int, int]]]):
        """Restore a previously taken snapshot."""
        self.grid = [[snapshot[x][y] for y in range(self.height)] for x in range(self.width)]

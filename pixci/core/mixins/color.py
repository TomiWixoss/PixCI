import colorsys
from typing import Dict, List
from ..canvas_base import BaseCanvas, hex2rgba

class ColorMixin(BaseCanvas):
    def add_color(self, char: str, color_code: str):
        self.palette[char] = hex2rgba(color_code)

    def add_palette(self, palette_dict: Dict[str, str]):
        for char, color_code in palette_dict.items():
            self.add_color(char, color_code)

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

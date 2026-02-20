import colorsys
from typing import Dict, List, Tuple, Optional
from ..canvas_base import BaseCanvas, hex2rgba

# ============================================================
# BUILT-IN PALETTES - Các bảng màu huyền thoại cho Pixel Art
# ============================================================
BUILTIN_PALETTES = {
    "endesga32": {
        "01": "#BE4A2FFF", "02": "#D77643FF", "03": "#EAD4AAFF", "04": "#E4A672FF",
        "05": "#B86F50FF", "06": "#733E39FF", "07": "#3E2731FF", "08": "#A22633FF",
        "09": "#E43B44FF", "10": "#F77622FF", "11": "#FEAE34FF", "12": "#FEE761FF",
        "13": "#63C74DFF", "14": "#3E8948FF", "15": "#265C42FF", "16": "#193C3EFF",
        "17": "#124E89FF", "18": "#0099DBFF", "19": "#2CE8F5FF", "20": "#FFFFFFFE",
        "21": "#C0CBDCFF", "22": "#8B9BB4FF", "23": "#5A6988FF", "24": "#3A4466FF",
        "25": "#262B44FF", "26": "#181425FF", "27": "#FF0044FF", "28": "#68386CFF",
        "29": "#B55088FF", "30": "#F6757AFF", "31": "#E8B796FF", "32": "#C28569FF",
    },
    "pico8": {
        "BK": "#000000FF", "DN": "#1D2B53FF", "DP": "#7E2553FF", "DG": "#008751FF",
        "BR": "#AB5236FF", "GY": "#5F574FFF", "LG": "#C2C3C7FF", "WH": "#FFF1E8FF",
        "RD": "#FF004DFF", "OR": "#FFA300FF", "YE": "#FFEC27FF", "GN": "#00E436FF",
        "BL": "#29ADFFFF", "LV": "#83769CFF", "PK": "#FF77A8FF", "PC": "#FFCCAAFF",
    },
    "sweetie16": {
        "01": "#1A1C2CFF", "02": "#5D275DFF", "03": "#B13E53FF", "04": "#EF7D57FF",
        "05": "#FFCD75FF", "06": "#A7F070FF", "07": "#38B764FF", "08": "#257179FF",
        "09": "#29366FFF", "10": "#3B5DC9FF", "11": "#41A6F6FF", "12": "#73EFF7FF",
        "13": "#F4F4F4FF", "14": "#94B0C2FF", "15": "#566C86FF", "16": "#333C57FF",
    },
    "nes": {
        "BK": "#000000FF", "DG": "#626262FF", "LG": "#898989FF", "WH": "#ADADADFF",
        "R1": "#FF0000FF", "R2": "#AB0000FF", "G1": "#00FF00FF", "G2": "#006B00FF",
        "B1": "#0000FFFF", "B2": "#0000ABFF", "Y1": "#FFFF00FF", "OR": "#FF6B00FF",
        "CY": "#00FFFFFF", "PU": "#FF00FFFF", "SK": "#FFB6ADFF", "TN": "#004040FF",
    },
    "gameboy": {
        "D0": "#0F380FFF",  # Darkest
        "D1": "#306230FF",  # Dark
        "D2": "#8BAC0FFF",  # Light  
        "D3": "#9BBC0FFF",  # Lightest
    },
}


class ColorMixin(BaseCanvas):
    def add_color(self, char: str, color_code: str):
        """Add a single color to the palette."""
        self.palette[char] = hex2rgba(color_code)

    def add_palette(self, palette_dict: Dict[str, str]):
        """Add multiple colors to the palette from a dictionary.
        
        Example:
            canvas.add_palette({
                "R1": "#E62E2D",  # Base red
                "R2": "#B31C26",  # Dark red (shadow)
                "R3": "#FF6B6B",  # Light red (highlight)
            })
        """
        for char, color_code in palette_dict.items():
            self.add_color(char, color_code)

    def load_palette(self, name: str, prefix: str = ""):
        """Load a built-in pixel art palette.
        
        Available palettes: 'endesga32', 'pico8', 'sweetie16', 'nes', 'gameboy'
        
        Args:
            name: Name of the built-in palette
            prefix: Optional prefix to add to all color keys (to avoid collisions)
            
        Example:
            canvas.load_palette("pico8")
            canvas.fill_rect((0, 0), (10, 10), "RD")  # pico-8 red
            
            # With prefix to avoid collision
            canvas.load_palette("endesga32", prefix="E_")
            canvas.fill_rect((0, 0), (10, 10), "E_09")
        """
        if name.lower() not in BUILTIN_PALETTES:
            available = ", ".join(BUILTIN_PALETTES.keys())
            raise ValueError(f"Palette '{name}' not found. Available: {available}")
        
        palette_data = BUILTIN_PALETTES[name.lower()]
        for key, hex_val in palette_data.items():
            self.palette[prefix + key] = hex2rgba(hex_val)

    def list_palettes(self) -> List[str]:
        """List all available built-in palette names."""
        return list(BUILTIN_PALETTES.keys())

    def generate_ramp(self, base_color: str, steps: int, mode: str = "hue_shift") -> List[str]:
        """Generate a color ramp from a base color.
        
        Modes:
            'hue_shift' (default): Professional pixel art ramp with warm shadows,
                                   cool highlights, and hue rotation. Best quality.
            'linear': Simple lightness ramp without hue change.
            'warm_cool': Extreme warm-to-cool shift for dramatic lighting.
        
        Returns: List of hex color strings from darkest to lightest.
        
        Example:
            skin_ramp = canvas.generate_ramp("#E8A87C", 5, "hue_shift")
            canvas.add_palette({f"SK{i}": c for i, c in enumerate(skin_ramp)})
        """
        base_rgba = self._get_color(base_color)
        r, g, b = [x / 255.0 for x in base_rgba[:3]]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        ramp = []
        for i in range(steps):
            t = i / max(1, (steps - 1))  # 0.0 (darkest) to 1.0 (lightest)
            
            if mode == "hue_shift":
                # Warm shadows (shift hue toward red/orange), cool highlights (shift toward blue/cyan)
                # Shadow: +0.04 hue (warmer), Highlight: -0.03 hue (cooler)
                hue_shift = (0.5 - t) * 0.07
                new_h = (h + hue_shift) % 1.0
                
                # Shadows are more saturated, highlights desaturate slightly
                sat_curve = 1.0 + (0.5 - t) * 0.3  # 1.15 at shadow, 0.85 at highlight
                new_s = min(1.0, max(0.0, s * sat_curve))
                
                # Non-linear lightness curve (more detail in midtones)
                # Using a slight S-curve for more natural look
                lt = t * t * (3 - 2 * t)  # Smoothstep
                new_l = min(0.95, max(0.08, l * (0.35 + 1.1 * lt)))
                
            elif mode == "warm_cool":
                # Dramatic warm-to-cool shift
                hue_shift = (0.5 - t) * 0.12
                new_h = (h + hue_shift) % 1.0
                new_s = min(1.0, max(0.0, s * (1.0 + (0.5 - t) * 0.5)))
                lt = t * t * (3 - 2 * t)
                new_l = min(0.95, max(0.08, l * (0.3 + 1.2 * lt)))
                
            else:  # linear
                new_h = h
                new_s = s
                new_l = min(0.95, max(0.08, l * (0.4 + 1.0 * t)))
                
            nr, ng, nb = colorsys.hls_to_rgb(new_h, new_l, new_s)
            hex_val = f"#{int(nr*255):02X}{int(ng*255):02X}{int(nb*255):02X}FF"
            ramp.append(hex_val)
            
        return ramp

    def auto_shade(self, base_color: str, levels: int = 3) -> Dict[str, str]:
        """Generate shadow + highlight variants from a base color.
        Returns a dict like {"dark2": ..., "dark1": ..., "base": ..., "light1": ..., "light2": ...}
        
        Example:
            shades = canvas.auto_shade("#E62E2D", levels=2)
            canvas.add_palette(shades)
            # Now you can use: "dark2", "dark1", "base", "light1", "light2"
        """
        ramp = self.generate_ramp(base_color, levels * 2 + 1, "hue_shift")
        result = {}
        
        for i, hex_val in enumerate(ramp):
            offset = i - levels
            if offset < 0:
                key = f"dark{abs(offset)}"
            elif offset == 0:
                key = "base"
            else:
                key = f"light{offset}"
            result[key] = hex_val
        
        return result

    def complementary(self, base_color: str) -> str:
        """Get the complementary (opposite) color. Useful for accents."""
        base_rgba = self._get_color(base_color)
        r, g, b = [x / 255.0 for x in base_rgba[:3]]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        new_h = (h + 0.5) % 1.0
        nr, ng, nb = colorsys.hls_to_rgb(new_h, l, s)
        return f"#{int(nr*255):02X}{int(ng*255):02X}{int(nb*255):02X}FF"

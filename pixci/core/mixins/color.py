import colorsys
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from ..canvas_base import BaseCanvas, hex2rgba

# ============================================================
# LOSPEC PALETTE CACHE - Lưu palette đã tải về để dùng offline
# ============================================================
_CACHE_DIR = Path(__file__).parent.parent.parent.parent / ".palette_cache"

# Offline fallback cho 5 palette phổ biến nhất (dùng khi không có mạng)
_OFFLINE_PALETTES = {
    "endesga-32": [
        "be4a2f","d77643","ead4aa","e4a672","b86f50","733e39","3e2731","a22633",
        "e43b44","f77622","feae34","fee761","63c74d","3e8948","265c42","193c3e",
        "124e89","0099db","2ce8f5","ffffff","c0cbdc","8b9bb4","5a6988","3a4466",
        "262b44","181425","ff0044","68386c","b55088","f6757a","e8b796","c28569",
    ],
    "pico-8": [
        "000000","1d2b53","7e2553","008751","ab5236","5f574f","c2c3c7","fff1e8",
        "ff004d","ffa300","ffec27","00e436","29adff","83769c","ff77a8","ffccaa",
    ],
    "sweetie-16": [
        "1a1c2c","5d275d","b13e53","ef7d57","ffcd75","a7f070","38b764","257179",
        "29366f","3b5dc9","41a6f6","73eff7","f4f4f4","94b0c2","566c86","333c57",
    ],
    "resurrect-64": [
        "2e222f","3e3546","625565","966c6c","ab947a","694f62","7f708a","9babb2",
        "c7dcd0","ffffff","6e2727","b33831","ea4f36","f57d4a","ae2334","e83b3b",
        "fb6b1d","f79617","f9c22b","7a3045","9e4539","cd683d","e6904e","fbb954",
        "4c3e24","676633","a2a947","d5e04b","fbff86","165a4c","239063","1ebc73",
        "91db69","cddf6c","313638","374e4a","547e64","92a984","b2ba90","0b5e65",
        "0b8a8f","0eaf9b","30e1b9","8ff8e2","323353","484a77","4d65b4","4d9be6",
        "8fd3ff","45293f","6b3e75","905ea9","a884f3","eaaded","753c54","a24b6f",
        "cf657f","ed8099","831c5d","c32454","f04f78","f68181","fca790","fdcbb0",
    ],
    "gameboy": [
        "0f380f","306230","8bac0f","9bbc0f",
    ],
}


def _fetch_from_lospec(slug: str) -> Optional[List[str]]:
    """Fetch palette hex values from Lospec API."""
    import urllib.request
    import urllib.error
    
    url = f"https://lospec.com/palette-list/{slug}.hex"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PixCI/3.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("utf-8")
            colors = [line.strip().lower() for line in text.strip().splitlines() if line.strip()]
            if colors:
                return colors
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        pass
    return None


def _save_cache(slug: str, colors: List[str]):
    """Save palette to local cache for offline use."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _CACHE_DIR / f"{slug}.json"
    with open(cache_file, "w") as f:
        json.dump(colors, f)


def _load_cache(slug: str) -> Optional[List[str]]:
    """Load palette from local cache."""
    cache_file = _CACHE_DIR / f"{slug}.json"
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return None


def _hex_list_to_dict(colors: List[str], label_mode: str = "number") -> Dict[str, str]:
    """Convert a list of hex strings to a named palette dict.
    
    label_mode:
        'number' → "01", "02", ... (for most palettes)
    """
    result = {}
    for i, c in enumerate(colors):
        c = c.strip().lower()
        if not c.startswith("#"):
            c = "#" + c
        if len(c) == 7:  # #RRGGBB → #RRGGBBFF
            c += "ff"
        key = f"{i+1:02d}" if len(colors) > 9 else str(i + 1)
        result[key] = c.upper()
    return result


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
        """Load a pixel art palette by slug name.
        
        Supports 4000+ palettes from lospec.com!
        First checks local cache, then fetches from Lospec API,
        falls back to offline built-in palettes.
        
        Popular palettes: 'endesga-32', 'pico-8', 'sweetie-16', 
        'resurrect-64', 'gameboy', 'island-joy-16', 'apollo',
        'oil-6', 'fantasy-24', 'slso8', 'zughy-32', 
        'dreamscape8', 'aap-64', 'na16', 'dawnbringer-32', etc.
        
        Args:
            name: Lospec palette slug (the URL name, e.g. 'endesga-32')
            prefix: Optional prefix for color keys to avoid collisions
            
        Example:
            canvas.load_palette("endesga-32")
            canvas.fill_rect((0, 0), (10, 10), "09")  # Endesga red
            
            canvas.load_palette("pico-8", prefix="P_")
            canvas.fill_rect((0, 0), (10, 10), "P_9")  # Pico-8 red
        """
        slug = name.lower().strip()
        colors = None
        
        # 1. Check local cache
        colors = _load_cache(slug)
        
        # 2. Try Lospec API
        if colors is None:
            colors = _fetch_from_lospec(slug)
            if colors:
                _save_cache(slug, colors)  # Cache for offline use
        
        # 3. Fallback to offline built-in
        if colors is None and slug in _OFFLINE_PALETTES:
            colors = _OFFLINE_PALETTES[slug]
        
        if colors is None:
            offline_list = ", ".join(_OFFLINE_PALETTES.keys())
            raise ValueError(
                f"Palette '{name}' not found. "
                f"Check the slug at https://lospec.com/palette-list\n"
                f"Offline palettes available: {offline_list}"
            )
        
        palette_dict = _hex_list_to_dict(colors)
        for key, hex_val in palette_dict.items():
            self.palette[prefix + key] = hex2rgba(hex_val)
        
        return palette_dict  # Return the dict so the user can see the keys

    def list_palettes(self) -> List[str]:
        """List offline built-in palette names. 
        For 4000+ more, visit https://lospec.com/palette-list
        """
        return list(_OFFLINE_PALETTES.keys())

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
                hue_shift = (0.5 - t) * 0.07
                new_h = (h + hue_shift) % 1.0
                sat_curve = 1.0 + (0.5 - t) * 0.3
                new_s = min(1.0, max(0.0, s * sat_curve))
                lt = t * t * (3 - 2 * t)  # Smoothstep
                new_l = min(0.95, max(0.08, l * (0.35 + 1.1 * lt)))
                
            elif mode == "warm_cool":
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

from .canvas_base import BaseCanvas, hex2rgba
from .mixins.color import ColorMixin
from .mixins.geometry import GeometryMixin
from .mixins.render import RenderMixin
from .mixins.transform import TransformMixin
from .mixins.postprocess import PostprocessMixin
from .mixins.isometric import IsometricMixin

class Canvas(ColorMixin, GeometryMixin, RenderMixin, TransformMixin, PostprocessMixin, IsometricMixin, BaseCanvas):
    pass

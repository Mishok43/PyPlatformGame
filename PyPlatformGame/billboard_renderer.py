"""Module containing billboard render processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable

import esper
import glm

from .physics import aabb


@dataclass
class DrawOrderComponent:
    """Draw order component."""

    order: int

    def __init__(self, order: int):
        self.order = order


@dataclass
class TextureComponent:
    """Texture component for ECS."""

    tex_name: str
    face_right: bool

    def __init__(self, tex_name: str):
        """Initialize texture component."""
        self.tex_name = tex_name
        self.face_right = True


class RenderProcessor(esper.Processor):
    """Billboard render processor for ECS."""

    def __init__(self, callback: Callable):
        """Initialize billboard renderer."""
        self.callback = callback

    def process(self, *_):
        """Feed AABBs to the renderer with appropriate parameters."""
        for _, (box, tex, draw) in self.world.get_components(
                aabb.AABBComponent, TextureComponent, DrawOrderComponent):
            if tex.face_right:
                self.callback(tex.tex_name, box.pos, box.dim, draw.order)
            else:
                new_pos = box.pos + glm.vec2(box.dim.x, 0)
                new_dim = glm.vec2(-box.dim.x, box.dim.y)
                self.callback(tex.tex_name, new_pos, new_dim, draw.order)

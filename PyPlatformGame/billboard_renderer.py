"""Module containing billboard render processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable

import esper

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

    def __init__(self, tex_name: str):
        """Initialize texture component."""
        self.tex_name = tex_name


class RenderProcessor(esper.Processor):
    """Billboard render processor for ECS."""

    def __init__(self, callback: Callable):
        """Initialize billboard renderer."""
        self.callback = callback

    def process(self, *_):
        """Feed AABBs to the renderer with appropriate parameters."""
        for _, (box, tex, draw) in self.world.get_components(
                aabb.AABBComponent, TextureComponent, DrawOrderComponent):
            self.callback(tex.tex_name, box.pos, box.dim, draw.order)

"""Module containing debug render processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable

import esper

from .physics import aabb


@dataclass
class TextureComponent:
    """Texture component for ECS."""

    tex_name: str

    def __init__(self, tex_name: str):
        """Initialize texture component."""
        self.tex_name = tex_name


class RenderProcessor(esper.Processor):
    """Render processor for ECS."""

    def __init__(self, callback: Callable):
        """Initialize debug renderer."""
        self.callback = callback

    def process(self, *_):
        """Render AABB components in different colors with Pygame."""

        for _, (box, tex) in self.world.get_components(aabb.AABBComponent, TextureComponent):
            self.callback(tex.tex_name, box.pos, box.dim)

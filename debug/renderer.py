"""Module containing debug render processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable, Tuple

import esper
import pygame

from ..physics import aabb


@dataclass
class ColorComponent:
    """Color component for ECS."""

    color: Tuple[int, int, int]

    def __init__(self, color: Tuple[int, int, int]):
        """Initialize color component."""
        self.color = color


class RenderProcessor(esper.Processor):
    """Render processor for ECS."""

    def __init__(self, callback: Callable):
        """Initialize debug renderer."""
        self.callback = callback

    def process(self, *_):
        """Render AABB components in different colors with Pygame."""

        for _, (box, color) in self.world.get_components(aabb.AABBComponent, ColorComponent):
            surface = pygame.Surface(box.dim)
            surface.fill(color.color)
            rect = pygame.Rect(*box.pos, *box.dim)

            self.callback(box.pos, box.dim)

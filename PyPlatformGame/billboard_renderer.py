"""Module containing billboard render processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable
import math

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
    wobble_time: float
    wobble_amplitude: float
    wobble_acceleration: float

    def __init__(self, tex_name: str, wobble_amplitude = 0.0,
            wobble_acceleration = 0.0):
        """Initialize texture component."""
        self.tex_name = tex_name
        self.face_right = True
        self.wobble_time = 0.0
        self.wobble_amplitude = wobble_amplitude
        self.wobble_acceleration = wobble_acceleration


class RenderProcessor(esper.Processor):
    """Billboard render processor for ECS."""

    def __init__(self, callback: Callable):
        """Initialize billboard renderer."""
        self.callback = callback

    def process(self, *_):
        """Feed AABBs to the renderer with appropriate parameters."""
        for _, (box, tex, draw) in self.world.get_components(
                aabb.AABBComponent, TextureComponent, DrawOrderComponent):

            wobble = glm.vec2(0.0, tex.wobble_amplitude * abs(
                    math.sin(tex.wobble_acceleration * tex.wobble_time)))

            if tex.face_right:
                self.callback(tex.tex_name, box.pos + wobble, box.dim - wobble, draw.order)
            else:
                new_pos = box.pos + glm.vec2(box.dim.x, 0)
                new_dim = glm.vec2(-box.dim.x, box.dim.y)
                self.callback(tex.tex_name, new_pos + wobble, new_dim - wobble, draw.order)

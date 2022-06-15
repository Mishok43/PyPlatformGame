"""Module containing camera processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable

import esper
import glm

from .physics import aabb


CAMERA_OFFSET = -0.1


@dataclass
class FollowCameraComponent:
    """Follow camera component for ECS."""


class CameraProcessor(esper.Processor):
    """Camera processor for ECS."""

    def __init__(self, callback: Callable):
        """Initialize camera."""
        self.callback = callback

    def process(self, *_):
        """Process camera position and execute callback."""
        for _, (_, box) in self.world.get_components(FollowCameraComponent, aabb.AABBComponent):
            self.callback(box.pos + box.dim / 2 + glm.vec2(0.0, CAMERA_OFFSET))

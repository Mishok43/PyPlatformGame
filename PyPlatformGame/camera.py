"""Module containing camera processor for ECS and assosiated components."""


from dataclasses import dataclass
from typing import Callable

import esper

from .physics import aabb


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
            self.callback(box.pos + box.dim / 2)

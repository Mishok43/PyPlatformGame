"""Module containing velocity ECS component."""


from dataclasses import dataclass
from typing import Tuple

import glm


@dataclass
class VelocityComponent:
    """Velocity component for ECS."""

    direction: glm.vec2

    def __init__(self, direction: Tuple[float, float] | glm.vec2):
        """Initialize velocity component."""
        self.direction = glm.vec2(direction)

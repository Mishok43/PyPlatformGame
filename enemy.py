"""Module containing enemy logic for ECS."""


from dataclasses import dataclass
from typing import Tuple

import esper
import glm

from .physics import aabb


@dataclass
class TimerComponent:
    """Enemy timer component for ECS."""

    time: float
    is_set: bool

    def __init__(self):
        """Initialize timer component."""
        self.time = 0.0
        self.is_set = False


@dataclass
class SettingsComponent:
    """Enemy settings component for ECS."""

    direction: glm.vec2(0.0)
    mirror_time: float
    mirror_axis: glm.vec2(0.0)
    mirror_state: bool

    def __init__(self,
            direction: Tuple[float, float] | glm.vec2,
            mirror_time: float,
            mirror_axis: Tuple[float, float] | glm.vec2):
        """Initialize settings controller component."""
        self.direction = glm.vec2(direction)
        self.mirror_time = mirror_time
        self.mirror_axis = glm.vec2(mirror_axis)
        self.mirror_state = True


class ControllerProcessor(esper.Processor):
    """Enemy controller processor for ECS."""

    def process(self, dt: float, *_):
        """Process enemy logic."""
        for ent, (box, settings, timer) in self.world.get_components(
                aabb.AABBComponent, SettingsComponent, TimerComponent):

            if not timer.is_set:
                timer.time = settings.mirror_time
                timer.is_set = True
                self.world.add_component(ent, timer)
                continue

            if settings.mirror_state:
                box.pos += settings.direction * glm.vec2(dt)
            else:
                box.pos += settings.direction * -settings.mirror_axis * glm.vec2(dt)

            timer.time -= dt
            if timer.time < 0.0:
                timer.time = settings.mirror_time
                self.world.add_component(ent, timer)

                settings.mirror_state = not settings.mirror_state
                self.world.add_component(ent, settings)

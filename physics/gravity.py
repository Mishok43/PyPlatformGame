"""Module containing collision component and processor for ECS."""


from dataclasses import dataclass

import glm
import esper

from . import velocity


DT_COMPENSATOR = 20
MAX_MODIFIER = 3


@dataclass
class SusceptibleToGravityComponent:
    """Component for querying entities with passive collision in ECS."""

    force: float

    def __init__(self):
        """Initialize susceptible to gravity component."""
        self.force = 9.81


class GravityProcessor(esper.Processor):
    """Gravity processor for ECS."""

    def process(self, dt: float, *_):
        """Process gravity."""
        for ent, (grav, vel) in self.world.get_components(
                SusceptibleToGravityComponent, velocity.VelocityComponent):

            vel.direction += glm.vec2(0.0, grav.force) * DT_COMPENSATOR * dt
            vel.direction.y = min(vel.direction.y, grav.force * MAX_MODIFIER)
            self.world.add_component(ent, vel)

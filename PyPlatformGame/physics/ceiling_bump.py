"""Module containing ceiling bump processor for ECS."""


import esper

from . import velocity
from . import collision


class CeilingBumpProcessor(esper.Processor):
    """Ceiling bump processor for ECS."""

    def process(self, *_):
        """Process ceiling bumps."""
        for ent, (_, vel) in self.world.get_components(
                collision.CeilingBumpComponent, velocity.VelocityComponent):

            vel.direction.y = 0.0
            self.world.remove_component(ent, collision.CeilingBumpComponent)

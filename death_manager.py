"""Module containing entity death logic for ECS."""


from dataclasses import dataclass

import esper

from .physics import collision


@dataclass
class InvincibilityComponent:
    """Invincibility component for ECS."""


class DeathProcessor(esper.Processor):
    """Death processor for ECS."""

    def process(self, *_):
        """Kill entities marked for death."""
        for ent, _ in self.world.get_component(collision.MarkOfDeathComponent):
            if _ := self.world.try_component(ent, InvincibilityComponent):
                self.world.remove_component(ent, collision.MarkOfDeathComponent)
                continue

            self.world.delete_entity(ent)

"""Module containing entity death logic for ECS."""


from dataclasses import dataclass
from typing import Callable

import esper

from .physics import collision
from . import player

@dataclass
class InvincibilityComponent:
    """Invincibility component for ECS."""


class DeathProcessor(esper.Processor):
    """Death processor for ECS."""

    def __init__(self, player_death_callback: Callable,
                enemy_death_callback: Callable):
        """Set callbacks."""
        self.player_death_callback = player_death_callback
        self.enemy_death_callback = enemy_death_callback
    def process(self, *_):
        """Kill entities marked for death."""
        for ent, _ in self.world.get_component(collision.MarkOfDeathComponent):
            if _ := self.world.try_component(ent, InvincibilityComponent):
                self.world.remove_component(ent, collision.MarkOfDeathComponent)
                continue
            if _ := self.world.try_component(ent, player.StateComponent):
                self.player_death_callback()
            else:
                self.enemy_death_callback()
            self.world.delete_entity(ent)

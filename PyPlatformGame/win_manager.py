"""Module containing win condition logic for ECS."""


from typing import Callable

import esper

from . import enemy


class WinProcessor(esper.Processor):
    """Win condition processor for ECS."""
    def __init__(self, win_callback: Callable):
        self.win_callback = win_callback

    def process(self, *_):
        """Check if all enemies are dead."""
        if len(self.world.get_component(enemy.SettingsComponent)) <= 0:
            self.win_callback()

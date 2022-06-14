"""Module containing input components for ECS."""


from dataclasses import dataclass


@dataclass
class SusceptibleToInputComponent:
    """Component for querying entities susceptible to input in ECS."""


@dataclass
class InputComponent:
    """Input component for ECS."""

    move_direction: float
    do_jump: bool
    attack: float

    def __init__(self):
        """Initialize input component."""
        self.move_direction = 0.0
        self.do_jump = False
        self.attack = False

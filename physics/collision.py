"""Module containing collision component and processor for ECS."""


from dataclasses import dataclass
from typing import Tuple

import pygame
import glm
import esper

from . import aabb
from . import velocity


@dataclass
class PassiveCollisionComponent:
    """Component for querying entities with passive collision in ECS."""


@dataclass
class ActiveCollisionComponent:
    """Component for querying entities with active collision in ECS."""


@dataclass
class HurtComponent:
    """Component for querying if collision should hurt an entity in ECS."""


@dataclass
class MarkOfDeathComponent:
    """Component for marking hurt entities in ECS."""


@dataclass
class GroundedComponent:
    """Component for querying if entity is grounded in ECS."""


@dataclass
class CeilingBumpComponent:
    """Component for querying if ceiling bump has occured."""


@dataclass
class CollisionComponent:
    """Collision component for ECS."""

    time: float
    normal = glm.vec2

    def __init__(self, time: float, normal: Tuple[float, float] | glm.vec2):
        """Initialize collision component."""
        self.time = float(time)
        self.normal = glm.vec2(normal)


class CollisionProcessor(esper.Processor):
    """Collision processor for ECS."""

    def process(self, *_):
        """Process collisions."""
        active = self.world.get_component(ActiveCollisionComponent)
        for idx, (act_ent, _) in enumerate(active):
            act_aabb = self.world.component_for_entity(act_ent, aabb.AABBComponent)

            # Broad phase and swept AABB
            if act_vel := self.world.try_component(act_ent, velocity.VelocityComponent):

                for pas_ent, _ in self.world.get_component(PassiveCollisionComponent):
                    pas_aabb = self.world.component_for_entity(pas_ent, aabb.AABBComponent)

                    broad_box = aabb.broad_box(act_aabb, act_vel)

                    collided = aabb.check(broad_box, pas_aabb)
                    if collided:

                        col_time, col_normal = aabb.swept(act_aabb, pas_aabb, act_vel)
                        col = CollisionComponent(time=col_time, normal=col_normal)

                        if self.world.try_component(act_ent, CollisionComponent):
                            self.world.remove_component(act_ent, CollisionComponent)
                        self.world.add_component(act_ent, col)

            # Hurtboxes
            for pas_ent, _ in active[idx+1:]:
                pas_aabb = self.world.component_for_entity(pas_ent, aabb.AABBComponent)

                act_rect = pygame.Rect(*act_aabb.pos, *act_aabb.dim)
                pas_rect = pygame.Rect(*pas_aabb.pos, *pas_aabb.dim)

                if act_rect.colliderect(pas_rect):
                    if _ := self.world.try_component(pas_ent, HurtComponent):
                        self.world.add_component(act_ent, MarkOfDeathComponent())
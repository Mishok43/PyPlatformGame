"""Module containing player logic for ECS."""


from dataclasses import dataclass

import esper
import glm

from .physics import aabb
from .physics import velocity
from .physics import collision
from . import input_data
from .physics import gravity
from .debug import renderer as debug_renderer


PLAYER_SPEED = 500.0
JUMP_MULTIPLIER = 5
FALL_MULTIPLIER = 2


class PhysicsProcessor(esper.Processor):
    """Player physics processor for ECS."""

    def process(self, *_):
        """Process physics for player entities."""
        for ent, (box, vel) in self.world.get_components(
                aabb.AABBComponent, velocity.VelocityComponent):

            if col := self.world.try_component(ent, collision.CollisionComponent):
                box.pos += vel.direction * col.time

                # Deflection
                # if abs(col.normal.x) > 0.0001:
                #     vel.direction.x *= -1
                # if abs(col.normal.y) > 0.0001:
                #     vel.direction.y *= -1

                # box.pos += vel.direction * (1.0 - col.time)

                # Slide
                if col.time < 1.0:
                    inv_normal = glm.vec2(col.normal.y, col.normal.x)
                    dot_prod = glm.dot(vel.direction, inv_normal) * (1.0 - col.time)
                    box.pos += inv_normal * dot_prod

                self.world.remove_component(ent, collision.CollisionComponent)

                if abs(col.normal.x) < 0.0001:
                    if col.normal.y < -0.0001:
                        self.world.add_component(ent, collision.GroundedComponent())
                    elif col.normal.y > 0.0001:
                        self.world.add_component(ent, collision.CeilingBumpComponent())

            else:
                box.pos += vel.direction


@dataclass
class DisjointedParamsComponent:
    """Parameters for disjointed hurtbox component for ECS."""

    time: float
    host: int

    def __init__(self, time: float, host: int):
        """Initialize Parameters for disjointed hurtbox component."""
        self.time = time
        self.host = host


class DisjointedController(esper.Processor):
    """Disjointed hurtbox processor for ECS."""

    def process(self, dt: float, *_):
        """Process disjointed hurtboxes."""
        for ent, (box, params) in self.world.get_components(
                aabb.AABBComponent, DisjointedParamsComponent):

            if not self.world.entity_exists(params.host):
                self.world.delete_entity(ent)
                continue

            host_box = self.world.component_for_entity(params.host, aabb.AABBComponent)
            state = self.world.component_for_entity(params.host, StateComponent)

            if state.face_right:
                box.pos = glm.vec2(aabb.extent(host_box).x + 1.0, aabb.top(host_box))
            else:
                box.pos = glm.vec2(aabb.left(host_box) - box.dim.x - 1.0, aabb.top(host_box))
            self.world.add_component(ent, box)

            params.time -= dt
            if params.time < 0.0:
                self.world.delete_entity(ent)
                state.has_disjointed = False
                self.world.add_component(params.host, state)
            else:
                self.world.add_component(ent, params)


@dataclass
class StateComponent:
    """Player state component for ECS."""

    face_right: bool
    has_disjointed: bool

    def __init__(self):
        """Initialize player state component."""
        self.face_right = True
        self.has_disjointed = False


class InputProcessor(esper.Processor):
    """Player input processor for ECS."""

    def __init__(self, input_entity: int):
        """Initialize player input processor."""
        self.input_entity = input_entity
        self.jump_held = False

    def process(self, dt: float, *_):
        """Process player input."""
        input_component = self.world.component_for_entity(
                self.input_entity, input_data.InputComponent)

        for ent, (state, _, vel, grav) in self.world.get_components(
                StateComponent,
                input_data.SusceptibleToInputComponent,
                velocity.VelocityComponent,
                gravity.SusceptibleToGravityComponent):

            vel_h = input_component.move_direction * PLAYER_SPEED * dt

            if abs(vel_h) > 0.0001:
                state.face_right = vel_h > 0.0
                self.world.add_component(ent, state)

            vel_v = vel.direction.y

            if not self.jump_held and input_component.do_jump and \
                    (_ := self.world.try_component(ent, collision.GroundedComponent)):

                vel_v = -JUMP_MULTIPLIER * grav.force
                self.jump_held = True
                self.world.remove_component(ent, collision.GroundedComponent)

            elif self.jump_held and not input_component.do_jump:
                if vel_v < 0.0:
                    self.world.add_component(ent, collision.CeilingBumpComponent())
                self.jump_held = False

            vel_new = velocity.VelocityComponent(direction=glm.vec2(vel_h, vel_v))
            self.world.add_component(ent, vel_new)

            if input_component.attack and not state.has_disjointed:
                state.has_disjointed = True
                self.world.add_component(ent, state)

                self.world.create_entity(aabb.AABBComponent(pos=(0, 0), dim=(30, 30)),
                        debug_renderer.ColorComponent(color=(255, 255, 0)),
                        collision.ActiveCollisionComponent(),
                        collision.HurtComponent(),
                        DisjointedParamsComponent(time=0.1, host=ent))

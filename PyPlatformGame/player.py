"""Module containing player logic for ECS."""


from dataclasses import dataclass
from typing import Callable

import esper
import glm

from .audiomanager import AudioManager
from .physics import aabb
from .physics import velocity
from .physics import collision
from . import input_data
from .physics import gravity
from . import billboard_renderer as billy


PLAYER_SPEED = 0.625
JUMP_MULTIPLIER = 0.00833
ATTACK_COOLDOWN = 0.6
ATTACK_ACTIVE_TIME = 0.3


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
                box.pos = glm.vec2(aabb.extent(host_box).x, aabb.top(host_box))
            else:
                box.pos = glm.vec2(aabb.left(host_box) - box.dim.x, aabb.top(host_box))

            params.time -= dt
            if params.time < 0.0:
                self.world.delete_entity(ent)
                state.has_disjointed = False


@dataclass
class StateComponent:
    """Player state component for ECS."""

    face_right: bool
    has_disjointed: bool
    attack_held: bool
    attack_timer: float

    def __init__(self):
        """Initialize player state component."""
        self.face_right = True
        self.has_disjointed = False
        self.attack_held = False
        self.attack_timer = -1.0


class InputProcessor(esper.Processor):
    """Player input processor for ECS."""

    def __init__(self, input_entity: int, attack_sound_callback: Callable):
        """Initialize player input processor."""
        self.input_entity = input_entity
        self.jump_held = False
        self.attack_sound_callback = attack_sound_callback

    def process(self, dt: float, *_):
        """Process player input."""
        input_component = self.world.component_for_entity(
                self.input_entity, input_data.InputComponent)

        for ent, (state, _, vel, grav, tex) in self.world.get_components(
                StateComponent,
                input_data.SusceptibleToInputComponent,
                velocity.VelocityComponent,
                gravity.SusceptibleToGravityComponent,
                billy.TextureComponent):

            vel_h = input_component.move_direction * PLAYER_SPEED * dt

            if abs(vel_h) > 0.0001:
                state.face_right = vel_h > 0.0
                tex.wobble_time += dt
                tex.face_right = state.face_right
            else:
                tex.wobble_time = 0.0

            vel_v = vel.direction.y

            if not self.jump_held and input_component.do_jump and \
                    self.world.has_component(ent, collision.GroundedComponent):

                vel_v = -JUMP_MULTIPLIER * grav.force
                self.jump_held = True
                self.world.remove_component(ent, collision.GroundedComponent)

            elif self.jump_held and not input_component.do_jump:
                if vel_v < 0.0:
                    self.world.add_component(ent, collision.CeilingBumpComponent())
                self.jump_held = False

            if not self.world.has_component(ent, collision.GroundedComponent):
                tex.wobble_time = 0.0

            vel_new = velocity.VelocityComponent(direction=glm.vec2(vel_h, vel_v))
            self.world.add_component(ent, vel_new)

            state.attack_timer = max(state.attack_timer - dt, -1.0)

            if not input_component.attack:
                state.attack_held = False
            elif not state.has_disjointed and not state.attack_held and state.attack_timer < 0.0:
                state.has_disjointed = True
                state.attack_held = True
                state.attack_timer = ATTACK_COOLDOWN

                self.world.create_entity(aabb.AABBComponent(pos=(0, 0), dim=(0.07, 0.07)),
                        billy.TextureComponent(tex_name="cross.png"),
                        billy.DrawOrderComponent(order=3),
                        collision.ActiveCollisionComponent(),
                        collision.HurtComponent(),
                        DisjointedParamsComponent(time=ATTACK_ACTIVE_TIME, host=ent))

                self.attack_sound_callback()

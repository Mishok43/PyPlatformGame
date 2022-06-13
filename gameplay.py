"""Game initialization and game loop."""


import pygame
import esper

from .physics import aabb
from .physics import ceiling_bump
from .physics import collision
from .physics import velocity
from .physics import gravity
from . import billboard_renderer as billy
from . import input_data
from . import player
from . import enemy
from . import death_manager
from .app_state import app_state

# Setup
def init_physics(billboard_callback):
    """Physics initialization."""
    world = esper.World()

    world.add_processor(billy.RenderProcessor(billboard_callback))
    world.add_processor(player.PhysicsProcessor(), priority=2)
    world.add_processor(death_manager.DeathProcessor(), priority=3)
    world.add_processor(collision.CollisionProcessor(), priority=4)
    world.add_processor(ceiling_bump.CeilingBumpProcessor(), priority=5)
    world.add_processor(gravity.GravityProcessor(), priority=6)
    world.add_processor(enemy.ControllerProcessor(), priority=7)
    world.add_processor(player.DisjointedController(), priority=8)

    input_entity = world.create_entity(input_data.InputComponent())
    world.add_processor(player.InputProcessor(input_entity), priority=9)

    # Player
    world.create_entity(aabb.AABBComponent(pos=(200, 300), dim=(50, 50)),
            billy.TextureComponent(tex_name="test.png"),
            collision.ActiveCollisionComponent(),
            velocity.VelocityComponent(direction=(0, 0)),
            gravity.SusceptibleToGravityComponent(),
            input_data.SusceptibleToInputComponent(),
            player.StateComponent())

    # Enemies
    world.create_entity(aabb.AABBComponent(pos=(500, 300), dim=(50, 100)),
            billy.TextureComponent(tex_name="test.png"),
            collision.ActiveCollisionComponent(),
            collision.HurtComponent(),
            enemy.TimerComponent(),
            enemy.SettingsComponent(direction=(100, 0), mirror_time=2.0, mirror_axis=(1,0)))

    world.create_entity(aabb.AABBComponent(pos=(50, 50), dim=(144, 100)),
            billy.TextureComponent(tex_name="test.png"),
            collision.ActiveCollisionComponent(),
            collision.HurtComponent(),
            enemy.TimerComponent(),
            enemy.SettingsComponent(direction=(0, 150), mirror_time=1.0, mirror_axis=(0,1)))

    # Platform
    world.create_entity(
            aabb.AABBComponent(pos=(400, app_state().screen_res[1]-200),
            dim=(app_state().screen_res[0], 20)),
            billy.TextureComponent(tex_name="test.png"),
            collision.PassiveCollisionComponent())

    # Borders
    world.create_entity(
            aabb.AABBComponent(pos=(0, app_state().screen_res[1]-20),
            dim=(app_state().screen_res[0], 20)),
            billy.TextureComponent(tex_name="test.png"),
            collision.PassiveCollisionComponent())

    return (world, input_entity)

def process_input(world, input_entity, pressed_keys):
    """Process input from keyboard."""
    input_component = input_data.InputComponent()

    if pressed_keys[pygame.K_a]:
        input_component.move_direction = -1.0

    if pressed_keys[pygame.K_d]:
        input_component.move_direction = 1.0

    if pressed_keys[pygame.K_SPACE]:
        input_component.do_jump = True

    if pressed_keys[pygame.K_p]:
        input_component.attack = True

    world.add_component(input_entity, input_component)

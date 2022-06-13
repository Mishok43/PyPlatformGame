"""Game initialization and game loop."""


import pygame
import esper

from .physics import aabb
from .physics import ceiling_bump
from .physics import collision
from .physics import velocity
from .physics import gravity
from .debug import renderer as debug_renderer
from . import input_data
from . import player
from . import enemy
from . import death_manager


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_NAME = "PyPlatformGame"
FPS=60

# Setup
def main():
    """Program entry point."""
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption(GAME_NAME)

    world = esper.World()

    world.add_processor(debug_renderer.RenderProcessor(screen))
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
            debug_renderer.ColorComponent(color=(255, 0, 0)),
            collision.ActiveCollisionComponent(),
            velocity.VelocityComponent(direction=(0, 0)),
            gravity.SusceptibleToGravityComponent(),
            input_data.SusceptibleToInputComponent(),
            player.StateComponent())

    # Enemies
    world.create_entity(aabb.AABBComponent(pos=(500, 300), dim=(50, 100)),
            debug_renderer.ColorComponent(color=(0, 0, 255)),
            collision.ActiveCollisionComponent(),
            collision.HurtComponent(),
            enemy.TimerComponent(),
            enemy.SettingsComponent(direction=(100, 0), mirror_time=2.0, mirror_axis=(1,0)))

    world.create_entity(aabb.AABBComponent(pos=(50, 50), dim=(144, 100)),
            debug_renderer.ColorComponent(color=(0, 0, 255)),
            collision.ActiveCollisionComponent(),
            collision.HurtComponent(),
            enemy.TimerComponent(),
            enemy.SettingsComponent(direction=(0, 150), mirror_time=1.0, mirror_axis=(0,1)))

    # Platform
    world.create_entity(aabb.AABBComponent(pos=(400, SCREEN_HEIGHT-200), dim=(SCREEN_WIDTH, 20)),
            debug_renderer.ColorComponent(color=(0, 255, 0)),
            collision.PassiveCollisionComponent())

    # Borders
    world.create_entity(aabb.AABBComponent(pos=(0, SCREEN_HEIGHT-20), dim=(SCREEN_WIDTH, 20)),
            debug_renderer.ColorComponent(color=(0, 255, 0)),
            collision.PassiveCollisionComponent())

    # Game loop
    running = True
    clock = pygame.time.Clock()
    while running:
        delta_time = clock.tick(FPS) / 1000

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle Input
        input_component = input_data.InputComponent()
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_a]:
            input_component.move_direction = -1.0

        if pressed_keys[pygame.K_d]:
            input_component.move_direction = 1.0

        if pressed_keys[pygame.K_SPACE]:
            input_component.do_jump = True

        if pressed_keys[pygame.K_p]:
            input_component.attack = True

        world.add_component(input_entity, input_component)

        # Game logic and Render
        world.process(delta_time)

        pygame.display.flip()

    pygame.quit()

main()

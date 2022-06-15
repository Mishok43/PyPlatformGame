"""Module for gameplay code (level load, physics, controls)."""
from dataclasses import dataclass
from typing import Callable
import json
import esper
import pygame as pg

from .physics import aabb
from .physics import ceiling_bump
from .physics import collision
from .physics import velocity
from .physics import gravity
from . import billboard_renderer as billy
from . import input_data
from . import player
from . import enemy
from . import camera
from . import death_manager
from . import win_manager

@dataclass
class GameplayCallbacks:
    """Callbacks for various gameplay events."""

    win_callback: Callable
    camera_callback: Callable
    billboard_render: Callable
    player_death: Callable
    enemy_death: Callable

class Gameplay:
    """Level management, physics and player controls."""

    def __init__(self, level_filename: str, clb: GameplayCallbacks):
        """Load description of level from JSON file."""
        self.world = esper.World()
        self.world.add_processor(win_manager.WinProcessor(clb.win_callback), priority=1)
        self.world.add_processor(camera.CameraProcessor(clb.camera_callback), priority=2)
        self.world.add_processor(billy.RenderProcessor(clb.billboard_render), priority=3)
        self.world.add_processor(player.PhysicsProcessor(), priority=4)
        self.world.add_processor(death_manager.DeathProcessor(clb.player_death,
                                                clb.enemy_death), priority=5)
        self.world.add_processor(collision.CollisionProcessor(), priority=6)
        self.world.add_processor(ceiling_bump.CeilingBumpProcessor(), priority=7)
        self.world.add_processor(gravity.GravityProcessor(), priority=8)
        self.world.add_processor(enemy.ControllerProcessor(), priority=9)
        self.world.add_processor(player.DisjointedController(), priority=10)
        self.input_entity = self.world.create_entity(input_data.InputComponent())
        self.world.add_processor(player.InputProcessor(self.input_entity), priority=11)

        with open(level_filename, encoding='utf-8') as file:
            level = json.load(file)

            player_descr = level["player"]
            player_wobble = player_descr["wobble"]
            self.world.create_entity(aabb.AABBComponent(
                        pos=player_descr["pos"], dim=player_descr["dim"]),
                    billy.TextureComponent(tex_name=player_descr["texture"],
                        wobble_amplitude=player_wobble["amplitude"],
                        wobble_acceleration=player_wobble["acceleration"]),
                    billy.DrawOrderComponent(order=2),
                    collision.ActiveCollisionComponent(),
                    velocity.VelocityComponent(direction=(0, 0)),
                    gravity.SusceptibleToGravityComponent(),
                    input_data.SusceptibleToInputComponent(),
                    player.StateComponent(),
                    camera.FollowCameraComponent())

            for enemy_descr in level["enemies"]:
                motion = enemy_descr["motion"]
                enemy_wobble = enemy_descr["wobble"]
                self.world.create_entity(
                    aabb.AABBComponent(pos=enemy_descr["pos"], dim=enemy_descr["dim"]),
                    billy.TextureComponent(tex_name=enemy_descr["texture"],
                        wobble_amplitude=enemy_wobble["amplitude"],
                        wobble_acceleration=enemy_wobble["acceleration"]),
                    billy.DrawOrderComponent(order=1),
                    collision.ActiveCollisionComponent(),
                    collision.HurtComponent(),
                    enemy.TimerComponent(),
                    enemy.SettingsComponent(
                        direction=motion["direction"],
                        mirror_time=motion["mirror_time"],
                        mirror_axis=motion["mirror_axis"]))

            for platform in level["platforms"]:
                self.world.create_entity(
                    aabb.AABBComponent(pos=platform["pos"],
                        dim=platform["dim"]),
                    billy.TextureComponent(tex_name=platform["texture"]),
                    billy.DrawOrderComponent(order=0),
                    collision.PassiveCollisionComponent())

            for death_box in level["death_boxes"]:
                self.world.create_entity(
                    aabb.AABBComponent(pos=death_box["pos"],
                        dim=death_box["dim"]),
                    collision.ActiveCollisionComponent(),
                    collision.HurtComponent())

    def process_input(self):
        """Process inputs and pass to ECS."""
        input_component = input_data.InputComponent()
        pressed_keys = pg.key.get_pressed()
        if pressed_keys[pg.K_a]:
            input_component.move_direction = -1.0
        if pressed_keys[pg.K_d]:
            input_component.move_direction = 1.0
        if pressed_keys[pg.K_SPACE]:
            input_component.do_jump = True
        if pressed_keys[pg.K_p]:
            input_component.attack = True
        self.world.add_component(self.input_entity, input_component)
    def update(self, delta_time):
        """Update for all ECS systems."""
        self.world.process(delta_time)

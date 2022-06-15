"""Module with implementation of main game loop and additional data."""
from dataclasses import dataclass
import gettext
from math import sin, cos
import os
from typing import Tuple
import pygame as pg
import glm
from .app_state import app_state, init_app_state, delete_app_state
from .ui_descr import menu_ui, pause_ui, game_ui, results_ui, UI
from .scene import Scene, Camera
from .renderer import draw
from .gameplay import Gameplay, GameplayCallbacks
from .audiomanager import AudioManager


FPS: int = 60
MENU: int = 1
GAME: int = 2
PAUSE: int = 3
RESULTS: int = 4
ROTATION_SPEED: float = 0.3
VERTICAL_SPEED: float = 0.5
ROTATION_SCALE: float = 1
VERTICAL_SCALE: float = 10
CAMERA_LIMIT_X: float = 0.7
CAMERA_LIMIT_Y: float = 0.5

@dataclass
class GameState:
    """Storage for all non-render state of game."""

    cur_state: int = MENU
    prev_state: int = None
    killed_enemy_count: int = 0
    won: bool = False
    should_quit: bool = False

    click_sound_handle: int = None
    kill_sound_handle: int = None
    die_sound_handle: int = None
    attack_sound_handle: int = None

    scene: Scene = None
    gameplay: Gameplay = None
    interface: UI = None

    screen_x: float = 0
    screen_y: float = 0

G_STATE = GameState()

def sound_callback(loudness: float):
    """Set volume of sound."""
    AudioManager().set_sounds_volume(loudness)

def music_callback(loudness: float):
    """Set volume of music."""
    AudioManager().set_background_volume(loudness)

def billboard_render(tex: str, pos: glm.vec2, size: glm.vec2, order: int = 0) -> None:
    """Add billboard to render list."""
    h_w = app_state().screen_res[1] / app_state().screen_res[0]
    G_STATE.scene.add_bilboard(tex,
            (
                (pos[0] + 0.5 * size[0] - G_STATE.screen_x) * h_w,
                pos[1] + 0.5 * size[1] - G_STATE.screen_y
            ),
            (size[0] * h_w, size[1]),
            order)

def attack_sound_callback():
    """Play attack sound."""
    if G_STATE.attack_sound_handle != -1:
        AudioManager().play_sound(G_STATE.attack_sound_handle)

def win_callback() -> None:
    """Prepare to showq won game screen."""
    G_STATE.won = True
    G_STATE.cur_state = RESULTS

def camera_callback(pos: Tuple[int, int]) -> None:
    """Update camera, following the player."""
    screen_size = (app_state().screen_res[0] / app_state().screen_res[1], 1)
    if pos[0] < G_STATE.screen_x + CAMERA_LIMIT_X:
        G_STATE.screen_x = pos[0] - CAMERA_LIMIT_X
    elif pos[0] > G_STATE.screen_x + screen_size[0] - CAMERA_LIMIT_X:
        G_STATE.screen_x = pos[0] - screen_size[0] + CAMERA_LIMIT_X
    if pos[1] < G_STATE.screen_y + CAMERA_LIMIT_Y:
        G_STATE.screen_y = pos[1] - CAMERA_LIMIT_Y
    elif pos[1] > G_STATE.screen_y + screen_size[1] - CAMERA_LIMIT_Y:
        G_STATE.screen_y = pos[1] - screen_size[1] + CAMERA_LIMIT_Y

def enemy_death_callback() -> None:
    """Inform enemy death."""
    if G_STATE.click_sound_handle != -1:
        AudioManager().play_sound(G_STATE.kill_sound_handle)
    G_STATE.killed_enemy_count += 1

def player_death_callback() -> None:
    """Inform player death and prepare to show lost game screen."""
    if G_STATE.click_sound_handle != -1:
        AudioManager().play_sound(G_STATE.die_sound_handle)
    G_STATE.won = False
    G_STATE.cur_state = RESULTS

def exit_callback() -> None:
    """Prepare to exit an app."""
    if G_STATE.click_sound_handle != -1:
        AudioManager().play_sound(G_STATE.click_sound_handle)
    G_STATE.should_quit = True

def play_callback() -> None:
    """Start or continue the game."""
    if G_STATE.click_sound_handle != -1:
        AudioManager().play_sound(G_STATE.click_sound_handle)
    G_STATE.cur_state = GAME

def menu_callback() -> None:
    """Return to main menu."""
    if G_STATE.click_sound_handle != -1:
        AudioManager().play_sound(G_STATE.click_sound_handle)
    G_STATE.killed_enemy_count = 0
    G_STATE.cur_state = MENU

def restart_callback() -> None:
    """Restart the game."""
    G_STATE.killed_enemy_count = 0
    G_STATE.cur_state = GAME

def lang_callback_ru() -> None:
    """Set RU language for game."""
    G_STATE.prev_state = None
    base_dir = os.path.dirname(__file__)
    transl = gettext.translation('PyPlatformGame', base_dir, languages=['ru'])
    transl.install()

def lang_callback_en() -> None:
    """Set EN language for game."""
    G_STATE.prev_state = None
    base_dir = os.path.dirname(__file__)
    transl = gettext.translation('PyPlatformGame', base_dir, languages=['en'])
    transl.install()

def process_state(base_dir: str) -> None:
    """Update game state tracking and interface layout."""
    if G_STATE.cur_state != G_STATE.prev_state:
        if G_STATE.cur_state == MENU:
            G_STATE.interface = menu_ui(
                    (play_callback, exit_callback, music_callback, sound_callback),
                    (AudioManager().get_background_volume(),
                    AudioManager().get_sounds_volume()),
                    (lang_callback_ru, lang_callback_en))
        elif G_STATE.cur_state == PAUSE:
            G_STATE.interface = pause_ui(play_callback, menu_callback,
                                        music_callback, sound_callback,
                                        (AudioManager().get_background_volume(),
                                        AudioManager().get_sounds_volume()))
        elif G_STATE.cur_state == GAME:
            G_STATE.interface = game_ui()
            if G_STATE.prev_state != PAUSE:
                G_STATE.gameplay = Gameplay(os.path.join(base_dir, 'assets', 'level.json'),
                    GameplayCallbacks(attack_sound_callback, win_callback, camera_callback,
                        billboard_render, player_death_callback, enemy_death_callback))
        elif G_STATE.cur_state == RESULTS:
            G_STATE.interface = results_ui(restart_callback, menu_callback,
                                        G_STATE.killed_enemy_count, G_STATE.won)
        G_STATE.prev_state = G_STATE.cur_state

def update_gameplay(delta_time: str, base_dir: str) -> None:
    """Call gameplay update or reinit it."""
    if G_STATE.cur_state == GAME and G_STATE.prev_state != PAUSE and G_STATE.prev_state != GAME:
        G_STATE.gameplay = Gameplay(os.path.join(base_dir, 'assets', 'level.json'),
            GameplayCallbacks(attack_sound_callback, win_callback, camera_callback,
                billboard_render, player_death_callback, enemy_death_callback))
    if G_STATE.cur_state == PAUSE:
        G_STATE.gameplay.update(0)
    elif G_STATE.cur_state == GAME:
        G_STATE.gameplay.update(delta_time)
def input_logic() -> None:
    """Process inputs."""
    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE] and G_STATE.cur_state == GAME:
        G_STATE.cur_state = PAUSE
    for slider in G_STATE.interface.sliders:
        slider.process_input()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            G_STATE.should_quit = True
        else:
            for button in G_STATE.interface.buttons:
                button.process_event(event)
    G_STATE.gameplay.process_input()


def main() -> None:
    """Game initialization and main loop."""
    pg.init()
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 1)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
    pg.display.set_mode((1280, 720), pg.OPENGL|pg.DOUBLEBUF)

    base_dir = os.path.dirname(__file__)

    init_app_state((1280, 720),
                os.path.join(base_dir, 'shaders'),
                os.path.join(base_dir, 'assets', 'textures'),
                os.path.join(base_dir, 'assets', 'meshes'))
    G_STATE.gameplay = Gameplay(
        os.path.join(base_dir, 'assets', 'level.json'),
        GameplayCallbacks(
            attack_sound_callback, win_callback, camera_callback, billboard_render,
            player_death_callback, enemy_death_callback)
    )
    G_STATE.scene = Scene(os.path.join(base_dir, 'assets', 'scene.json'))
    lang_callback_en()

    audiomanager = AudioManager()
    sound_path = os.path.join(base_dir, 'assets', 'sounds')
    audiomanager.init_sounds(sound_path, sound_path)
    audiomanager.play_background_music("soundtrack.mp3")
    G_STATE.click_sound_handle = AudioManager().get_sound_handle("click_button.wav")
    G_STATE.die_sound_handle = AudioManager().get_sound_handle("die.wav")
    G_STATE.kill_sound_handle = AudioManager().get_sound_handle("kill.wav")
    G_STATE.attack_sound_handle = AudioManager().get_sound_handle("attack.wav")

    time = 0
    clock = pg.time.Clock()

    while True:
        if G_STATE.cur_state == MENU:
            pos = glm.vec3(
                    sin(time * ROTATION_SPEED)*150,
                    30.0 + sin(time * VERTICAL_SPEED) * 20,
                    cos(time * ROTATION_SPEED)*150)
            direction = glm.normalize(-pos)
        else:
            pos = glm.vec3(
                sin(G_STATE.screen_x * ROTATION_SCALE)*150,
                30.0 + max(0, min(20, G_STATE.screen_y * VERTICAL_SCALE)),
                cos(G_STATE.screen_x * ROTATION_SCALE)*150)
            direction = glm.normalize(-pos)
        process_state(base_dir)
        delta_time = clock.tick(FPS) / 1000
        time += delta_time
        G_STATE.scene.before_render()
        input_logic()
        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            G_STATE.scene = Scene(os.path.join(base_dir, 'assets', 'scene.json'))
        update_gameplay(delta_time, base_dir)
        if G_STATE.should_quit:
            break
        draw(G_STATE.scene, G_STATE.interface, Camera(pos, direction))
        pg.display.flip()

    G_STATE.interface = None
    delete_app_state()
    pg.quit()

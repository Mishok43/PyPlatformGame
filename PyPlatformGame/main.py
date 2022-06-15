import glm
from math import sin, cos
import gettext
import os
from .app_state import app_state, init_app_state, delete_app_state
from .render.shaders import ShaderManager
from .ui_descr import menu_ui, pause_ui, game_ui, results_ui
from .scene import Scene, Camera
from .renderer import draw
import pygame as pg
from .gameplay import Gameplay, GameplayCallbacks
from .audiomanager import AudioManager

base_dir = None
click_sound_handle = None
kill_sound_handle = None
die_sound_handle = None
killed_enemy_count = 0
MENU = 1
GAME = 2
PAUSE = 3
RESULTS = 4
cur_state = MENU
prev_state = None
should_stop = False
scene = None
gameplay = None
interface = None
cur_screen = [0, 0]

def sound_callback(l: float):
    AudioManager().set_sounds_volume(l)

def music_callback(l: float):
    AudioManager().set_background_volume(l)

def billboard_render(tex, pos, size, order = 0):
    h_w = app_state().screen_res[1] / app_state().screen_res[0]
    scene.add_bilboard(tex,
            (
                (pos[0] + 0.5 * size[0] - cur_screen[0]) * h_w,
                pos[1] + 0.5 * size[1] - cur_screen[1]
            ),
            (size[0] * h_w, size[1]),
            order)

def camera_callback(pos):
    global cur_screen
    CAMERA_MOVEMENT_THR = (0.7, 0.5)
    screen_size = (app_state().screen_res[0] / app_state().screen_res[1], 1)
    for dim in range(2):
        if pos[dim] < cur_screen[dim] + CAMERA_MOVEMENT_THR[dim]:
            cur_screen[dim] = pos[dim] - CAMERA_MOVEMENT_THR[dim]
        elif pos[dim] > cur_screen[dim] + screen_size[dim] - CAMERA_MOVEMENT_THR[dim]:
            cur_screen[dim] = pos[dim] - screen_size[dim] + CAMERA_MOVEMENT_THR[dim]

def enemy_death_callback():
    if click_sound_handle != -1:
        AudioManager().play_sound(kill_sound_handle)

    global killed_enemy_count
    killed_enemy_count += 1

def player_death_callback():
    if click_sound_handle != -1:
        AudioManager().play_sound(die_sound_handle)

    global cur_state
    cur_state = RESULTS

def exit_callback():
    if click_sound_handle != -1:
        AudioManager().play_sound(click_sound_handle)

    global should_stop
    should_stop = True

def play_callback():
    if click_sound_handle != -1:
        AudioManager().play_sound(click_sound_handle)

    global cur_state
    cur_state = GAME

def menu_callback():
    if click_sound_handle != -1:
        AudioManager().play_sound(click_sound_handle)
        
    global cur_state
    global killed_enemy_count
    global gameplay
    killed_enemy_count = 0
    cur_state = MENU
    gameplay = Gameplay(os.path.join(base_dir, 'assets', 'level.json'),
            GameplayCallbacks(camera_callback, billboard_render, player_death_callback, enemy_death_callback))

def restart_callback():
    global cur_state
    global killed_enemy_count
    global gameplay
    killed_enemy_count = 0
    cur_state = GAME
    gameplay = Gameplay(os.path.join(base_dir, 'assets', 'level.json'),
            GameplayCallbacks(camera_callback, billboard_render, player_death_callback, enemy_death_callback))

def lang_callback_ru():
    global prev_state
    prev_state = None
    base_dir = os.path.dirname(__file__)
    t = gettext.translation('PyPlatformGame', base_dir, languages=['ru'])
    t.install()

def lang_callback_en():
    global prev_state
    prev_state = None
    base_dir = os.path.dirname(__file__)
    t = gettext.translation('PyPlatformGame', base_dir, languages=['en'])
    t.install()

lang_callback_en()

def process_keyboard():
    global cur_state
    global scene
    global gameplay
    keys = pg.key.get_pressed()
    if keys[pg.K_r]:
        app_state().shader_manager = ShaderManager(os.path.join(base_dir, 'shaders'))
        scene = Scene(os.path.join(base_dir, 'assets', 'scene.json'))
        gameplay = Gameplay(os.path.join(base_dir, 'assets', 'level.json'),
            GameplayCallbacks(camera_callback, billboard_render, player_death_callback, enemy_death_callback))
    elif keys[pg.K_ESCAPE]:
        cur_state = PAUSE

def logic():
    global should_stop
    if cur_state == GAME:
        process_keyboard()
    for s in interface.sliders:
        s.process_input()
    for e in pg.event.get():
        if e.type == pg.QUIT:
            should_stop = True
        else:
            for b in interface.buttons:
                b.process_event(e)

def main():
    global scene
    global interface
    global gameplay
    global base_dir
    global click_sound_handle
    global kill_sound_handle
    global die_sound_handle
    global cur_state
    global prev_state
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
    gameplay = Gameplay(
        os.path.join(base_dir, 'assets', 'level.json'),
        GameplayCallbacks(
            camera_callback, billboard_render, player_death_callback, enemy_death_callback)
    )
    scene = Scene(os.path.join(base_dir, 'assets', 'scene.json'))
    time = 0
    ROTATION_SPEED = 0.3
    VERTICAL_SPEED = 0.5
    clock = pg.time.Clock()
    FPS = 60

    audiomanager = AudioManager()
    sound_path = os.path.join(base_dir, 'assets', 'sounds')
    audiomanager.init_sounds(sound_path, sound_path)
    audiomanager.play_background_music("soundtrack.mp3")
    click_sound_handle = AudioManager().get_sound_handle("click_button.wav")
    die_sound_handle = AudioManager().get_sound_handle("die.wav")
    kill_sound_handle = AudioManager().get_sound_handle("kill.wav")
    while True:
        pos = glm.vec3(sin(time * ROTATION_SPEED)*150, 30.0 + sin(time * VERTICAL_SPEED) * 20, cos(time * ROTATION_SPEED)*150)
        dir = glm.normalize(-pos)
        if cur_state != prev_state:
            if cur_state == MENU:
                interface = menu_ui(play_callback, exit_callback, music_callback, sound_callback, (AudioManager().get_background_volume(), AudioManager().get_sounds_volume()), (lang_callback_ru, lang_callback_en))
            elif cur_state == PAUSE:
                interface = pause_ui(play_callback, menu_callback, music_callback, sound_callback, (AudioManager().get_background_volume(), AudioManager().get_sounds_volume()))
            elif cur_state == GAME:
                interface = game_ui()
            elif cur_state == RESULTS:
                interface = results_ui(restart_callback, menu_callback, killed_enemy_count)
            prev_state = cur_state
        delta_time = clock.tick(FPS) / 1000
        time += delta_time
        scene.before_render()
        logic()
        gameplay.process_input()
        if cur_state == PAUSE:
            gameplay.update(0)
        elif cur_state == GAME:
            gameplay.update(delta_time)
        if should_stop:
            break
        draw(scene, interface, Camera(pos, dir))
        pg.display.flip()
    interface = None
    delete_app_state()
    pg.quit()

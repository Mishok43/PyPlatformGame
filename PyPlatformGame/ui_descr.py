"""Descriptions for all ui screens in game."""
from dataclasses import dataclass
from typing import Callable, List, Tuple
import pygame as pg
from .app_state import app_state
from .gui import ButtonDescr, SliderDescr, Button, Slider, TextRect, BaseUIElem

@dataclass
class UI:
    """Storage for all UI elements."""

    buttons: List[Button]
    sliders: List[Slider]
    others: List[Tuple[BaseUIElem, float, float]]

def menu_ui(callbacks: Tuple[Callable, Callable, Callable, Callable],
        sounds: Tuple[float, float], lang_callbacks: Tuple[Callable, Callable]) -> UI:
    """Create ui for main menu."""
    button_descr = ButtonDescr()
    slider_descr = SliderDescr(size=(0.5, 0.03), inner_fract=(0.125, 3.0))
    buttons_font = int(80 / 1280 * app_state().screen_res[0])
    name_font = int(128 / 1280 * app_state().screen_res[0])
    sound_font = int(64 / 1280 * app_state().screen_res[0])
    return UI(
        [
            Button(TextRect(_('Play'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.325, 0.2, 0.13], callbacks[0]),
            Button(TextRect(_('Exit'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.9, 0.1, 0.13], callbacks[1]),
            Button(TextRect(_('Ru'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.4, 0.5, 0.1, 0.13], lang_callbacks[0]),
            Button(TextRect(_('En'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.6, 0.5, 0.1, 0.13], lang_callbacks[1])
        ],
        [
            Slider(slider_descr, (0.6, 0.65), sounds[0], callbacks[2]),
            Slider(slider_descr, (0.6, 0.75), sounds[1], callbacks[3])
        ],
        [
            (TextRect(_('GAME'),
                pg.font.SysFont('arial', name_font), (0, 0, 0, 255)), 0.5, 0.15),
            (TextRect(_('Language'),
                pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.5),
            (TextRect(_('Music'),
                pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.65),
            (TextRect(_('Sounds'),
                pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.75)
        ]
    )

def pause_ui(continue_callback: Callable, menu_callback: Callable, music_callback: Callable,
            sound_callback: Callable, sounds: Tuple[float, float]) -> UI:
    """Create ui for pause menu."""
    button_descr = ButtonDescr()
    slider_descr = SliderDescr(size=(0.5, 0.03), inner_fract=(0.125, 3.0))
    buttons_font = int(80 / 1280 * app_state().screen_res[0])
    sound_font = int(64 / 1280 * app_state().screen_res[0])
    return UI(
        [
            Button(TextRect(_('Continue'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.2, 0.4, 0.13], continue_callback),
            Button(TextRect(_('Main menu'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.8, 0.4, 0.13], menu_callback)
        ],
        [
            Slider(slider_descr, (0.6, 0.5), sounds[0], music_callback),
            Slider(slider_descr, (0.6, 0.6), sounds[1], sound_callback)
        ],
        [
            (TextRect(_('Loudness'),
                pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.5, 0.35),
            (TextRect(_('Music'),
                pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.5),
            (TextRect(_('Sounds'),
                pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.6)
        ]
    )

def results_ui(restart_callback: Callable, menu_callback:
        Callable, killed_enemy_count: int, won: bool) -> UI:
    """Create ui for pause menu."""
    button_descr = ButtonDescr()
    buttons_font = int(80 / 1280 * app_state().screen_res[0])
    result_font = int(128 / 1280 * app_state().screen_res[0])
    return UI(
        [
            Button(TextRect(_('Restart'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.55, 0.4, 0.13], restart_callback),
            Button(TextRect(_('Main menu'), pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.75, 0.4, 0.13], menu_callback)
        ],
        [],
        [
            (TextRect(_('YOU WON!!!'),
                pg.font.SysFont('arial', result_font), (0, 255, 0, 255)), 0.5, 0.15)
        if won else
            (TextRect(_('YOU LOST!!!'),
                pg.font.SysFont('arial', result_font), (255, 0, 0, 255)), 0.5, 0.15),
            (TextRect(_('ENEMIES KILLED: {}').format(killed_enemy_count),
                    pg.font.SysFont('arial', result_font), (0, 0, 0, 255)), 0.5, 0.35),
        ]
    )

def game_ui() -> UI:
    """Create in-game ui."""
    return UI([], [], [])

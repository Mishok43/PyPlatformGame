"""Descriptions for all ui screens in game."""
from dataclasses import dataclass
from typing import Callable, List, Tuple
import pygame as pg
from app_state import app_state
from gui import ButtonDescr, SliderDescr, Button, Slider, TextRect, BaseUIElem

@dataclass
class UI:
    """Storage for all UI elements."""

    buttons: List[Button]
    sliders: List[Slider]
    others: List[Tuple[BaseUIElem, float, float]]

def menu_ui(play_callback: Callable, exit_callback: Callable, music_callback: Callable,
            sound_callback: Callable, sounds: Tuple[float, float]) -> UI:
    """Create ui for main menu."""
    button_descr = ButtonDescr()
    slider_descr = SliderDescr(size=(0.5, 0.03), inner_fract=(0.125, 3.0))
    buttons_font = int(80 / 1280 * app_state().screen_res[0])
    name_font = int(128 / 1280 * app_state().screen_res[0])
    sound_font = int(64 / 1280 * app_state().screen_res[0])
    return UI(
        [
            Button(TextRect('Play', pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.325, 0.2, 0.13], play_callback),
            Button(TextRect('Exit', pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.85, 0.2, 0.13], exit_callback)
        ],
        [
            Slider(slider_descr, (0.6, 0.6), sounds[0], music_callback),
            Slider(slider_descr, (0.6, 0.7), sounds[1], sound_callback)
        ],
        [
            (TextRect('GAME', pg.font.SysFont('arial', name_font), (0, 0, 0, 255)), 0.5, 0.15),
            (TextRect('Loudness', pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.5, 0.46),
            (TextRect('Music', pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.6),
            (TextRect('Sounds', pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.7)
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
            Button(TextRect('Continue', pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.2, 0.4, 0.13], continue_callback),
            Button(TextRect('Main menu', pg.font.SysFont('arial', buttons_font), (0, 0, 0, 255)),
                    button_descr, [0.5, 0.8, 0.4, 0.13], menu_callback)
        ],
        [
            Slider(slider_descr, (0.6, 0.5), sounds[0], music_callback),
            Slider(slider_descr, (0.6, 0.6), sounds[1], sound_callback)
        ],
        [
            (TextRect('Loudness', pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.5, 0.35),
            (TextRect('Music', pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.5),
            (TextRect('Sounds', pg.font.SysFont('arial', sound_font), (0, 0, 0, 255)), 0.25, 0.6)
        ]
    )

def game_ui() -> UI:
    """Create in-game ui."""
    return UI([], [], [])

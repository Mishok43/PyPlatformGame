"""GUI elements and related stuff."""
from dataclasses import dataclass
from typing import Callable, Tuple, List
from OpenGL import GL
import pygame as pg
import glm
from app_state import app_state
from audiomanager import AudioManager
class BaseUIElem:
    """Base UI elem that can be placed inside a button."""

    def get_relative_size(self) -> Tuple[float, float]:
        """Get size of the rectangle as fraction of screen size."""
        return (0.0, 0.0)
    def render(self, _ : Tuple[float, float]):
        """Render element at position."""

class TextRect(BaseUIElem):
    """Rectangle with specified text."""

    def __init__(self, text: str, font: pg.font.Font,
                color: Tuple[int,int,int,int] = (255, 255, 255, 255),
                size:Tuple[float,float] = None):
        """Render text with font and create texture."""
        text_surface = font.render(text, True, color)
        intermediate_alpha_surface = pg.Surface((text_surface.get_width(),
                                        text_surface.get_height()), pg.SRCALPHA)
        intermediate_alpha_surface.fill(pg.Color((0,0,0,0)))
        font_rect = text_surface.get_rect()
        font_rect.center = (text_surface.get_width() // 2, text_surface.get_height() // 2)
        intermediate_alpha_surface.blit(text_surface, font_rect)
        text_data = pg.image.tostring(intermediate_alpha_surface, "RGBA", True)
        self.tex_id = GL.glGenTextures(1)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        self.width = text_surface.get_width()
        self.height = text_surface.get_height()
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.width, self.height, 0,
                                            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, text_data)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        self.width /= app_state().screen_res[0]
        self.height /= app_state().screen_res[1]
        if size is not None:
            self.width = size[0]
            self.height = size[1]
    def get_relative_size(self) -> Tuple[float, float]:
        """Get size of the rectangle as fraction of screen size."""
        return (self.width, self.height)
    def render(self, pos: Tuple[float, float]) -> None:
        """Render rectangle with center at specified position."""
        app_state().shader_manager.use_program('tex_rect')
        blend = GL.glGetBooleanv(GL.GL_BLEND)
        blend_src = GL.glGetIntegerv(GL.GL_BLEND_SRC_ALPHA)
        blend_dst = GL.glGetIntegerv(GL.GL_BLEND_DST_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glUniform4f(app_state().shader_manager.get_uniform('pos_size'),
                        pos[0], 1.0-pos[1], *self.get_relative_size())
        app_state().shader_manager.set_texture('source', self.tex_id)
        app_state().mesh_manager.draw_quad()
        if not blend:
            GL.glDisable(GL.GL_BLEND)
        else:
            GL.glBlendFunc(blend_src, blend_dst)
    def __del__(self):
        """Delete texture."""
        GL.glDeleteTextures(1, [self.tex_id])

class TexturedRect(BaseUIElem):
    """Rectangle with specified texture."""

    def __init__(self, tex_name, size):
        """Create textured rectangle."""
        self.tex_id = app_state().texture_manager.get(tex_name,
                                GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, False)
        self.width = size[0]
        self.height = size[1]
    def get_relative_size(self) -> Tuple[float, float]:
        """Get size of the rectangle as fraction of screen size."""
        return (self.width, self.height)
    def render(self, pos : Tuple[float, float]) -> None:
        """Render rectangle with center at specified position."""
        app_state().shader_manager.use_program('tex_rect')
        blend = GL.glGetBooleanv(GL.GL_BLEND)
        blend_src = GL.glGetIntegerv(GL.GL_BLEND_SRC_ALPHA)
        blend_dst = GL.glGetIntegerv(GL.GL_BLEND_DST_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_ONE_MINUS_SRC_ALPHA, GL.GL_SRC_ALPHA)
        GL.glUniform4f(app_state().shader_manager.get_uniform('pos_size'),
                        pos[0], 1.0-pos[1], *self.get_relative_size())
        app_state().shader_manager.set_texture('source', self.tex_id)
        app_state().mesh_manager.draw_quad()
        if not blend:
            GL.glDisable(GL.GL_BLEND)
        else:
            GL.glBlendFunc(blend_src, blend_dst)

@dataclass
class ButtonDescr:
    """Button description."""

    border_size: float = 0.01
    frame_size: float = 0.003
    corner_r: float = 0.008
    background_color: Tuple[float, float, float] = (0.7, 0.7, 0.7)
    frame_color: Tuple[float, float, float] = (0.3, 0.3, 0.3)
    pressed_color: Tuple[float, float, float]  = (0.5, 0.5, 0.5)

class Button:
    """GUI button. Supports both rendering and user interaction."""

    def __init__(self, inner_elem: BaseUIElem, b_descr: ButtonDescr,
            pos_size: List[float], callback: Callable = None, click_sound_filename: str = "click_button.wav"):
        """Create button."""
        self.elem = inner_elem
        if len(pos_size) == 4:
            size = inner_elem.get_relative_size()
        else:
            size = (pos_size[2], pos_size[3])
        self.size = (size[0] + b_descr.border_size, size[1] + b_descr.border_size)
        self.frame_pix = b_descr.frame_size * app_state().screen_res[0]
        self.corner_pix = b_descr.corner_r * app_state().screen_res[0]
        self.descr = b_descr
        self.callback = callback
        self.pos = (pos_size[0], pos_size[1])
        self.click_sound_handle = AudioManager().get_sound_handle(click_sound_filename) if str != "" else -1
        
    def render(self, background_tex: int) -> None:
        """Render button."""
        app_state().shader_manager.use_program('button_background')
        GL.glUniform4f(app_state().shader_manager.get_uniform('pos_size'),
                            self.pos[0], 1.0 - self.pos[1], *self.size)
        if self.mouse_over():
            GL.glUniform3f(app_state().shader_manager.get_uniform('background_color'),
                                *self.descr.pressed_color)
        else:
            GL.glUniform3f(app_state().shader_manager.get_uniform('background_color'),
                                *self.descr.background_color)
        GL.glUniform3f(app_state().shader_manager.get_uniform('frame_color'),
                                *self.descr.frame_color)
        GL.glUniform2f(app_state().shader_manager.get_uniform('screen_size'),
                                *app_state().screen_res)
        GL.glUniform1f(app_state().shader_manager.get_uniform('frame'), self.frame_pix)
        GL.glUniform1f(app_state().shader_manager.get_uniform('corner'), self.corner_pix)
        app_state().shader_manager.set_texture('source', background_tex)
        app_state().mesh_manager.draw_quad()
        self.elem.render(self.pos)
    def mouse_over(self) -> bool:
        """Check if mouse is over button."""
        x_pos, y_pos = pg.mouse.get_pos()
        screen_sz = glm.vec2(app_state().screen_res[0], app_state().screen_res[1])
        centered = abs(glm.vec2(x_pos, y_pos) - screen_sz * glm.vec2(self.pos[0], self.pos[1]))
        size = screen_sz * glm.vec2(self.size[0], self.size[1]) * 0.5
        if centered.x > size.x or centered.y > size.y:
            return False
        to_border_pixels = size - centered
        if to_border_pixels.x < self.corner_pix and to_border_pixels.y < self.corner_pix:
            rad_x = to_border_pixels.x - self.corner_pix
            rad_y = to_border_pixels.y - self.corner_pix
            sq_dist = rad_x * rad_x + rad_y * rad_y
            if sq_dist > self.corner_pix * self.corner_pix:
                return False
        return True
    def process_event(self, event: pg.event.Event):
        """Process event to check if it is mouse click on button."""
        if self.mouse_over() and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.callback is not None:
                if self.click_sound_handle != -1:
                    AudioManager().play_sound(self.click_sound_handle)
                self.callback()

@dataclass
class SliderDescr:
    """GUI slider description."""

    frame_size: float = 0.003
    corner_r: float = 0.008
    background_color: Tuple[float, float, float] = (0.7, 0.7, 0.7)
    frame_color: Tuple[float, float, float] = (0.3, 0.3, 0.3)
    size: Tuple[float, float] = (0.5, 0.05)
    inner_fract: Tuple[float, float] = (0.25, 3.0)

class Slider:
    """GUI slider element. Supports both rendering and user interaction."""

    def __init__(self, s_descr: SliderDescr, pos: Tuple[float, float], state: float = 0.5,
                callback: Callable = None):
        """Create slider."""
        self.frame_pix = s_descr.frame_size * app_state().screen_res[0]
        self.corner_pix = s_descr.corner_r * app_state().screen_res[0]
        self.descr = s_descr
        self.callback = callback
        self.pos = pos
        self.size = s_descr.size
        self.state = state
    def render(self, background_tex: int) -> None:
        """Render slider."""
        app_state().shader_manager.use_program('button_background')
        GL.glUniform4f(app_state().shader_manager.get_uniform('pos_size'),
                            self.pos[0], 1.0 - self.pos[1], *self.size)
        GL.glUniform3f(app_state().shader_manager.get_uniform('background_color'),
                            *self.descr.frame_color)
        GL.glUniform3f(app_state().shader_manager.get_uniform('frame_color'),
                            *self.descr.frame_color)
        GL.glUniform2f(app_state().shader_manager.get_uniform('screen_size'),
                            *app_state().screen_res)
        GL.glUniform1f(app_state().shader_manager.get_uniform('frame'), self.frame_pix)
        GL.glUniform1f(app_state().shader_manager.get_uniform('corner'), self.corner_pix)
        app_state().shader_manager.set_texture('source', background_tex)
        app_state().mesh_manager.draw_quad()
        GL.glUniform4f(app_state().shader_manager.get_uniform('pos_size'),
                        self.pos[0] + (self.state - 0.5) * self.size[0],
                        1.0 - self.pos[1],
                        self.size[0] * self.descr.inner_fract[0],
                        self.size[1] * self.descr.inner_fract[1])
        GL.glUniform3f(app_state().shader_manager.get_uniform('background_color'),
                            *self.descr.background_color)
        app_state().mesh_manager.draw_quad()
    def process_input(self) -> None:
        """Update slider if user interacts with it."""
        x_pos, y_pos = pg.mouse.get_pos()
        screen_sz = glm.vec2(app_state().screen_res[0], app_state().screen_res[1])
        centered = glm.vec2(x_pos, y_pos) - screen_sz * glm.vec2(self.pos[0], self.pos[1])
        centered_abs = abs(centered)
        size = screen_sz * glm.vec2(self.size[0], self.size[1]) * 0.5
        if centered_abs.x > size.x or (centered_abs.y >
                                size.y * self.descr.inner_fract[1]):
            return
        if pg.mouse.get_pressed(num_buttons=3)[0]:
            self.state = centered.x / size.x * 0.5 + 0.5
            if self.state < self.descr.inner_fract[0] * 0.5:
                self.state = self.descr.inner_fract[0] * 0.5
            elif self.state > 1.0 - self.descr.inner_fract[0] * 0.5:
                self.state = 1.0 - self.descr.inner_fract[0] * 0.5
            if self.callback is not None:
                self.callback((self.state - self.descr.inner_fract[0] * 0.5)
                                / (1.0 - self.descr.inner_fract[0]))

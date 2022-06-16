"""Scene data storage and processing."""
from dataclasses import dataclass
import json
from typing import Tuple
from OpenGL import GL
import glm
from .app_state import app_state

@dataclass
class SceneElem:
    """Scene element description."""

    mesh_name: str
    tex_name: str
    pos: glm.vec3
    y_rotation: float
    scale: glm.vec3

@dataclass
class Billboard:
    """Billboard description."""

    tex_name: str
    pos: glm.vec2
    size: glm.vec2
    order: int

@dataclass
class Light:
    """Light description."""

    pos: glm.vec3
    dir: glm.vec3

@dataclass
class Camera:
    """Camera description."""

    pos: glm.vec3
    dir: glm.vec3

class Scene:
    """Scene storage and processing."""

    def __init__(self, scene_filename: str):
        """Load scene and save light data."""
        self.elems = []
        with open(scene_filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.z_near = float(data['z_near'])
            self.z_far = float(data['z_far'])
            self.shadow_z_near = float(data['shadow_z_near'])
            self.shadow_z_far = float(data['shadow_z_far'])
            self.shadow_fov = float(data['shadow_fov'])
            scene = data['scene']
            for obj in scene:
                mesh_name = obj['mesh_name']
                tex_name = obj['tex_name']
                for transform in obj['transforms']:
                    position = transform['position']
                    scale = transform['scale']
                    y_rotation = transform['y_rotation']
                    self.elems.append(SceneElem(mesh_name,
                                                tex_name,
                                                glm.vec3(position[0], position[1], position[2]),
                                                float(y_rotation),
                                                glm.vec3(scale[0], scale[1], scale[2])))
        self.billboard_list = []
    def before_render(self) -> None:
        """Prepare for rendering."""
        self.billboard_list = []
    def add_bilboard(self, name: str, pos: Tuple[float, float],
                    size: Tuple[float, float], order: int) -> None:
        """Add billboard object to be rendered on current frame."""
        self.billboard_list.append(Billboard(name, pos, size, order))
    def render_to_shadow(self, light: Light):
        """Render all needed parts to shadow map texture."""
        light_v = glm.lookAt(light.pos, light.pos + light.dir, glm.vec3(0,1,0))
        s_fov = self.shadow_fov
        light_p = glm.ortho(-s_fov, s_fov, -s_fov, s_fov, self.shadow_z_near, self.shadow_z_far)
        light_vp = light_p * light_v
        app_state().shader_manager.use_program('shadows')
        GL.glUniformMatrix4fv(app_state().shader_manager.get_uniform('VP'),
                                1, GL.GL_FALSE, glm.value_ptr(light_vp))
        for elem in self.elems:
            matrix = glm.rotate(glm.scale(glm.translate(glm.mat4(1), elem.pos), elem.scale),
                            elem.y_rotation, glm.vec3(0,1,0))
            GL.glUniformMatrix4fv(app_state().shader_manager.get_uniform('M'),
                                1, GL.GL_FALSE, glm.value_ptr(matrix))
            app_state().mesh_manager.draw(elem.mesh_name)
    def render(self, camera: Camera, light: Light, shadow_tex_id: int):
        """Render full scene for main pass."""
        # 3d scene elements
        projection = glm.perspective(45.0, app_state().screen_res[0] / app_state().screen_res[1],
                                    self.z_near, self.z_far)
        view = glm.lookAt(camera.pos, camera.pos + camera.dir, glm.vec3(0,1,0))
        light_v = glm.lookAt(light.pos, light.pos + light.dir, glm.vec3(0,1,0))
        s_fov = self.shadow_fov
        light_p = glm.ortho(-s_fov, s_fov, -s_fov, s_fov, self.shadow_z_near, self.shadow_z_far)
        light_vp = light_p * light_v
        main_vp = projection * view
        app_state().shader_manager.use_program('mesh_render')
        app_state().shader_manager.set_texture('shadow', shadow_tex_id)
        GL.glUniformMatrix4fv(app_state().shader_manager.get_uniform('VP'),
                                1, GL.GL_FALSE, glm.value_ptr(main_vp))
        GL.glUniformMatrix4fv(app_state().shader_manager.get_uniform('lightVP'),
                                1, GL.GL_FALSE, glm.value_ptr(light_vp))
        GL.glUniform3fv(app_state().shader_manager.get_uniform('lightPos'),
                                1, glm.value_ptr(light.pos))
        for elem in self.elems:
            matrix = glm.rotate(glm.scale(glm.translate(glm.mat4(1), elem.pos), elem.scale),
                            elem.y_rotation, glm.vec3(0,1,0))
            GL.glUniformMatrix4fv(app_state().shader_manager.get_uniform('M'),
                                1, GL.GL_FALSE, glm.value_ptr(matrix))
            app_state().shader_manager.set_texture('color_tex',
                                app_state().texture_manager.get(elem.tex_name))
            app_state().mesh_manager.draw(elem.mesh_name)
        # billboards
        self.billboard_list.sort(reverse=False,
                    key=lambda billboard: billboard.order)
        app_state().shader_manager.use_program('billboard')
        prev_blend = GL.glGetBooleanv(GL.GL_BLEND)
        prev_blend_src = GL.glGetIntegerv(GL.GL_BLEND_SRC_ALPHA)
        prev_blend_dst = GL.glGetIntegerv(GL.GL_BLEND_DST_ALPHA)
        GL.glEnable(GL.GL_BLEND)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        for obj in self.billboard_list:
            GL.glUniform4f(app_state().shader_manager.get_uniform('pos_size'),
                            obj.pos[0], 1.0-obj.pos[1], obj.size[0], obj.size[1])
            app_state().shader_manager.set_texture('source',
                                    app_state().texture_manager.get(obj.tex_name))
            app_state().mesh_manager.draw_quad()
        if not prev_blend:
            GL.glDisable(GL.GL_BLEND)
        else:
            GL.glBlendFunc(prev_blend_src, prev_blend_dst)
        GL.glDepthFunc(GL.GL_LESS)
    
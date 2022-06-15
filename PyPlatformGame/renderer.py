"""Main draw call."""
from OpenGL import GL
from .app_state import app_state
from .scene import Scene, Camera
from .ui_descr import UI

def draw(scene : Scene, interface: UI, camera: Camera):
    """Render current scene and interface."""
    # shadows
    app_state().rt_manager.bind(1024, 1024, [GL.GL_RG32F], True)
    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
    scene.render_to_shadow()
    depth_filtered = app_state().rt_manager.get_color(0)
    app_state().rt_manager.set_linear_filter(depth_filtered.get_id())
    app_state().rt_manager.bind(*app_state().screen_res, [GL.GL_RGBA8], True)
    GL.glClearColor(126/255,206/255,234/255,0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
    scene.render(camera, depth_filtered.get_id())
    depth_filtered = None
    result = app_state().rt_manager.get_color(0)
    depth = app_state().rt_manager.get_depth()
    app_state().rt_manager.set_linear_filter(result.get_id())
    # box blur for DoF
    app_state().rt_manager.bind(*app_state().screen_res, [GL.GL_RGBA8], False)
    app_state().shader_manager.use_program('blur')
    GL.glUniform2f(app_state().shader_manager.get_uniform('offset'),
                    1.5 / app_state().screen_res[0], 1.5 / app_state().screen_res[1])
    app_state().shader_manager.set_texture('source', result.get_id())
    app_state().mesh_manager.draw_fullscreen_triangle()
    result_blurred = app_state().rt_manager.get_color(0)
    app_state().rt_manager.set_linear_filter(result_blurred.get_id())
    # ssao
    app_state().rt_manager.bind(app_state().screen_res[0] // 2,
                                app_state().screen_res[1] // 2, [GL.GL_R8], False)
    app_state().shader_manager.use_program('ssao')
    app_state().shader_manager.set_texture('depthTex', depth.get_id())
    app_state().mesh_manager.draw_fullscreen_triangle()
    ssao = app_state().rt_manager.get_color(0)
    app_state().rt_manager.set_linear_filter(ssao.get_id())
    # ssao filtering
    app_state().rt_manager.bind(app_state().screen_res[0] // 2,
                                app_state().screen_res[1] // 2, [GL.GL_R8], False)
    app_state().shader_manager.use_program('blur')
    GL.glUniform2f(app_state().shader_manager.get_uniform('offset'),
                    3.0 / app_state().screen_res[0], 3.0 / app_state().screen_res[1])
    app_state().shader_manager.set_texture('source', ssao.get_id())
    app_state().mesh_manager.draw_fullscreen_triangle()
    ssao_blurred = app_state().rt_manager.get_color(0)
    app_state().rt_manager.set_linear_filter(ssao_blurred.get_id())
    ssao = None
    if len(interface.buttons) > 0 or len(interface.sliders) > 0:
        # vertical gauss blur (for UI)
        app_state().rt_manager.bind(app_state().screen_res[0],
                                    app_state().screen_res[1], [GL.GL_RGBA8], False)
        app_state().shader_manager.use_program('blur_v')
        GL.glUniform2f(app_state().shader_manager.get_uniform('offset'),
                    1.0 / app_state().screen_res[0], 1.0 / app_state().screen_res[1])
        app_state().shader_manager.set_texture('source', result.get_id())
        app_state().mesh_manager.draw_fullscreen_triangle()
        blur_v = app_state().rt_manager.get_color(0)
        app_state().rt_manager.set_linear_filter(blur_v.get_id())
        # horizontal gauss blur (for UI)
        app_state().rt_manager.bind(app_state().screen_res[0],
                                    app_state().screen_res[1], [GL.GL_RGBA8], False)
        app_state().shader_manager.use_program('blur_h')
        GL.glUniform2f(app_state().shader_manager.get_uniform('offset'),
                    1.0 / app_state().screen_res[0], 1.0 / app_state().screen_res[1])
        app_state().shader_manager.set_texture('source', blur_v.get_id())
        app_state().mesh_manager.draw_fullscreen_triangle()
        blur_g = app_state().rt_manager.get_color(0)
        app_state().rt_manager.set_linear_filter(blur_g.get_id())
        blur_v = None
    else:
        blur_g = None
    # combine everything and render to screen
    app_state().rt_manager.bind_fb0()
    app_state().shader_manager.use_program('resolve')
    GL.glUniform2f(app_state().shader_manager.get_uniform('far_dof_range'), 0.9, 0.95)
    app_state().shader_manager.set_texture('source', result.get_id())
    app_state().shader_manager.set_texture('source_blurred', result_blurred.get_id())
    app_state().shader_manager.set_texture('depth', depth.get_id())
    app_state().shader_manager.set_texture('ssao', ssao_blurred.get_id())
    app_state().mesh_manager.draw_fullscreen_triangle()
    depth = None
    result = None
    result_blurred = None
    ssao_blurred = None
    # UI
    for button in interface.buttons:
        button.render(blur_g.get_id())
    for slider in interface.sliders:
        slider.render(blur_g.get_id())
    for obj in interface.others:
        obj[0].render((obj[1], obj[2]))
    blur_g = None

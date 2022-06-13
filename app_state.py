"""More convinient processing of global state."""
from dataclasses import dataclass
from typing import Tuple
from render.shaders import ShaderManager
from render.textures import TextureManager
from render.rtargets import RTargetManager
from render.meshes import MeshManager

@dataclass
class AppState:
    """App state information."""

    screen_res: Tuple[int, int]
    rt_manager: RTargetManager
    shader_manager: ShaderManager
    texture_manager: TextureManager
    mesh_manager: MeshManager

APP_STATE_INTERNAL = None

def init_app_state(screen_res: Tuple[int, int],
                    shaders_folder: str,
                    textures_folder: str,
                    meshes_folder: str) -> None:
    """Init app state."""
    global APP_STATE_INTERNAL
    APP_STATE_INTERNAL = AppState(screen_res,
                                RTargetManager(screen_res),
                                ShaderManager(shaders_folder),
                                TextureManager(textures_folder),
                                MeshManager(meshes_folder))
def app_state() -> AppState:
    """Get app state."""
    return APP_STATE_INTERNAL

def delete_app_state() -> None:
    """Delete app state."""
    global APP_STATE_INTERNAL
    del APP_STATE_INTERNAL
    APP_STATE_INTERNAL = None

"""Meshes load, processing and management."""
import os
import ctypes
from OpenGL import GL
import numpy as np
import pywavefront

class Mesh:
    """Class for 3D model vertex data storage and rendering."""

    def __init__(self, filename: str):
        """Read data from .obj and create a vertex array."""
        scene = pywavefront.Wavefront(filename, collect_faces=True)
        if len(scene.materials) != 1:
            print(f'Incorrect number of matrials per object: {len(scene.materials)}')
        material = scene.materials[list(scene.materials.keys())[0]]
        vertices = np.array(material.vertices, dtype='float32')
        self.vertex_count = vertices.shape[0] // material.vertex_size
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.shape[0] * 4, vertices, GL.GL_STATIC_DRAW)
        size = material.vertex_size * 4
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, size,
                                    ctypes.c_void_p((material.vertex_size - 3)*4))
        if material.has_normals:
            GL.glEnableVertexAttribArray(1)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, size,
                                        ctypes.c_void_p((material.vertex_size - 6)*4))
            if material.has_uvs:
                GL.glEnableVertexAttribArray(2)
                GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, size, ctypes.c_void_p(0))
        elif material.has_uvs:
            GL.glEnableVertexAttribArray(2)
            GL.glVertexAttribPointer(2, 0, GL.GL_FLOAT, GL.GL_FALSE, size, ctypes.c_void_p(0))
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBindVertexArray(0)
    def draw(self) -> None:
        """Render the model."""
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)
        GL.glBindVertexArray(0)
    def __del__(self):
        """Delete owned OpenGL.GL objects."""
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteVertexArrays(1, [self.vao])

class MeshManager:
    """Manager for all used meshes."""

    def __init__(self, base_folder: str):
        """Init manager to load meshes from base_folder and create empty vao."""
        self.base_folder = base_folder
        self.meshes = {}
        self.empty_vao = GL.glGenVertexArrays(1)
    def draw(self, filename: str) -> None:
        """Render the mesh with specified name."""
        if filename not in self.meshes:
            self.meshes[filename] = Mesh(os.path.join(self.base_folder, filename))
        self.meshes[filename].draw()
    def draw_fullscreen_triangle(self) -> None:
        """Render fullscreen triangle."""
        GL.glBindVertexArray(self.empty_vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
        GL.glBindVertexArray(0)
    def draw_quad(self) -> None:
        """Render a quad made of two triangles."""
        GL.glBindVertexArray(self.empty_vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
        GL.glBindVertexArray(0)
    def __del__(self):
        """Remove all managed meshes and empty vao."""
        self.meshes = {}
        GL.glDeleteVertexArrays(1, [self.empty_vao])

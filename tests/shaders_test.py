"""Module which contains ShaderManager unit testing."""

import unittest
import pygame as pg
import os
import time

from PyPlatformGame.render import shaders


class ShaderManagerTest(unittest.TestCase):
    """Test class for validating shader management."""

    @classmethod
    def setUpClass(cls):
        """Setting up pygame with OpenGL before testing."""
        pg.display.set_mode((1, 1), pg.OPENGL|pg.DOUBLEBUF)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 1)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        shaders_folder  = os.path.join('PyPlatformGame', 'shaders')
        cls.shader_manager = shaders.ShaderManager(shaders_folder)

    @classmethod
    def tearDownClass(cls):
        """Cleanup."""
        del cls.shader_manager
        pg.display.quit()

    def test_use_correct(self):
        """Check binding for existing shaders."""
        shaders = ['tex_rect', 'mesh_render', 'ssao', 'billboard']
        for shader in shaders:
            self.assertTrue(self.shader_manager.use_program(shader)) 

    def test_use_missing(self):
        """Check binding for missing shaders."""
        self.assertFalse(self.shader_manager.use_program('some_random_shader')) 

    def test_get_uniform(self):
        """Check uniforms from correct shaders."""
        uniform_shader = [
            ('tex_rect', 'source'),
            ('mesh_render', 'lightVP'),
            ('resolve', 'source_blurred'),
            ('resolve', 'far_dof_range')
        ]
        for value in uniform_shader:
            self.shader_manager.use_program(value[0])
            self.assertNotEqual(-1, self.shader_manager.get_uniform(value[1])) 
    
    def test_uniforms_missing(self):
        """Check if -1 is returned for missing uniforms and shaders."""
        self.shader_manager.use_program('some_random_shader')
        self.assertEqual(-1, self.shader_manager.get_uniform('some_uniform'))
        self.shader_manager.use_program('tex_rect')
        self.assertEqual(-1, self.shader_manager.get_uniform('some_uniform'))

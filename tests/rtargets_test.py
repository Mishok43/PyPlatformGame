"""Module which contains RTargetManager unit testing."""

from turtle import rt
import unittest
import pygame as pg
import OpenGL.GL as GL

from PyPlatformGame.render import rtargets


class RtargetManagerTest(unittest.TestCase):
    """Test class for validating render target management."""

    @classmethod
    def setUpClass(cls):
        """Setting up pygame with OpenGL before testing."""
        pg.display.set_mode((2, 2), pg.OPENGL|pg.DOUBLEBUF)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 1)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

    @classmethod
    def tearDownClass(cls):
        """Cleanup OpenGL."""
        pg.display.quit()

    def setUp(self):
        """Create RTargetManager."""
        self.rt_manager = rtargets.RTargetManager((2, 2))

    def tearDown(self):
        """Delete RTargetManager."""
        del self.rt_manager

    def test_acquire(self):
        """Try to aquire some texture as rendertarget."""
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex = self.rt_manager.get_color(0)
        self.assertGreaterEqual(tex.get_id(), 0)
    
    def test_differ(self):
        """Test if different resolutions and formats have own targets."""
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_id0 = self.rt_manager.get_color(0).get_id()
        self.rt_manager.bind(1024, 1024, [GL.GL_R8])
        tex_id1 = self.rt_manager.get_color(0).get_id()
        self.rt_manager.bind(256, 256, [GL.GL_R8])
        tex_id2 = self.rt_manager.get_color(0).get_id()
        self.assertNotEqual(tex_id0, tex_id1)
        self.assertNotEqual(tex_id0, tex_id2)
        self.assertNotEqual(tex_id1, tex_id2)

    def test_reuse(self):
        """Test if target reuse works correctly."""
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_id0 = self.rt_manager.get_color(0).get_id()
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_id1 = self.rt_manager.get_color(0).get_id()
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_id2 = self.rt_manager.get_color(0).get_id()
        self.assertEqual(tex_id0, tex_id1)
        self.assertEqual(tex_id1, tex_id2)

    def test_preserve(self):
        """Test if target is not reused when."""
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_0 = self.rt_manager.get_color(0)
        tex_id0 = tex_0.get_id()
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_id1 = self.rt_manager.get_color(0).get_id()
        self.assertNotEqual(tex_id0, tex_id1)

    def test_compex(self):
        """Test sequence where first render target can be reused on third step."""
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_0 = self.rt_manager.get_color(0)
        tex_id0 = tex_0.get_id()
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_1 = self.rt_manager.get_color(0)
        tex_id1 = tex_1.get_id()
        self.assertNotEqual(tex_id0, tex_id1)
        tex_0 = None
        self.rt_manager.bind(1024, 1024, [GL.GL_RGBA8])
        tex_id2 = self.rt_manager.get_color(0).get_id()
        self.assertEqual(tex_id0, tex_id2)

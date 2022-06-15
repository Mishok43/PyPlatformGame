"""Render targets creation and management."""
import sys
from typing import List, Tuple
from OpenGL import GL

class TexHolder:
    """Storage for texture id for correct ref-counting."""

    def __init__(self) -> None:
        """Get texture id from OpenGL."""
        self.identifier = GL.glGenTextures(1)
    def get_id(self) -> int:
        """Get if of texture."""
        return self.identifier
    def __del__(self) -> None:
        """Delete texture."""
        GL.glDeleteTextures(1, [self.identifier])

class RTarget:
    """Render target description."""

    def __init__(self, width: int, height: int, fmt: GL.Constant):
        """Create empty texture with specified size and format."""
        self.width = width
        self.height = height
        self.fmt = fmt
        self.tex = TexHolder()
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex.get_id())
        GL.glTexStorage2D(GL.GL_TEXTURE_2D, 1, fmt, width, height)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    def check(self, width: int, height: int, fmt: GL.Constant) -> None:
        """Check if current render target has specified propierties and is not used enywhere."""
        return sys.getrefcount(self.tex) == 2 and (self.width == width) and (
                    self.height == height) and (self.fmt == fmt)
    def get_tex(self) -> TexHolder:
        """Get associated TexHolder."""
        return self.tex
    def __del__(self):
        """Delete render target."""
        del self.tex

class Framebuffer:
    """Management for framebuffer and its targets."""

    MAX_RTARGETS = 4
    DrawBuffers = [GL.GL_COLOR_ATTACHMENT0 + i for i in range(4)]
    def __init__(self):
        """Create OpenGL framebuffer object."""
        self.framebuffer = GL.glGenFramebuffers(1)
        self.textures = []
        self.depth = None
    def bind(self, textures: List[RTarget], depth: RTarget = None) -> None:
        """Attach specified textures as color and depth attachments and bind the framebuffer."""
        self.textures = textures
        self.depth = depth
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.framebuffer)
        count = len(textures)
        for i, tex in enumerate(textures):
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0 + i,
                                    GL.GL_TEXTURE_2D, tex.get_id(), 0)
        if depth:
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT,
                                    GL.GL_TEXTURE_2D, depth.get_id(), 0)
        else:
            GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glDepthMask(GL.GL_FALSE)
        GL.glDrawBuffers(count, self.DrawBuffers)
        if GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER) != GL.GL_FRAMEBUFFER_COMPLETE:
            print('Failed to bind framebuffer. Status is',
                    GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER))
    def unbind(self) -> None:
        """Unbind the framebuffer and its textures."""
        for i in range(len(self.textures)):
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0 + i,
                                        GL.GL_TEXTURE_2D, 0, 0)
        self.textures = []
        if self.depth:
            GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT,
                                        GL.GL_TEXTURE_2D, 0, 0)
        self.depth = None
    def get_color_tex(self, idx: int) -> RTarget:
        """Return color rendertarget with specified index."""
        if idx < len(self.textures):
            return self.textures[idx]
        return None
    def get_depth(self) -> RTarget:
        """Return depth target."""
        return self.depth
    def __del__(self):
        """Delete OpenGL framebuffer object."""
        GL.glDeleteFramebuffers(1, [self.framebuffer])

class RTargetManager:
    """Manager for all existing render targets to avoid manual resource tracking."""

    def __init__(self, backbuffer_res: Tuple[int, int]):
        """Initialize with specified backbuffer resolution."""
        self.framebuffers = []
        self.rtargets = []
        self.dtargets = []
        self.active = None
        self.backbuffer_res = backbuffer_res
    def bind(self, width: int, height: int, formats: List[GL.Constant] = None,
                needs_depth: bool = False) -> None:
        """Find, setup and bind framebuffer with specified propierties."""
        found = list(filter(lambda fb_descr: fb_descr[0] == width
                                    and fb_descr[1] == height, self.framebuffers))
        if len(found) == 0:
            found = Framebuffer()
            self.framebuffers.append((width, height, found))
        else:
            found = found[0][2]
        if self.active:
            self.active.unbind()
        self.active = found
        textures = []
        depth = None
        if formats:
            for fmt in formats:
                found_tex = None
                for rtarget in self.rtargets:
                    if rtarget.check(width, height, fmt):
                        found_tex = rtarget.get_tex()
                        break
                if found_tex is None:
                    rtarget = RTarget(width, height, fmt)
                    self.rtargets.append(rtarget)
                    found_tex = rtarget.get_tex()
                textures.append(found_tex)
        if needs_depth:
            found_tex = None
            for depth_target in self.dtargets:
                if depth_target.check(width, height, GL.GL_DEPTH24_STENCIL8):
                    found_tex = depth_target.get_tex()
                    break
            if found_tex is None:
                depth_target = RTarget(width, height, GL.GL_DEPTH24_STENCIL8)
                self.dtargets.append(depth_target)
                found_tex = depth_target.get_tex()
            depth = found_tex
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glDepthMask(GL.GL_TRUE)
        self.active.bind(textures, depth)
        GL.glViewport(0, 0, width, height)
    def get_color(self, idx: int) -> TexHolder:
        """Get color texture with specified index."""
        if self.active:
            return self.active.get_color_tex(idx)
        return None
    def get_depth(self) -> TexHolder:
        """Get depth texture."""
        if self.active:
            return self.active.get_depth()
        return None
    def unbind(self) -> None:
        """Unbind current framebuffer and bind default fbo."""
        if self.active:
            self.active.unbind()
            self.active = None
        self.bind_fb0()
    def bind_fb0(self) -> None:
        """Bind default framebuffer."""
        if self.active:
            self.active.unbind()
            self.active = None
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_FALSE)
        GL.glViewport(0, 0, self.backbuffer_res[0], self.backbuffer_res[1])

    def set_linear_filter(self, tex_id: int) -> None:
        """Set linear filtering mode for texture."""
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def __del__(self):
        """Cleanup all resources."""
        self.framebuffers = []
        self.rtargets = []
        self.dtargets = []
        self.active = None

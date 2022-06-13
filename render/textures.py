"""Textures management."""
import os
from PIL import Image
from OpenGL import GL

class Texture:
    """Texture creation and storage control."""

    def __init__(self, filename: str, wrap_mode: GL.Constant, filtering: GL.Constant, mips: bool):
        """Load texture from filename and set filtering mode."""
        img = Image.open(filename, 'r')
        self.tex_id = GL.glGenTextures(1)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_R, wrap_mode)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, wrap_mode)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, wrap_mode)
        min_f = mag_f = filtering
        if mips:
            if filtering == GL.GL_LINEAR:
                min_f = GL.GL_LINEAR_MIPMAP_LINEAR
            else:
                min_f = GL.GL_NEAREST_MIPMAP_LINEAR
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, min_f)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, mag_f)
        channels = len(img.getbands())
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, img.size[0], img.size[1], 0, GL.GL_RGBA,
         GL.GL_UNSIGNED_BYTE, img.tobytes("raw", "RGBX") if channels == 3 else img.tobytes("raw"))
        if mips:
            GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    def get(self) -> int:
        """Get texture id."""
        return self.tex_id
    def __del__(self):
        """Delete OpenGL texture object."""
        GL.glDeleteTextures(1, [self.tex_id])

class TextureManager:
    """Management for all textures, loaded from files."""

    def __init__(self, folder_name: str):
        """Set folder for textures."""
        self.textures = {}
        self.folder_name = folder_name
    def get(self, filename: str, wrap_mode: GL.Constant = GL.GL_REPEAT,
            filtering: GL.Constant = GL.GL_LINEAR, mips: bool = True):
        """Get texture id by name. Load new if none found."""
        if filename not in self.textures:
            self.textures[filename] = Texture(
                os.path.join(self.folder_name, filename), wrap_mode, filtering, mips)
        return self.textures[filename].get()
    def __del__(self):
        """Cleanup."""
        self.textures = {}

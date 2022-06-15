"""Shaders management."""
import os
from OpenGL import GL

class Shader:
    """Storage and management of OpenGL program object."""

    def __init__(self, program: int):
        """Set intial data values."""
        self.program = program
        self.uniforms = {}
        self.active_tex_slot = 0
    def use(self) -> None:
        """Use current program."""
        GL.glUseProgram(self.program)
        self.active_tex_slot = 0
    def uniform(self, name: str) -> int:
        """Get uniform locationby name."""
        if name in self.uniforms:
            return self.uniforms[name]
        uniform = GL.glGetUniformLocation(self.program, name)
        if uniform == -1:
            print(f'Uniform {name} not found')
        else:
            self.uniforms[name] = uniform
            return uniform
        return -1
    def set_texture(self, name: str, tex_id: int) -> None:
        """Set texture uniform."""
        uniform = self.uniform(name)
        if uniform == -1:
            return
        GL.glActiveTexture(GL.GL_TEXTURE0 + self.active_tex_slot)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
        GL.glUniform1i(uniform, self.active_tex_slot)
        self.active_tex_slot += 1

class ShaderManager:
    """Management of all shaders, used by app."""

    SHADER_EXTENSIONS = {
        '.vert' : GL.GL_VERTEX_SHADER,
        '.geom' : GL.GL_GEOMETRY_SHADER,
        '.tesc' : GL.GL_TESS_CONTROL_SHADER,
        '.tese' : GL.GL_TESS_EVALUATION_SHADER,
        '.frag' : GL.GL_FRAGMENT_SHADER,
        '.comp' : GL.GL_COMPUTE_SHADER
    }
    SHADER_EXTENSIONS_REV = {sh_type: ext for ext, sh_type in SHADER_EXTENSIONS.items()}
    GRAPHICS_PIPELINE_SHADERS = [GL.GL_VERTEX_SHADER, GL.GL_GEOMETRY_SHADER,
            GL.GL_TESS_CONTROL_SHADER, GL.GL_TESS_EVALUATION_SHADER, GL.GL_FRAGMENT_SHADER]
    # if a graphics pipeline is used at least vertex and fragment shaders should present
    REQUIRED_GRAPHICS_PIPELINE_SHADERS = [GL.GL_VERTEX_SHADER, GL.GL_FRAGMENT_SHADER]
    # if tessellation is enabled it should be used by both shaders
    TESSELLATION_SHADERS = [GL.GL_TESS_CONTROL_SHADER, GL.GL_TESS_EVALUATION_SHADER]
    COMPUTE_PIPELINE_SHADERS = [GL.GL_COMPUTE_SHADER]

    def __init__(self, shaders_folder_name: str):
        """Load all shaders from specified folder."""
        self.folder = shaders_folder_name
        self.program = None
        # load all possible pipelines grouped with shader names
        pipelines = {}
        for _, _, files in os.walk(self.folder):
            for file in files:
                filename, ext = os.path.splitext(file)
                if ext in self.SHADER_EXTENSIONS:
                    shader_type = self.SHADER_EXTENSIONS[ext]
                    if pipelines.get(filename):
                        pipelines[filename].append(shader_type)
                    else:
                        pipelines[filename] = [shader_type]
        # filter not complete pipelines and report on errors
        filtered_pipelines = {}
        for name, shaders in pipelines.items():
            shaders_set = set(shaders)
            is_graphics = len(set(self.GRAPHICS_PIPELINE_SHADERS) & shaders_set) > 0
            is_compute = len(set(self.COMPUTE_PIPELINE_SHADERS) & shaders_set) > 0
            failed = False
            if is_graphics and is_compute:
                print(f'Cannot select pipeline type for "{name}" shaders. '
                        'Use only graphics or compute shaders with common filename')
                failed = True
            if is_graphics:
                if (set(self.REQUIRED_GRAPHICS_PIPELINE_SHADERS)
                        & shaders_set) != set(self.REQUIRED_GRAPHICS_PIPELINE_SHADERS):
                    print(f'Looks like pipelines "{name}" is graphics, '
                            'but not all required shaders are specified')
                    failed = True
                if len(set(self.TESSELLATION_SHADERS) & shaders_set) == 1:
                    print(f'Looks like pipeline "{name}" uses tessellation, '
                            'but only one of tessellation stages has a shader')
                    failed = True
            if not failed:
                filtered_pipelines[name] = shaders
        # finally try to build pipelines and link programs
        self.programs = {}
        for name, shaders in filtered_pipelines.items():
            failed = False
            shader_ids = []
            for sh_type in shaders:
                filename = name + self.SHADER_EXTENSIONS_REV[sh_type]
                with open(os.path.join(self.folder, filename), 'r', encoding='utf-8') as file:
                    source = file.read()
                shader = GL.glCreateShader(sh_type)
                GL.glShaderSource(shader, source)
                GL.glCompileShader(shader)
                if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
                    print(f'Shader compilation of "{filename}" failed with error:')
                    print(GL.glGetShaderInfoLog(shader).decode('ascii'))
                    failed = True
                else:
                    shader_ids.append(shader)
            if not failed:
                program = GL.glCreateProgram()
                for shader_id in shader_ids:
                    GL.glAttachShader(program, shader_id)
                    GL.glDeleteShader(shader_id)
                GL.glLinkProgram(program)
                if GL.glGetProgramiv(program, GL.GL_LINK_STATUS) != GL.GL_TRUE:
                    print(f'Program linkage of "{filename}" failed with error:')
                    print(GL.glGetProgramInfoLog(program).decode('ascii'))
                    GL.glDeleteProgram(program)
                else:
                    self.programs[name] = Shader(program)
    def use_program(self, shader_name: str) -> bool:
        """Use shader with specified name."""
        if shader_name in self.programs:
            self.program = shader_name
            self.programs[shader_name].use()
            return True
        else:
            self.program = None
            print(f'Program {shader_name} not found and cannot be set')
            return False
    def get_uniform(self, name: str) -> int:
        """Get uniform from currently active shader."""
        if self.program is not None:
            return self.programs[self.program].uniform(name)
        return -1
    def set_texture(self, uniform_name: str, tex_id: int) -> None:
        """Bind texture to currently active shader."""
        if self.program is not None:
            self.programs[self.program].set_texture(uniform_name, tex_id)
    def __del__(self):
        """Delete OpenGL program objects."""
        for program in self.programs.values():
            GL.glDeleteProgram(program.program)

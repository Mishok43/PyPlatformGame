#version 430 core

layout(location=0) in vec3 pos;

uniform mat4 VP;
uniform mat4 M;

out float depth;

void main()
{
    gl_Position = VP * M * vec4(pos, 1);
    depth = gl_Position.z; 
}
#version 430 core

layout(location=0) in vec3 pos;
layout(location=1) in vec3 normal;
layout(location=2) in vec2 texcoord;

out vec3 nrml;
out vec2 tcrd;
out vec4 lightCrd;
out vec3 p;

uniform mat4 VP;
uniform mat4 M;
uniform mat4 lightVP;

void main()
{
    gl_Position = VP * M * vec4(pos, 1);
    nrml = (M * vec4(normal, 0.0)).xyz;
    tcrd = texcoord;
    lightCrd = lightVP * M * vec4(pos, 1);
    p = (M * vec4(pos, 1)).xyz;
}
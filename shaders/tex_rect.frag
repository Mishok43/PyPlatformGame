#version 430 core

in vec2 texcoords;

uniform sampler2D source;

out vec4 color;

void main()
{
    color = texture(source, texcoords);
}
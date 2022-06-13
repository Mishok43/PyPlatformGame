#version 430 core

in vec2 texcoords;

uniform sampler2D source;
uniform vec2 offset;

out vec4 color;

void main()
{
    vec4 value = texture(source, texcoords);
    value += texture(source, texcoords + vec2(offset.x, 0));
    value += texture(source, texcoords + vec2(-offset.x, 0));
    value += texture(source, texcoords + vec2(0, offset.y));
    value += texture(source, texcoords + vec2(0, -offset.y));
    value += texture(source, texcoords + vec2(offset.x, offset.y));
    value += texture(source, texcoords + vec2(-offset.x, offset.y));
    value += texture(source, texcoords + vec2(offset.x, -offset.y));
    value += texture(source, texcoords + vec2(-offset.x, -offset.y));
    color = value / 9.0;
}
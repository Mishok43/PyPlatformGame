#version 410 core

uniform vec4 pos_size;

out vec2 texcoords;

void main()
{
    vec2 vertices[6] = vec2[6](vec2(-1, -1), vec2(-1, 1), vec2(1, 1),    vec2(-1, -1), vec2(1, 1), vec2(1, -1));
    gl_Position = vec4(vertices[gl_VertexID]*pos_size.zw + (pos_size.xy * 2.0 - 1.0), -1, 1);
    texcoords = 0.5 * vertices[gl_VertexID] + vec2(0.5);
}
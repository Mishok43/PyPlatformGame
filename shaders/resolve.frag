#version 430 core

in vec2 texcoords;

uniform sampler2D source;
uniform sampler2D source_blurred;
uniform sampler2D depth;
uniform sampler2D ssao;
uniform vec2 far_dof_range;

out vec4 color;

void main()
{
    vec4 src = texture(source, texcoords);
    vec4 src_b = texture(source_blurred, texcoords);
    float d = texture(depth, texcoords).r;
    color = mix(src, src_b, smoothstep(far_dof_range.x, far_dof_range.y, d)) * texture(ssao, texcoords).r; 
}
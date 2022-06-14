#version 410 core

in vec2 texcoords;

uniform sampler2D source;

uniform vec3 background_color;
uniform vec3 frame_color;
uniform float frame;
uniform float corner;

uniform vec2 screen_size;
uniform vec4 pos_size;

out vec4 color;

void main()
{
    color = texture(source, texcoords);

    vec2 crd = gl_FragCoord.xy;
    vec2 centered = abs(crd - screen_size*pos_size.xy);
    vec2 to_border_pixels = screen_size * pos_size.zw * 0.5 - centered;
    vec3 mul = background_color;
    if (to_border_pixels.x < corner && to_border_pixels.y < corner)
    {
        vec2 rxy = to_border_pixels - corner;
        float sq_dist = rxy.x * rxy.x + rxy.y * rxy.y;
        float cf = corner - frame;
        if (sq_dist > corner * corner)
            discard;
        else if (sq_dist > cf * cf)
            mul = frame_color;
    }
    else if (to_border_pixels.x < frame || to_border_pixels.y < frame)
        mul = frame_color;
    color *= vec4(mul, 1.0);
}
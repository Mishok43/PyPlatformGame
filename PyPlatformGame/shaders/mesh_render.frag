#version 410 core

uniform sampler2D shadow;
uniform sampler2D color_tex;
uniform vec3 lightPos;

in vec3 nrml;
in vec2 tcrd;
in vec4 lightCrd;
in vec3 p;

out vec4 color;

float linstep(float min_r, float max_r, float v)
{
    return clamp((v - min_r) / (max_r - min_r), 0, 1);
}

float vsm(vec2 sampled, float d)
{
    const float eps = 10e-5;
    float p = float(d <= sampled.x + eps);
    float v = max(0.0, sampled.y - sampled.x*sampled.x); 
    float dif = d - sampled.x;   
    float p_max = v / (v + dif*dif);
    return max(p, linstep(0.3, 1, p_max));
}

void main()
{
    vec4 lcrd = lightCrd / lightCrd.w;
    vec2 shadowDepth = texture(shadow, lcrd.xy * 0.5 + 0.5).rg;
    float realDepth = lightCrd.z;
    vec3 lightDir = lightPos - p;
    color = texture(color_tex, vec2(tcrd.x, 1.0 - tcrd.y));
    color *= vec4(0.3) + clamp(dot(normalize(lightDir), nrml), 0.0, 1.0);
    color *= (0.4 + 0.6 * vsm(shadowDepth, realDepth));
}
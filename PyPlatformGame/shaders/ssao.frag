#version 410 core

uniform sampler2D depthTex;

in vec2 texcoords;
out float color;

const float PI = 3.1415926535897931;

void main() {
    float depth = texture(depthTex, texcoords).r;
    float r = 0.005 / depth;
    vec3 k = vec3(1.0, 0.75, 0.5);
    float res = 0.0f;
    for (int i = 0; i < 2; i++)
    {
        for (int dir = 0; dir < 3; dir++)
        {
            float v = float(dir) * 2.0 / 3.0 * PI;
            vec2 offset = vec2(cos(v), sin(v)) * r / k[i];
            float d1 = texture(depthTex, texcoords + offset).r;
            float d2 = texture(depthTex, texcoords - offset).r;
            float diff1 = depth - d1;
            float diff2 = depth - d2;
            if (d1 < 0.999 && d2 < 0.999 && diff1 * diff2 > 0 && d1 > 0.0 && d2 > 0.0)
                res += (diff1 * (1.0 - smoothstep(0.005, 0.0075, abs(diff1))) + diff2 * (1.0 - smoothstep(0.005, 0.0075, abs(diff2)))) * k[i];
        }
    }
    color = 1.0 - res*50.0;
}
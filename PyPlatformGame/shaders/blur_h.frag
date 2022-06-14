#version 410 core

in vec2 texcoords;

uniform sampler2D source;
uniform vec2 offset;

out vec4 color;

// #define GAUSS_R 9
// const float gaussWeights[10] = float[10](0.133176, 0.125979, 0.106639, 0.080775, 0.054750, 0.033208, 0.018023, 0.008753, 0.003804, 0.001479);

#define GAUSS_R 15
const float gaussWeights[16] = float[16](0.079940, 0.078358, 0.073794, 0.066772, 0.058049, 0.048486, 0.038911, 0.030003, 0.022226, 0.015820, 0.010819, 0.007108, 0.004487, 0.002722, 0.001586, 0.000888);

void main()
{
    vec4 value = texture(source, texcoords);
    color = value / 9.0;
    vec4 res = texture(source, texcoords) * gaussWeights[0];
    for (int i = 1; i <= GAUSS_R; i++)
        res += (texture(source, texcoords + vec2(offset.x * float(i), 0)) + texture(source, texcoords + vec2(-offset.x * float(i), 0))) * gaussWeights[i];
    color = res;
}
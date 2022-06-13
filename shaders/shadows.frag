#version 430 core

in float depth;
out vec2 color;

void main()
{
    float d = depth;
    float dx = dFdx(d);   
    float dy = dFdy(d);
    color = vec2(d, d*d + 0.25*(dx*dx + dy*dy));
}
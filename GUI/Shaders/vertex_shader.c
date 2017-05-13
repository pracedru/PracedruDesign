#version 130

attribute highp vec4 vertex;
attribute highp vec4 normal;
varying highp vec3 eye_norm;

uniform mediump vec4 color;
uniform mediump mat3 normal_matrix;
uniform mediump mat4 mvp;
void main(void)
{
    gl_Position = mvp * vertex;
    eye_norm = normalize(normal_matrix * normal.xyz);
}
#version 140

attribute highp vec4 vertex;
attribute highp vec4 normal;
varying highp vec3 eye_norm;

uniform mediump vec4 color;
uniform mediump mat4 model;
uniform mediump mat4 view;
uniform mediump mat4 mvp;
void main(void)
{
    mat3 normalMatrix = mat3(transpose(inverse(view * model)));
    gl_Position = mvp * vertex;
    eye_norm = normalize(normalMatrix * normal.xyz);

}
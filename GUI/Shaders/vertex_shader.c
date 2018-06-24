#version 130

in highp vec4 vertex;
in highp vec4 normal;

out highp vec3 position;
out highp vec3 eye_norm;
out highp vec3 globe_norm;
out highp vec3 eye_up;
out highp vec3 eye_vector;

uniform mediump mat3 normal_matrix;
uniform mediump mat4 model_view_matrix;
uniform mediump mat4 mvp;
void main(void)
{
    gl_Position = mvp * vertex;
    position = vec3(mvp * vertex);
    eye_norm = normalize(normal_matrix * normal.xyz);
    eye_up = normalize(normal_matrix * vec3(0.0,1.0,0.0));
    eye_vector = vec3(normalize(model_view_matrix * vertex));
    globe_norm = normal.xyz;
}
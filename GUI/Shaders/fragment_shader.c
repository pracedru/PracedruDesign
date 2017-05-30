#version 130

in highp vec3 eye_norm;
in highp vec3 globe_norm;
in highp vec3 eye_up;
in highp vec3 eye_vector;
uniform mediump vec4 color;
uniform mediump float specular;
uniform bool lighting;
uniform bool gradient;
uniform vec2 resolution;
uniform mediump mat4 model_view_matrix;
void main(void)
{
    float ambient = 0.65;
    float spec_size = 0.1 - specular/20;
    float spec = 0.0;
    vec4 lcol = color;
    vec4 scol = vec4(1.0,1.0,1.0,1.0);
    if (lighting) {

        vec3 enorm;
        vec3 gnorm;
        if (gl_FrontFacing){
            enorm = -eye_norm;
            gnorm = -globe_norm;
        }
        else {
            enorm = eye_norm;
            gnorm = globe_norm;
        }
        float p = dot(enorm, normalize(vec3(0.5, -0.7, 1.5)));
        float p2 = dot(eye_up, enorm);
        vec4 reflectedDirection = vec4(normalize(reflect(eye_vector, enorm)), 1.0);
        reflectedDirection = transpose(model_view_matrix) * reflectedDirection;
        spec = max((p-(1.0-spec_size))/spec_size,0)*2.0;
        spec = min(pow(spec,3.0)/25.0, 0.25);

        p -= specular/2;
        p = p < 0. ? 0. : p * (1.0-ambient);
        float s = min(specular, 1.0);
        ambient += s*reflectedDirection.y/5.0 + (1.0-s)*p2/10.0;
        lcol.x = color.x * (ambient + p);
        lcol.y = color.y * (ambient + p);
        lcol.z = color.z * (ambient + p);
        lcol += scol * spec * specular;
    }
    if (gradient){
        float grad = 0.18 * gl_FragCoord.y / resolution.y;
        lcol = vec4(0.68+grad, 0.68+grad, 0.73+grad,1.0);
    }
    gl_FragColor = lcol;
}
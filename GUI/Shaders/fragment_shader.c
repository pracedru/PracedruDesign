varying highp vec3 eye_norm;
uniform mediump vec4 color;
uniform bool lighting;
uniform bool gradient;
uniform vec2 resolution;
void main(void)
{
    vec4 lcol = color;
    if (lighting) {
        vec3 enorm;
        if (gl_FrontFacing){
            enorm = -eye_norm;
        }
        else {
            enorm = eye_norm;
        }
        float p = dot(enorm, normalize(vec3(0.5, -0.5, 1.0)));
        p = p < 0. ? 0. : p * 0.5;
        lcol.x = color.x * (0.5 + p);
        lcol.y = color.y * (0.5 + p);
        lcol.z = color.z * (0.5 + p);
    }
    if (gradient){
        float grad = 0.18 * gl_FragCoord.y / resolution.y;
        lcol = vec4(0.68+grad, 0.68+grad, 0.73+grad,1);
    }
    gl_FragColor = lcol;
}
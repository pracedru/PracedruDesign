varying highp vec3 eye_norm;
uniform mediump vec4 color;
uniform bool lighting;
uniform bool gradient;
uniform vec2 resolution;
void main(void)
{
    if (lighting) {
        if (gl_FrontFacing){
            eye_norm = -eye_norm;
        }
        float p = dot(eye_norm, normalize(vec3(0.5, -0.5, 1.0)));
        p = p < 0. ? 0. : p * 0.5;
        color.x = color.x * (0.5 + p);
        color.y = color.y * (0.5 + p);
        color.z = color.z * (0.5 + p);
    }
    if (gradient){
        float grad = 0.3 * gl_FragCoord.y / resolution;
        color = vec4(0.7+grad, 0.7+grad, 0.73+grad,1);
    }
    gl_FragColor = color;
}
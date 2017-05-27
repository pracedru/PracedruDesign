varying highp vec3 eye_norm;
uniform mediump vec4 color;
uniform bool lighting;
uniform bool gradient;
uniform vec2 resolution;
void main(void)
{
    float ambient = 0.55;
    float spec_size = 0.06;
    float spec = 0.0;
    vec4 lcol = color;
    if (lighting) {
        vec3 enorm;
        if (gl_FrontFacing){
            enorm = -eye_norm;
        }
        else {
            enorm = eye_norm;
        }
        float p = dot(enorm, normalize(vec3(0.5, -0.7, 1.5)));
        p = p < 0. ? 0. : p * (1.0-ambient);

        spec = max((p-(1.0-spec_size-ambient))/spec_size,0)*2;
        spec = min(pow(spec,3)/60, 0.10);
        p += spec;
        lcol.x = color.x * (ambient + p);
        lcol.y = color.y * (ambient + p);
        lcol.z = color.z * (ambient + p);
    }
    if (gradient){
        float grad = 0.18 * gl_FragCoord.y / resolution.y;
        lcol = vec4(0.68+grad, 0.68+grad, 0.73+grad,1);
    }
    gl_FragColor = lcol;
}
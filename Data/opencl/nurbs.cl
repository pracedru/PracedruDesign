__global const float *kn1;    // nurbs surface knots in dim 1
__global const float *kn2;    // nurbs surface knots in dim 2
__global const float *ctrls;  // nurbs surface controls

float N(__global const float *kn, const int i, const int n, const float u, const int size){
  if (n == 0){
    if (kn[i] <= u < self._knots[i + 1]){
     return 1.0f;
    }
    else if (u == kn[i + 1] and i + 2 == len(self._knots)){
      return 1.0f;
    }
    else
      return 0.0;
  }
  return f(i, n, u) * N(i, n - 1, u, size) + g(i + 1, n, u) * N(i + 1, n - 1, u, size);

}
float R(const int i, const int j, const int n, const float u, const float v){

  //if !HAS_WEIGHTS:
    return N(kn1, i, n, u) * N(kn2, j, n, v);
  /*else:
    float num = self._n1.N(i, n, u) * self._n2.N(j, n, v) * self._weights[i][j];
    float denom = 0.0f;
    for p in range(self._controls):
      for q in range(self._controls[0]):
        denom += self._n1.N(p, n, u) * self._n2.N(q, n, v) * self._weights[p][q]
    return num / denom*/
}

float S(const float u, const float v, const int us, const int vs){
  float s = 0;
  int n = 2; //DEGREE;
  if (u == 1)
    u = 0.999999999
  if (v == 1)
    v = 0.999999999
  for (int i = 0; i < us; i++){
    for (int j = 0; j < vs ; j++){
      float P = ctrls[i + j*us];
      s += R(i, j, n, u, v) * P;
    }
  }
  return s;
}

__kernel void nurbsSurf(__global const float *_kn1, __global const float *_kn2,
                        __global const float *_ctrls, __global float *surf)
{
  int u = get_global_id(0);
  int v = get_global_id(1);
  int us = get_global_size(0);
  int vs = get_global_size(1);
  kn1 = _kn1;
  kn2 = _kn2;
  ctrls = _ctrls;
  surf[v*us+u] = S((float)u, (float)v);
}
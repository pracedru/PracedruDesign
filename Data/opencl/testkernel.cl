__kernel void sum(__global const double *a_g, __global const double *b_g, __global double *res_g)
{
  int gid = get_global_id(0);
  res_g[gid] = a_g[gid] + b_g[gid];
}
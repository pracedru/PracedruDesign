import numpy as np


class Nurbs(object):
  def __init__(self):
    self._knots = [0, 0, 0, 1, 1, 1]
    self._weights = None
    self._controls = []
    self._degree = 2

  @property
  def controls(self):
    return self._controls

  def set_controls(self, controls):
    self._controls = controls
    self.create_knots(len(controls))

  def create_knots(self, control_count):
    self._knots.clear()
    self._weights = None
    self._knots.append(0.0)
    self._knots.append(0.0)
    for i in range(control_count - 1):
      k = i / (control_count - 2)
      self._knots.append(k)
    self._knots.append(1)
    self._knots.append(1)

  def g(self, i, n, u):
    num = self._knots[i + n] - u
    denom = self._knots[i + n] - self._knots[i]
    if denom == 0.0:
      denom = 1.0e-30
    return num / denom

  def f(self, i, n, u):
    num = u - self._knots[i]
    denom = self._knots[i + n] - self._knots[i]
    if denom == 0.0:
      denom = 1.0e-30
    return num / denom

  def N(self, i, n, u):
    if n == 0:
      if self._knots[i] <= u < self._knots[i + 1]:
        return 1.0
      elif u == self._knots[i + 1] and i + 2 == len(self._knots):
        return 1.0
      return 0.0
    return self.f(i, n, u) * self.N(i, n - 1, u) + self.g(i + 1, n, u) * self.N(i + 1, n - 1, u)

  def R(self, i, n, u):
    if self._weights is None:
      return self.N(i, n, u)
    else:
      num = self.N(i, n, u) * self._weights[i]
      denom = 0.0
      for j in range(self._controls):
        denom += self.N(j, n, u) * self._weights[i]
      return num / denom

  def C(self, u):
    c = None
    n = self._degree
    for i in range(len(self._controls)):
      P = self._controls[i]
      if c is None:
        c = self.R(i, n, u) * P
      else:
        c += self.R(i, n, u) * P
    return c


class NurbsSurface(object):
  def __init__(self):
    self._n1 = Nurbs()
    self._n2 = Nurbs()
    self._controls = None
    self._weights = None
    self._degree = 2

  def set_controls(self, controls):
    self._controls = controls
    self._n1.create_knots(len(controls))
    self._n2.create_knots(len(controls[0]))

  def R(self, i, j, n, u, v):
    if self._weights is None:
      return self._n1.N(i, n, u) * self._n2.N(j, n, v)
    else:
      num = self._n1.N(i, n, u) * self._n2.N(j, n, v) * self._weights[i][j]
      denom = 0.0
      for p in range(self._controls):
        for q in range(self._controls[0]):
          denom += self._n1.N(p, n, u) * self._n2.N(q, n, v) * self._weights[p][q]
      return num / denom

  def S(self, u, v):
    s = None
    n = self._degree
    if u == 1:
      u = 0.999999999
    if v == 1:
      v = 0.999999999
    for i in range(len(self._controls)):
      for j in range(len(self._controls[0])):
        P = self._controls[i][j]
        if s is None:
          s = self.R(i, j, n, u, v) * P
        else:
          s += self.R(i, j, n, u, v) * P
    return s


def example_surface():
  ns = NurbsSurface()
  controls = np.array([
    [[0, 0, 0], [1, 0, 0], [2, 0, 0]],
    [[0, 1, 0], [1, 1, 1], [2, 1, 0]],
    [[0, 2, 0], [1, 2, 0], [2, 2, 0]]])
  ns.set_controls(controls)
  return ns

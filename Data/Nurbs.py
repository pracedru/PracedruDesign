import numpy as np
from Data.Vertex import Vertex

class Nurbs(object):
	def __init__(self):
		self._knots = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
		self._weights = []
		self._controls = []
		self._degree = 2
		self._ntable = []

	def set_degree(self, value):
		self._degree = value

	@property
	def controls(self):
		return self._controls

	def setControls(self, controls):
		self.set_controls(controls)

	def set_controls(self, controls, knots=None, weights=None):
		self._controls = controls
		if knots:
			self._knots = knots
		else:
			self.create_knots(len(controls))
		if weights:
			self._weights = weights
		else:
			self.create_weights(len(controls))
		self._ntable = []

	def create_knots(self, control_count):
		self._knots.clear()
		self._weights = None
		for n in range(self._degree):
			self._knots.append(0.0)

		if control_count>self._degree:
			for i in range(control_count + 1 - self._degree):
				k = i / (control_count - self._degree)
				self._knots.append(k)

		for n in range(self._degree):
			self._knots.append(1.0)

	def create_weights(self, control_count):
		self._weights = []
		for i in range(control_count):
			self._weights.append(1.0)

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

	def lookup(self, i, n):
		if len(self._ntable) < i + 1:
			self._ntable.append({})
			return None
		else:
			if n in self._ntable[i]:
				return self._ntable[i][n]
			else:
				return None

	def N(self, i, n, u):
		if n == self._degree:
			lu = self.lookup(i, u)
			if lu is not None:
				return lu
		if n == 0:
			if self._knots[i] <= u < self._knots[i + 1]:
				return 1.0
			elif u == self._knots[i + 1] and i + 2 == len(self._knots):
				return 1.0
			return 0.0
		retval = self.f(i, n, u) * self.N(i, n - 1, u) + self.g(i + 1, n, u) * self.N(i + 1, n - 1, u)
		if n == self._degree:
			self._ntable[i][u] = retval
		return retval

	def R(self, i, n, u):
		if self._weights is None:
			return self.N(i, n, u)
		else:
			num = self.N(i, n, u) * self._weights[i]
			denom = 0.0
			for j in range(len(self._controls)):
				denom += self.N(j, n, u) * self._weights[j]
			if denom == 0.0:
				denom = 1e-99
			return num / denom

	def C(self, u):
		c = Vertex()
		n = self._degree
		if u == 1:
			u = 0.999999999
		for i in range(len(self._controls)):
			P = self._controls[i]
			c += P * self.R(i, n, u)
		return c

	def range(self, divs):
		verts = []

		numerator = float(divs) - 1.0;
		for i in range(divs):
			c = i / numerator;
			verts.append(self.C(c))

		return verts;



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

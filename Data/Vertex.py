from math import sqrt, atan2, pi, acos
import numpy as np

__author__ = 'mamj'


class Vertex(object):
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.xyz = np.array([float(x), float(y), float(z)])

	@property
	def length(self):
		return np.linalg.norm(self.xyz)

	def distance(self, other):
		return np.linalg.norm(self.xyz - other.xyz)

	@property
	def angle(self):
		return Vertex().angle_between3d_p(self, Vertex(1.0))

	def angle2d(self, other):
		diff = other.xyz - self.xyz
		return atan2(diff[1], diff[0])

	def angle3d(self, other):
		diff = other.xyz - self.xyz
		return atan2(diff[0], diff[1]), atan2(diff[0], diff[2])

	def __add__(self, other):
		if issubclass(type(other), Vertex):
			return Vertex.from_xyz(self.xyz + other.xyz)
		elif hasattr(other, "__len__"):
			if len(other) == 3:
				return Vertex(self.x + other[0], self.y + other[1], self.z + other[2])
			else:
				raise TypeError("Other must have size 3: " + str(other))
		return Vertex(self.x + other.x, self.y + other.y, self.z + other.z)

	def __truediv__(self, other):
		if type(other) is float or type(other) is int:
			return Vertex(self.x / other, self.y / other, self.z / other)
		else:
			raise TypeError("Vertex can not be diveded by: " + str(other))

	def __mul__(self, other):
		if type(other) is float or type(other) is int:
			return Vertex(self.x * other, self.y * other, self.z * other)
		else:
			raise TypeError("Vertex can not be multiplied by: " + str(other))

	def __sub__(self, other):
		return Vertex(self.x-other.x, self.y-other.y, self.y-other.y)

	def equals(self, other):
		return self.x == other.x and self.y == other.y and self.z == other.z

	def get_xyz(self):
		return self.xyz

	@property
	def x(self):
		return self.xyz[0]

	@property
	def y(self):
		return self.xyz[1]

	@property
	def z(self):
		return self.xyz[2]

	@x.setter
	def x(self, x):
		self.xyz[0] = x

	@y.setter
	def y(self, y):
		self.xyz[1] = y

	@z.setter
	def z(self, z):
		self.xyz[2] = z

	def serialize_json(self):
		return {'xyz': self.xyz.tolist()}

	@staticmethod
	def from_xyz(xyz):
		return Vertex(xyz[0], xyz[1], xyz[2])

	@staticmethod
	def deserialize(data):
		vertex = Vertex()
		if data is not None:
			vertex.deserialize_data(data)
		return vertex

	def deserialize_data(self, data):
		self.xyz = np.array(data['xyz'])

	def angle_between_untouched(self, kp1, kp2):
		alpha1 = self.angle2d(kp1)
		alpha2 = self.angle2d(kp2)
		alpha = alpha2 - alpha1
		return alpha

	def angle_between(self, kp1, kp2):
		alpha1 = self.angle2d(kp1)
		alpha2 = self.angle2d(kp2)
		alpha = alpha2 - alpha1
		while alpha < 0:
			alpha += 2 * pi
		while alpha > 2 * pi:
			alpha -= 2 * pi
		return alpha

	def angle_between_positive_minimized(self, kp1, kp2):
		angle = abs(self.angle_between(kp1, kp2))
		if angle > pi:
			angle = 2 * pi - angle
		return angle

	def angle_between3d_p(self, kp1, kp2):
		x = kp1.xyz - self.xyz
		y = kp2.xyz - self.xyz
		lx = np.linalg.norm(x)
		ly = np.linalg.norm(y)
		try:
			angle = acos(x.dot(y) / (lx * ly))
		except ValueError as e:
			print(str(e))
		return angle

	def angle_between3d_planar(self, kp1, kp2, norm):
		v1 = kp1.xyz - self.xyz
		v2 = kp2.xyz - self.xyz
		nm = np.linalg.norm(v1)
		if nm != 0:
			x_axis = v1 / nm
		else:
			x_axis = v1
		cp = np.cross(v1, norm)
		nm = abs(np.linalg.norm(cp))
		if nm != 0:
			y_axis = cp / nm
		else:
			y_axis = cp
		z_axis = norm
		m = np.array([x_axis, y_axis, z_axis])
		proj = m.dot(v2)
		angle = atan2(proj[1], proj[0])
		return angle

from Data.Objects import IdObject
from Data.Point3d import Point3d

__author__ = 'mamj'


class Curve(IdObject):
	def __init__(self, uid=None):
		IdObject.__init__(self, uid)
		self._start_point = Point3d()
		self._end_point = Point3d()

	@property
	def start_point(self):
		return self._start_point

	@property
	def end_point(self):
		return self._end_point

	def coincident(self, point):
		return False

	def length(self):
		return 0.0


class Line(Curve):
	def __init(self, p1, p2, uid=None):
		Curve.__init__(self, uid)
		self._start_point = p1
		self._end_point = p2

	def length(self):
		return abs(self._start_point.distance(self._end_point))

	def coincident(self, point):
		return False

	def serialize_json(self):
		return {'p1': self._start_point, 'p2': self._end_point}

	@staticmethod
	def deserialize(data):
		line = Line(Point3d.deserialize(data['p1']), Point3d.deserialize(data['p2']), data['uid'])
		return line


class Arc(Curve):
	def __init__(self, p1, p2, radius, uid=None):
		Curve.__init__(self, uid)
		self._start_point = p1
		self._end_point = p2
		self._radius = radius

	def length(self):
		pass

	def coincident(self, point):
		pass

	def serialize_json(self):
		return {'p1': self._start_point, 'p2': self._end_point, 'r': self._radius}

	@staticmethod
	def deserialize(data):
		arc = Arc(Point3d.deserialize(data['p1']), Point3d.deserialize(data['p2']), data['r'], data['uid'])
		return arc

	@property
	def center_point(self):
		return None


class Circle(Curve):
	def __init__(self, center, radius, uid=None):
		Curve.__init__(self, uid)
		self._center = center
		self._radius = radius
		self._start_point = Point3d(center.x, center.y + radius, center.z)
		self._end_point = self._start_point

	def serialize_json(self):
		return {'c': self._center, 'r': self._radius}

	@staticmethod
	def deserialize(data):
		arc = Arc(Point3d.deserialize(data['c']), data['r'], data['uid'])
		return arc

from math import pi, cos, sin, tan

from Data import get_uids
from Data.Edges import *
from Data.Events import ChangeEvent
from Data.Objects import IdObject, NamedObservableObject
from Data.Point3d import KeyPoint
from Data.Vertex import Vertex

__author__ = 'mamj'


class AreaType(Enum):
	EdgeLoop = 0
	Composite = 1


class Area(IdObject, NamedObservableObject):
	def __init__(self, sketch):
		IdObject.__init__(self)
		NamedObservableObject.__init__(self, "New Area")
		self._sketch = sketch
		self._brush = None
		self._brush_rotation = 50
		self._type = None

	@property
	def type(self):
		return self._type

	@property
	def brush(self):
		return self._brush

	@property
	def brush_name(self):
		if self._brush is None:
			return "None"
		else:
			return self._brush.name

	@property
	def brush_rotation(self):
		return self._brush_rotation

	@brush_rotation.setter
	def brush_rotation(self, value):
		self._brush_rotation = value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'name': 'brush_rotation'}))

	@brush_name.setter
	def brush_name(self, value):
		if value == "" or value is None or value == "None":
			self._brush = None
			self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'name': 'brush_name'}))
			return
		styles = self._sketch.document.get_styles()
		brush = styles.get_brush_by_name(value)
		self._brush = brush
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'name': 'brush_name'}))

	@staticmethod
	def deserialize(data, sketch):
		if data['area']['type'] == AreaType.EdgeLoop.value:
			area = EdgeLoopArea(sketch)
			area.deserialize_data(data, sketch)
			return area
		elif data['area']['type'] == AreaType.Composite.value:
			area = CompositeArea(sketch)
			area.deserialize_data(data, sketch)
			return area

	def serialize_json(self):
		brush_uid = None
		if self._brush is not None:
			brush_uid = self._brush.uid
		return \
			{
				'uid': IdObject.serialize_json(self),
				'no': NamedObservableObject.serialize_json(self),
				'type': self._type.value,
				'brush': brush_uid,
				'brush_rot': self._brush_rotation
			}

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		NamedObservableObject.deserialize_data(self, data.get('no', None))
		brush_uid = data.get('brush')
		self._brush = self._sketch.document.get_styles().get_brush(brush_uid)
		self._brush_rotation = data.get("brush_rot", 50)


class EdgeLoopArea(Area):
	def __init__(self, sketch):
		Area.__init__(self, sketch)
		self._edge_uids = []
		self._key_points = None
		self._type = AreaType.EdgeLoop
		self._change_events_initalized = True

	def get_edge_by_index(self, index):
		return self._sketch.get_edge(self._edge_uids[index])

	def inside(self, point):
		anglesum = 0.0
		last_point = None
		if self.get_edge_by_index(0).type == EdgeType.CircleEdge:
			kp = self.get_edge_by_index(0).get_keypoints()[0]
			r = self.get_edge_by_index(0).get_meta_data('r')
			if r > kp.distance(point):
				return True
			return False
		else:
			for pnt in self.get_inside_key_points():
				if last_point is not None:
					angle = point.angle_between(last_point, pnt)
					if angle > pi:
						angle = -(2 * pi - angle)
					anglesum += angle
				last_point = pnt
			if abs(anglesum) > pi:
				return True
			return False

	def get_intersecting_edges(self, kp, gamma):
		intersecting_edges = []
		for edge_uid in self._edge_uids:
			edge = self._sketch.get_edge(edge_uid)
			if edge.type is EdgeType.LineEdge:
				kps = edge.get_end_key_points()
				x1 = kps[0].x
				y1 = kps[0].y
				x2 = kps[1].x
				y2 = kps[1].y
				x3 = kp.x
				y3 = kp.y
				x4 = kp.x + cos(gamma)
				y4 = kp.y + sin(gamma)
				denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
				if denom != 0:
					px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
					py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
					int_kp = Vertex(px, py)
					if edge.distance(int_kp) < 0.001:
						intersecting_edges.append([edge, int_kp])
			elif edge.type is EdgeType.ArcEdge:
				center_kp = edge.get_keypoints()[0]
				radius = edge.get_meta_data('r')
				sa = edge.get_meta_data('sa')
				ea = edge.get_meta_data('ea')
				alpha = kp.angle2d(center_kp)
				dist = kp.distance(center_kp)
				beta = alpha - gamma
				rad_ray_dist = sin(beta) * dist
				if rad_ray_dist < radius:
					omega = center_kp.angle2d(kp)
					int_kp = Vertex(center_kp.x + cos(omega) * radius, center_kp.y + sin(omega) * radius)
					if edge.distance(int_kp) < 0.001:
						intersecting_edges.append([edge, int_kp])

		return intersecting_edges

	def insert_edge(self, edge):
		kps = edge.get_end_key_points()
		index = -1
		if kps[0] in self.get_keypoints():
			index = self._key_points.index(kps[0])
		if index != -1:
			self._edge_uids.insert(index, edge.uid)
		else:
			self._edge_uids.append(edge.uid)
		edge.add_change_handler(self.on_edge_changed)
		self._key_points = None

	def add_edge(self, edge):
		self._edge_uids.append(edge.uid)
		edge.add_change_handler(self.on_edge_changed)
		self._key_points = None

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def on_edge_changed(self, event: ChangeEvent):
		if event.type == ChangeEvent.Deleted:
			if type(event.object) is Edge:
				if event.object.type != EdgeType.FilletLineEdge:
					self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))
				else:
					fillet_edge = event.object
					self._edge_uids.remove(fillet_edge.uid)
					fillet_edge.remove_change_handler(self.on_edge_changed)
					self._key_points = None
			if type(event.object) is KeyPoint:
				self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def get_keypoints(self):
		"""
		This function returns the key points that control the edges of this area.
		:return:
		"""
		if self._key_points is None:
			self._key_points = []
			this_kp =  self.get_edge_by_index(0).get_end_key_points()[0]
			next_kp = self.get_edge_by_index(0).get_end_key_points()[1]
			if this_kp == self.get_edge_by_index(1).get_end_key_points()[0] or this_kp == self.get_edge_by_index(1).get_end_key_points()[1]:
				this_kp = self.get_edge_by_index(0).get_end_key_points()[1]
				next_kp = self.get_edge_by_index(0).get_end_key_points()[0]
			self._key_points.append(this_kp)
			self._key_points.append(next_kp)
			for i in range(1, len(self._edge_uids)):
				edge = self.get_edge_by_index(i)
				if edge.type != EdgeType.FilletLineEdge:
					if next_kp == edge.get_end_key_points()[0]:
						next_kp = edge.get_end_key_points()[1]
					else:
						next_kp = edge.get_end_key_points()[0]
					self._key_points.append(next_kp)
		return self._key_points

	def get_inside_key_points(self):
		"""
		This functions finds the key points used to determine if another point is inside this area
		:return: list of points describing the outside limits
		"""
		key_points = []
		edges = self.get_edges()
		if edges[0].type == EdgeType.CircleEdge:
			key_points.append(edges[0].get_end_key_points()[0])
		else:
			this_kp = edges[0].get_end_key_points()[0]
			next_kp = edges[0].get_end_key_points()[1]
			if this_kp == edges[1].get_end_key_points()[0] or this_kp == edges[1].get_end_key_points()[1]:
				this_kp = edges[0].get_end_key_points()[1]
				next_kp = edges[0].get_end_key_points()[0]
			key_points.append(this_kp)
			if edges[0].type == EdgeType.ArcEdge:
				ckp = edges[0].get_keypoints()[0]
				sa = edges[0].get_meta_data('sa')
				ea = edges[0].get_meta_data('ea')
				r = edges[0].get_meta_data('r')
				diff = ea - sa
				if diff < 0:
					diff += 2 * pi
				ma = sa + diff / 2
				key_points.append(Vertex(ckp.x + cos(ma) * r, ckp.y + sin(ma) * r))
			key_points.append(next_kp)
			for i in range(1, len(edges)):
				edge = edges[i]
				if edge.type != EdgeType.FilletLineEdge:
					if edge.type == EdgeType.ArcEdge:
						ckp = edge.get_keypoints()[0]
						sa = edge.get_meta_data('sa')
						ea = edge.get_meta_data('ea')
						r = edge.get_meta_data('r')
						diff = ea - sa
						if diff < 0:
							diff += 2 * pi
						ma = sa + diff / 2
						key_points.append(Vertex(ckp.x + cos(ma) * r, ckp.y + sin(ma) * r))
					if edge.type == EdgeType.NurbsEdge:
						edge_kps = edge.get_keypoints()
						for i in range(1, len(edge_kps)-1):
							edge_kp = edge_kps[i]
							key_points.append(edge_kp)
					if next_kp == edge.get_end_key_points()[0]:
						next_kp = edge.get_end_key_points()[1]
					else:
						next_kp = edge.get_end_key_points()[0]
					key_points.append(next_kp)
		return key_points

	def initialize_change_events(self):
		self._change_events_initalized = True
		for uid in self._edge_uids:
			edge = self._sketch.get_edge(uid)
			edge.add_change_handler(self.on_edge_changed)

	def get_edges(self):
		if not self._change_events_initalized:
			self.initialize_change_events()
		edges = []
		for uid in self._edge_uids:
			edges.append(self._sketch.get_edge(uid))
		return edges

	def serialize_json(self):
		return \
			{
				'area': Area.serialize_json(self),
				'edges': self._edge_uids
			}

	def deserialize_data(self, data, sketch):
		Area.deserialize_data(self, data['area'])
		self._edge_uids = data['edges']
		self._change_events_initalized = False


class CompositeArea(Area):
	def __init__(self, sketch):
		Area.__init__(self, sketch)
		self._base_area = None
		self._subtracted_areas = []
		self._added_areas = []
		self._type = AreaType.Composite

	@property
	def base_area(self):
		return self._base_area

	@base_area.setter
	def base_area(self, value):
		self._base_area = value

	@property
	def subtracted_areas(self):
		return self._subtracted_areas

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def add_subtract_area(self, area):
		if area not in self._subtracted_areas:
			self._subtracted_areas.append(area)
			area.add_change_handler(self.on_area_changed)

	def add_added_area(self, area):
		if area not in self._added_areas:
			self._added_areas.append(area)
			area.add_change_handler(self.on_area_changed)

	def inside(self, vertex):
		if self._base_area.inside(vertex):
			for area in self._subtracted_areas:
				if area.inside(vertex):
					return False
			return True

	def get_edges(self):
		edges = list(self.base_area.get_edges())
		for area in self._subtracted_areas:
			edges.extend(area.get_edges())
		return edges

	def on_area_changed(self, event: ChangeEvent):
		if event.type == ChangeEvent.Deleted:
			self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def serialize_json(self):
		return \
			{
				'area': Area.serialize_json(self),
				'base_area': self._base_area.uid,
				'subtracted_areas': get_uids(self._subtracted_areas),
				'added_areas': get_uids(self._added_areas)
			}

	def deserialize_data(self, data, sketch):
		Area.deserialize_data(self, data['area'])
		self._base_area = sketch.get_area(data['base_area'])
		for area_uid in data['subtracted_areas']:
			area = sketch.get_area(area_uid)
			self._subtracted_areas.append(area)
			area.add_change_handler(self.on_area_changed)
		for area_uid in data['added_areas']:
			area = sketch.get_area(area_uid)
			self._added_areas.append(area)
			area.add_change_handler(self.on_area_changed)

from enum import Enum

from Data import get_uids
from Data.Areas import CompositeArea, EdgeLoopArea, AreaType, Edge
from Data.Edges import EdgeType
from Data.Events import ChangeEvent
from Data.Objects import IdObject, NamedObservableObject
from Data.Parameters import Parameters
from Data.Point3d import KeyPoint


class ProformerType(Enum):
	Circular = 0
	Diamond = 1
	Triangular = 2
	Square = 3
	Rectangular = 4
	Mirror = 5
	MirrorX = 6
	MirrorY = 7
	MirrorXY = 8


class Proformer(IdObject, Parameters):
	def __init__(self, sketch, type=ProformerType.Circular, name="New proformation"):
		IdObject.__init__(self)
		Parameters.__init__(self, name)
		self._sketch = sketch
		self._type = type
		self._kps = set()
		self._edges = set()
		self._areas = set()
		self._result_kps = {}
		self._result_edges = {}
		self._result_areas = {}
		self._lookup_kps = {}
		self._lookup_edges = {}
		self._lookup_areas = {}
		self._meta_data = {}
		self._meta_data_parameters = {}

	def remove_change_handlers(self):
		for kp in self._kps:
			kp.remove_change_handler(self.kp_changed)
		for edge in self._edges:
			edge.remove_change_handler(self.edge_changed)
		for area in self._areas:
			area.remove_change_handler(self.area_changed)

	def delete(self):
		self.remove_change_handlers()
		self.clear_all()
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	@property
	def base_keypoints(self):
		return list(self._kps)

	@base_keypoints.setter
	def base_keypoints(self, value):
		self._kps = set()
		for kp in value:
			self._kps.add(kp)

	def get_keypoint(self, uid):
		if uid in self._result_kps:
			return self._result_kps[uid]
		return None

	@property
	def base_edges(self):
		return list(self._edges)

	@base_edges.setter
	def base_edges(self, value):
		self._edges = set()
		for edge in value:
			self._edges.add(edge)

	def get_edge(self, uid):
		if uid in self._result_edges:
			return self._result_edges[uid]
		return None

	@property
	def base_areas(self):
		return list(self._areas)

	@base_areas.setter
	def base_areas(self, value):
		self._areas = set()
		for area in value:
			self._areas.add(area)

	def get_area(self, uid):
		if uid in self._result_areas:
			return self._result_areas[uid]
		return None

	@property
	def result_keypoints(self):
		return self._result_kps.values()

	@property
	def result_edges(self):
		return self._result_edges.values()

	@property
	def result_areas(self):
		return self._result_areas.values()

	def kp_changed(self, event: ChangeEvent):
		self.update_kp(event.sender, event)

	def edge_changed(self, event: ChangeEvent):
		self.update_edge(event.sender, event)

	def area_changed(self, event: ChangeEvent):
		self.update_area(event.sender, event)

	def clear_all(self):
		for area in self._result_areas.values():
			area.delete()
		for edge in self._result_edges.values():
			edge.delete()
		for kp in self._result_kps.values():
			kp.delete()
		self._result_kps = {}
		self._result_edges = {}
		self._result_areas = {}
		self._lookup_kps = {}
		self._lookup_edges = {}
		self._lookup_areas = {}
		for parameter in self.get_all_parameters():
			parameter.delete()

	def update_kp(self, kp, event = None):
		if self._type == ProformerType.MirrorX:
			if event is None:
				new_kp = self._lookup_kps[kp.uid]
				new_kp.y = -kp.y
				new_kp.x = kp.x
				for vertext_instance_tuple in kp.instances:
					new_kp.set_instance_x(vertext_instance_tuple[0], vertext_instance_tuple[1].x)
					new_kp.set_instance_y(vertext_instance_tuple[0], -vertext_instance_tuple[1].y)
			else:
				instance = event.object['instance']
				new_kp = self._lookup_kps[kp.uid]
				new_kp.set_instance_y(instance, -kp.get_instance_y(instance))
				new_kp.set_instance_x(instance, kp.get_instance_x(instance))
		if self._type == ProformerType.MirrorY:
			new_kp = self._lookup_kps[kp.uid]
			new_kp.y = kp.y
			new_kp.x = -kp.x


	def update_edge(self, edge, event=None):
		pass

	def update_area(self, area, event=None):
		new_area = self._lookup_areas[area.uid]
		new_area.brush_name = area.brush_name
		new_area.brush_rotation = area.brush_rotation

	def generate_kp(self, kp):
		if self._type == ProformerType.MirrorX or self._type == ProformerType.MirrorY:
			kp.add_change_handler(self.kp_changed)
			new_kp = KeyPoint(self._sketch)
			new_kp.editable = False
			self._result_kps[new_kp.uid] = new_kp
			self._lookup_kps[kp.uid] = new_kp

	def generate_edge(self, edge):
		if self._type == ProformerType.MirrorX:
			edge.add_change_handler(self.edge_changed)
			new_edge = Edge(self._sketch, edge.type, edge.name+"MIRX")
			new_edge.style_name = edge.style_name
			for kp in edge.get_key_points():
				new_edge.add_key_point(self._lookup_kps[kp.uid])
			if edge.type == EdgeType.FilletLineEdge:
				r = edge.get_meta_data('r', None)
				new_edge.set_meta_data('r', r)
				r_param = edge.get_meta_data_parameter('r')
				new_edge.set_meta_data_parameter('r', r_param)
			new_edge.editable = False
			self._result_edges[new_edge.uid] = new_edge
			self._lookup_edges[edge.uid] = new_edge

	def generate_area(self, area):
		if self._type == ProformerType.MirrorX:
			if issubclass(type(area), CompositeArea):
				area.add_change_handler(self.area_changed)
				new_area = CompositeArea(self._sketch)
				new_base_area = self._lookup_areas[area.base_area.uid]
				new_area.base_area = new_base_area
				for subtracted_area in area.subtracted_areas:
					new_subtracted_area = self._lookup_areas[subtracted_area.uid]
					new_area.add_subtract_area(new_subtracted_area)
				new_area.brush_name = area.brush_name
				new_area.name = area.name + "MIRX"
				self._result_areas[new_area.uid] = new_area
				self._lookup_areas[area.uid] = new_area
			else:
				area.add_change_handler(self.area_changed)
				new_area = EdgeLoopArea(self._sketch)
				for edge in area.get_edges():
					new_edge = self._lookup_edges[edge.uid]
					new_area.add_edge(new_edge)
				new_area.name = area.name + "MIRX"
				self._result_areas[new_area.uid] = new_area
				self._lookup_areas[area.uid] = new_area
				new_area.brush_name = area.brush_name

	def generate_all(self):
		base_areas = []
		for area in self._areas:
			if area.type == AreaType.Composite:
				if area.base_area not in base_areas:
					base_areas.append(area.base_area)
				for c_area in area.subtracted_areas:
					if c_area not in base_areas:
						base_areas.append(c_area)
		for area in self._areas:
			if area not in base_areas:
				base_areas.append(area)
		for area in base_areas:
			for edge in area.get_edges():
				self._edges.add(edge)
		for edge in self._edges:
			for kp in edge.get_key_points():
				if kp not in self._kps:
					self._kps.add(kp)
		for kp in self._kps:
			self.generate_kp(kp)
			self.update_kp(kp)
		for edge in self._edges:
			self.generate_edge(edge)
			self.update_edge(edge)
		for area in base_areas:
			self.generate_area(area)
			self.update_area(area)

	def resolve(self):
		self.clear_all()
		self.generate_all()


	def on_parameter_change(self, event: ChangeEvent):
		param = event.sender
		uid = param.uid
		meta_name = self._meta_data_parameters[uid]
		self._meta_data[meta_name] = param.value

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'no': NamedObservableObject.serialize_json(self),
			'type': self._type.value,
			'kps': get_uids(self._kps),
			'edges': get_uids(self._edges),
			'areas': get_uids(self._areas),
			'meta_data': self._meta_data,
			'meta_data_parameters': self._meta_data_parameters
		}

	@staticmethod
	def deserialize(parent, data):
		proformer = Proformer(parent)
		if data is not None:
			proformer.deserialize_data(data)
		return proformer

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		NamedObservableObject.deserialize_data(self, data['no'])
		self._type = ProformerType(data['type'])
		for kp_uid in data['kps']:
			kp = self._sketch.get_keypoint(kp_uid)
			self._kps.add(kp)
			kp.add_change_handler(self.kp_changed)
		for edge_uid in data['edges']:
			edge = self._sketch.get_edge(edge_uid)
			self._edges.add(edge)
			edge.add_change_handler(self.edge_changed)
		for area_uid in data['areas']:
			area = self._sketch.get_area(area_uid)
			self._areas.add(area)
			area.add_change_handler(self.area_changed)
		self._meta_data = data.get('meta_data')
		self._meta_data_parameters = data.get('meta_data_parameters')
		for parameter_uid in self._meta_data_parameters:
			param = self._sketch.get_parameter_by_uid(parameter_uid)
			if param is not None:
				param.add_change_handler(self.on_parameter_change)

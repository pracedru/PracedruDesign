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
		self._lookups_kps = []
		self._lookups_edges = []
		self._lookups_areas = []
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
		self._lookups_kps = []
		self._lookups_edges = []
		self._lookups_areas = []
		for parameter in self.get_all_parameters():
			parameter.delete()

	def update_kp(self, kp, event = None):
		if event is not None:
			if event.type == ChangeEvent.Deleted:
				kp = event.object
				kp.remove_change_handler(self.kp_changed)
				if kp in self._kps:
					self._kps.remove(kp)
				for lookup_kps in self._lookups_kps:
					if kp.uid in lookup_kps:
						new_kp = lookup_kps[kp.uid]
						self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectRemoved, new_kp))
						lookup_kps.pop(kp.uid)
						if new_kp.uid in self._result_kps:
							self._result_kps.pop(new_kp.uid)
						new_kp.delete()
						self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.ObjectRemoved, new_kp))
				return
		if self._type == ProformerType.MirrorX or self._type == ProformerType.MirrorY or self._type == ProformerType.Mirror:
			self.update_kp_mirror(kp, event, 0)
		elif self._type == ProformerType.MirrorXY:
			self.update_kp_mirror(kp, event, 0)
			self.update_kp_mirror(kp, event, 1)
			self.update_kp_mirror(kp, event, 2)

	def update_kp_mirror(self, kp, event, p_index):
		if event is None:
			new_kp = self._lookups_kps[p_index][kp.uid]
			coord = self.get_coordinate(kp.x, kp.y, p_index)
			new_kp.x = coord[0]
			new_kp.y = coord[1]
			for vertext_instance_tuple in kp.instances:
				coord = self.get_coordinate(vertext_instance_tuple[1].x, vertext_instance_tuple[1].y, p_index)
				new_kp.set_instance_x(vertext_instance_tuple[0], coord[0])
				new_kp.set_instance_y(vertext_instance_tuple[0], coord[1])
		else:
			instance = event.object['instance']
			new_kp = self._lookups_kps[p_index][kp.uid]
			coord = self.get_coordinate(kp.get_instance_x(instance), kp.get_instance_y(instance), p_index)
			new_kp.set_instance_x(instance, coord[0])
			new_kp.set_instance_y(instance, coord[1])

	def get_coordinate(self, x, y, p_index):
		coord = [0.0, 0.0]
		if self._type == ProformerType.MirrorX:
			coord[0] = x
			coord[1] = -y
		elif self._type == ProformerType.MirrorY:
			coord[0] = -x
			coord[1] = y
		elif self._type == ProformerType.MirrorXY:
			if p_index == 0:
				coord[0] = x
				coord[1] = -y
			elif p_index == 1:
				coord[0] = -x
				coord[1] = y
			elif p_index == 2:
				coord[0] = -x
				coord[1] = -y
		else:
			# todo: line mirror needs implementation
			coord[0] = x
			coord[1] = y
		return coord

	def update_edge(self, edge, event=None):
		if event is None:
			pass
		else:
			if event.type == ChangeEvent.Deleted:
				edge.remove_change_handler(self.edge_changed)
				if edge in self._edges:
					self._edges.remove(edge)
				for lookup_edges in self._lookups_edges:
					if edge.uid in lookup_edges:
						new_edge = lookup_edges[edge.uid]
						self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectRemoved, new_edge))
						lookup_edges.pop(edge.uid)
						if new_edge.uid in self._result_edges:
							self._result_edges.pop(new_edge.uid)
						new_edge.delete()
						self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.ObjectRemoved, new_edge))
				return

	def update_area(self, area, event=None):
		if event is None:
			pass
		else:
			if event.type == ChangeEvent.Deleted:
				area.remove_change_handler(self.area_changed)
				if area in self._areas:
					self._areas.remove(area)
				for lookup_areas in self._lookups_areas:
					if area.uid in lookup_areas:
						new_area = lookup_areas[area.uid]
						self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectRemoved, new_area))
						lookup_areas.pop(area.uid)
						if new_area.uid in self._result_areas:
							self._result_areas.pop(new_area.uid)
						new_area.delete()
						self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.ObjectRemoved, new_area))
				return
		for lookup_areas in self._lookups_areas:
			if area.uid in lookup_areas:
				new_area = lookup_areas[area.uid]
				new_area.name = area.name + self._type.name
				new_area.brush_name = area.brush_name
				new_area.brush_rotation = area.brush_rotation

	def generate_kp(self, kp):
		if self._type == ProformerType.MirrorX or self._type == ProformerType.MirrorY:
			count = 1
		if self._type == ProformerType.MirrorXY:
			count = 3
		for i in range(count):
			kp.add_change_handler(self.kp_changed)
			new_kp = KeyPoint(self._sketch)
			self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectAdded, new_kp))
			new_kp._uid = kp.uid + "-" + self._type.name + str(i)
			new_kp.editable = False
			self._result_kps[new_kp.uid] = new_kp
			self._lookups_kps[i][kp.uid] = new_kp
			self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.ObjectAdded, new_kp))

	def generate_edge(self, edge):
		if self._type == ProformerType.MirrorX or self._type == ProformerType.MirrorY:
			count = 1
		if self._type == ProformerType.MirrorXY:
			count = 3
		for i in range(count):
			edge.add_change_handler(self.edge_changed)
			new_edge = Edge(self._sketch, edge.type, edge.name+self._type.name)
			self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectAdded, new_edge))
			new_edge._uid = edge.uid + "-" + self._type.name + str(i)
			new_edge.style_name = edge.style_name
			for kp in edge.get_keypoints():
				new_edge.add_key_point(self._lookups_kps[i][kp.uid])
			if edge.type == EdgeType.FilletLineEdge:
				r = edge.get_meta_data('r', None)
				new_edge.set_meta_data('r', r)
				r_param = edge.get_meta_data_parameter('r')
				new_edge.set_meta_data_parameter('r', r_param)
			new_edge.editable = False
			self._result_edges[new_edge.uid] = new_edge
			self._lookups_edges[i][edge.uid] = new_edge
			self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.ObjectAdded, new_edge))

	def generate_area(self, area):
		if self._type == ProformerType.MirrorX or self._type == ProformerType.MirrorY:
			count = 1
		if self._type == ProformerType.MirrorXY:
			count = 3
		for i in range(count):
			if issubclass(type(area), CompositeArea):
				area.add_change_handler(self.area_changed)
				new_area = CompositeArea(self._sketch)
				new_area._uid = area.uid + "-" + self._type.name + str(i)
				self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectAdded, new_area))
				new_base_area = self._lookups_areas[i][area.base_area.uid]
				new_area.base_area = new_base_area
				for subtracted_area in area.subtracted_areas:
					new_subtracted_area = self._lookups_areas[i][subtracted_area.uid]
					new_area.add_subtract_area(new_subtracted_area)
				new_area.brush_name = area.brush_name
				new_area.name = area.name + self._type.name
				self._result_areas[new_area.uid] = new_area
				self._lookups_areas[i][area.uid] = new_area
			else:
				area.add_change_handler(self.area_changed)
				new_area = EdgeLoopArea(self._sketch)
				new_area._uid = area.uid + "-" + self._type.name + str(i)
				self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.BeforeObjectAdded, new_area))
				for edge in area.get_edges():
					new_edge = self._lookups_edges[i][edge.uid]
					new_area.add_edge(new_edge)
				new_area.name = area.name + self._type.name
				self._result_areas[new_area.uid] = new_area
				self._lookups_areas[i][area.uid] = new_area
				new_area.brush_name = area.brush_name

			self._sketch.changed(ChangeEvent(self._sketch, ChangeEvent.ObjectAdded, new_area))

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
			for kp in edge.get_keypoints():
				if kp not in self._kps:
					self._kps.add(kp)

		if self._type == ProformerType.MirrorX or self._type == ProformerType.MirrorY or self._type == ProformerType.Mirror:
			self._lookups_kps.append({})
			self._lookups_edges.append({})
			self._lookups_areas.append({})
		elif self._type == ProformerType.MirrorXY:
			for i in range(3):
				self._lookups_kps.append({})
				self._lookups_edges.append({})
				self._lookups_areas.append({})

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


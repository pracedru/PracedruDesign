from enum import Enum

from Data import get_uids
from Data.Areas import CompositeArea, EdgeLoopArea, AreaType, Edge
from Data.Edges import EdgeType
from Data.Events import ChangeEvent
from Data.Objects import IdObject, NamedObservableObject
from Data.Parameters import Parameters
from Data.Point3d import KeyPoint


class TransformerType(Enum):
	Overlap = 0
	Evolvente = 1


class Transformer(IdObject, Parameters):
	def __init__(self, sketch, type=TransformerType.Overlap, name="New transformation"):
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
		pass

	def generate_edge(self, edge):
		pass

	def generate_area(self, area):
		pass

	def generate_all(self):

			self._lookups_kps.append({})
			self._lookups_edges.append({})
			self._lookups_areas.append({})

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
		transformer = Transformer(parent)
		if data is not None:
			transformer.deserialize_data(data)
		return transformer

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		NamedObservableObject.deserialize_data(self, data['no'])
		self._type = TransformerType(data['type'])
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


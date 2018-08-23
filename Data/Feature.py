from enum import Enum
from math import pi

from Data.Events import *
from Data.Objects import *
from Data.Vertex import Vertex


class FeatureType(Enum):
	ExtrudeFeature = 0
	RevolveFeature = 1
	FilletFeature = 2
	PlaneFeature = 3
	SketchFeature = 4
	NurbsSurfaceFeature = 5


class Feature(NamedObservableObject, IdObject):
	AddOperation = 0
	SubtractOperation = 1
	DifferenceOperation = 2

	Forward = 0
	Backward = 1
	Both = 2

	def __init__(self, document, feature_parent, feature_type=FeatureType.ExtrudeFeature, name="new feature"):
		IdObject.__init__(self)
		NamedObservableObject.__init__(self, name)
		self._doc = document
		self._feature_parent = feature_parent
		if type(feature_type) is not FeatureType:
			raise TypeError("feature type must be FeatureType")
		self._feature_type = feature_type
		self._vertexes = {}
		self._edge_uids = []
		self._order_items = []
		self._feature_uids = []
		self._area_uids = []
		self._sketch_uids = []
		self._axis_uids = []

		self._operation_type = Feature.AddOperation
		self.add_change_handler(self.on_value_changed)

	def on_value_changed(self, event):
		if event.type == ChangeEvent.ValueChanged:
			if event.object == 'name':
				if self._feature_type == FeatureType.SketchFeature:
					self.get_objects()[0].name = self.name

	def get_feature_parent(self):
		return self._feature_parent

	@property
	def distance(self):
		if self._feature_type == FeatureType.ExtrudeFeature:
			return "[%.6f,%.6f]" % (round(self._vertexes['ex_ls'].x, 6), round(self._vertexes['ex_ls'].y, 6))
		if self._feature_type == FeatureType.RevolveFeature:
			return [round(self._vertexes['ex_ls'].x * 180 / pi, 2), round(self._vertexes['ex_ls'].y * 180 / pi, 2)]
		return None

	@distance.setter
	def distance(self, value):
		if self._feature_type == FeatureType.ExtrudeFeature:
			if type(value) is str:
				value = eval(value)
			self._vertexes['ex_ls'].x = value[0]
			self._vertexes['ex_ls'].y = value[1]
		else:
			self._vertexes['ex_ls'].x = value[0] * pi / 180
			self._vertexes['ex_ls'].y = value[1] * pi / 180
		self.changed(ValueChangeEvent(self, 'distance', None, value))

	def get_order_items(self):
		return self._order_items

	@property
	def plane(self):
		return self.get_features()[0]

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def add_vertex(self, key, vertex):
		self._vertexes[key] = vertex

	def get_vertex(self, key):
		if key in self._vertexes:
			return self._vertexes[key]
		return None

	def add_axis(self, axis):
		self._axis_uids.append(axis.uid)
		axis.add_change_handler(self.on_axis_changed)

	def add_edge(self, edge):
		self._edge_uids.append(edge.uid)
		edge.add_change_handler(self.on_edge_changed)

	def add_area(self, area):
		self._area_uids.append(area.uid)
		area.add_change_handler(self.on_area_changed)

	def add_sketch(self, sketch):
		self._sketch_uids.append(sketch.uid)
		sketch.add_change_handler(self.on_sketch_changed)

	def add_feature(self, feature):
		self._feature_uids.append(feature.uid)
		feature.add_change_handler(self.on_feature_changed)

	def get_features(self):
		features = []
		for uid in self._feature_uids:
			feature = self._feature_parent.get_feature(uid)
			features.append(feature)
		return features

	def get_sketches(self):
		sketches = []
		for uid in self._sketch_uids:
			sketches.append(self._feature_parent.get_sketch(uid))
		return sketches

	def get_areas(self):
		areas = []
		for uid in self._area_uids:
			areas.append(self._feature_parent.get_area(uid))
		return areas

	def get_axes(self):
		axes = []
		for uid in self._axis_uids:
			axes.append(self._feature_parent.document.get_axes()[uid])
		return axes

	def add_order_item(self, item):
		self._order_items.append(item)

	@property
	def feature_type(self):
		return self._feature_type

	def on_axis_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def on_edge_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def on_area_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def on_sketch_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def on_feature_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
			self._feature_uids.remove(event.sender.uid)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
			self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))
		else:
			self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'name': NamedObservableObject.serialize_json(self),
			'edges': self._edge_uids,
			'areas': self._area_uids,
			'sketches': self._sketch_uids,
			'vertexes': self._vertexes,
			'axes': self._axis_uids,
			'type': self._feature_type.value,
			'features': self._feature_uids,
			'order_items': self._order_items
		}

	@staticmethod
	def deserialize(data, feature_parent, document):
		feature = Feature(document, feature_parent)
		if data is not None:
			feature.deserialize_data(data, feature_parent)
		return feature

	def deserialize_data(self, data, feature_parent):
		IdObject.deserialize_data(self, data['uid'])
		NamedObservableObject.deserialize_data(self, data['name'])
		self._order_items = data.get('order_items', [])
		self._feature_type = FeatureType(data['type'])
		for vertex_data_tuple in data.get('vertexes', {}).items():
			vertex_data = vertex_data_tuple[1]
			vertex = Vertex.deserialize(vertex_data)
			self._vertexes[vertex_data_tuple[0]] = vertex

		self._edge_uids = data.get('edges', [])
		self._area_uids = data.get('areas', [])
		self._sketch_uids = data.get('sketches', [])
		self._feature_uids = data.get('features', [])
		self._axis_uids = data.get('axes', [])

		self._doc.add_late_init_object(self)

	def late_init(self):
		for edges_uid in self._edge_uids:
			edge = self._feature_parent.get_edge(edges_uid)
			edge.add_change_handler(self.on_edge_changed)
		for area_uid in self._area_uids:
			area = self._feature_parent.get_area(area_uid)
			area.add_change_handler(self.on_area_changed)
		for sketch_uid in self._sketch_uids:
			sketch = self._feature_parent.get_sketch(sketch_uid)
			sketch.add_change_handler(self.on_sketch_changed)
		for feature_uid in self._feature_uids:
			feature = self._feature_parent.get_feature(feature_uid)
			feature.add_change_handler(self.on_feature_changed)
		return
		# if len(self._feature_objects_late_bind) > 0:
		# 	if self._feature_type == FeatureType.RevolveFeature:
		# 		area_uid = self._feature_objects_late_bind[0]
		# 		axis_uid = self._feature_objects_late_bind[1]
		# 		area_object = None
		# 		axis_object = None
		# 		for sketch in self._feature_parent.get_sketches():  # self._doc.get_geometries().get_sketches():
		# 			area_object = sketch.get_area(area_uid)
		# 			if area_object is not None:
		# 				break
		# 		if area_object is not None:
		# 			self.add_object(area_object)
		# 		if axis_uid in self._doc.get_axes():
		# 			axis_object = self._doc.get_axes()[axis_uid]
		# 		if axis_object is not None:
		# 			self.add_object(axis_object)
		#
		# 	for feature_object_uid in self._feature_objects_late_bind:
		# 		feature_object = None
		# 		if self._feature_type == FeatureType.SketchFeature:
		# 			feature_object = self._feature_parent.get_sketch(
		# 				feature_object_uid)  # self._doc.get_geometries().get_geometry(feature_object_uid)
		# 		if self._feature_type == FeatureType.ExtrudeFeature or self._feature_type == FeatureType.RevolveFeature:
		# 			for sketch in self._doc.get_geometries().get_sketches():
		# 				feature_object = sketch.get_area(feature_object_uid)
		# 				if feature_object is not None:
		# 					break
		# 		if feature_object is not None:
		# 			self.add_object(feature_object)
		# 			feature_object.add_change_handler(self.on_object_changed)
		# 	self._feature_objects_late_bind.clear()
from Data.Areas import *
from Data.Edges import *
from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Geometry import Geometry
from Data.Objects import IdObject, ObservableObject
from Data.Parameters import Parameters, ParametersInstance
from Data.Point3d import KeyPoint

__author__ = 'mamj'


class Sketch(Geometry):
	def __init__(self, params_parent):
		Geometry.__init__(self, params_parent, "New Sketch", Geometry.Sketch)
		self._key_points = {}
		self._edges = {}
		self._texts = {}
		self._areas = {}
		self._sketch_instances = {}
		self._patterns = []
		self.threshold = 0.1
		self.edge_naming_index = 1

	def add_edge(self, edge):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, edge))
		self._edges[edge.uid] = edge
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, edge))
		edge.add_change_handler(self.on_edge_changed)

	def clear(self):
		self._key_points.clear()
		self._edges.clear()
		self._areas.clear()
		self.edge_naming_index = 1
		self.changed(ChangeEvent(self, ChangeEvent.Cleared, self))

	def get_limits(self):
		limits = [1.0e16, 1.0e16, -1.0e16, -1.0e16]
		for pnt in self._key_points.values():
			limits[0] = min(pnt.x, limits[0])
			limits[1] = min(pnt.y, limits[1])
			limits[2] = max(pnt.x, limits[2])
			limits[3] = max(pnt.y, limits[3])
		return limits

	@property
	def key_point_count(self):
		return len(self._key_points)

	@property
	def edges_count(self):
		return len(self._edges)

	@property
	def sketch_instances(self):
		return self._sketch_instances.values()

	def get_sketch(self, uid):
		return self.parent.get_sketch(uid)

	def get_edge(self, uid):
		if uid in self._edges:
			return self._edges[uid]
		else:
			return None

	def get_edge_by_name(self, name):
		for edge in self._edges.items():
			if edge[1].name == name:
				return edge[1]
		return None

	def get_keypoint(self, uid):
		try:
			return self._key_points[uid]
		except KeyError:
			return KeyPoint(self)

	def get_area(self, uid):
		if uid in self._areas:
			return self._areas[uid]
		return None

	def get_areas(self):
		return self._areas.values()

	def get_fillet(self, uid):
		if uid in self._fillets:
			return self._fillets[uid]
		else:
			return None

	def get_parent(self):
		return self._parent

	def get_next_edge_naming_index(self):
		self.edge_naming_index += 1
		return self.edge_naming_index - 1

	def remove_areas(self, areas):
		for area in areas:
			if area.uid in self._areas:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, area))
				self._areas.pop(area.uid)
				area.changed(ChangeEvent(self, ChangeEvent.Deleted, area))
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, area))

	def remove_edge(self, edge):
		if edge.uid in self._edges:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, edge))
			self._edges.pop(edge.uid)
			edge.changed(ChangeEvent(self, ChangeEvent.Deleted, edge))
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, edge))

	def remove_edges(self, edges):
		for edge in edges:
			self.remove_edge(edge)

	def remove_key_points(self, key_points):
		for kp in key_points:
			if kp.uid in self._key_points:
				kp.changed(ChangeEvent(self, ChangeEvent.Deleted, kp))
				self._key_points.pop(kp.uid)

	def get_keypoint_by_location(self, x, y, z, ts=None):
		key_point = None
		for p_tuple in self._key_points.items():
			p = p_tuple[1]
			if ts is None:
				ts = self.threshold
			if abs(p.x - x) < ts and abs(p.y - y) < ts and abs(p.z - z) < ts:
				key_point = p
				break
		return key_point

	def create_keypoint(self, x, y, z):
		key_point = KeyPoint(self, x, y, z)
		self.add_keypoint(key_point)
		return key_point

	def add_keypoint(self, key_point):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, key_point))
		self._key_points[key_point.uid] = key_point
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, key_point))
		key_point.add_change_handler(self.on_kp_changed)

	def create_sketch_instance(self, sketch_to_insert, kp):
		sketch_instance = SketchInstance(self, sketch_to_insert.name)
		sketch_instance.sketch = sketch_to_insert
		sketch_instance.offset = kp
		self._sketch_instances[sketch_instance.uid] = sketch_instance
		return sketch_instance

	def create_circle_edge(self, kp, radius_param):
		circle_edge = None
		if kp.uid in self._key_points:
			circle_edge = Edge(self, EdgeType.CircleEdge)
			circle_edge.name = "Edge" + str(self.edge_naming_index)
			circle_edge.add_key_point(kp)
			circle_edge.set_meta_data('r', radius_param.value)
			circle_edge.set_meta_data_parameter('r', radius_param)
			self.edge_naming_index += 1
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, circle_edge))
			self._edges[circle_edge.uid] = circle_edge
			self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, circle_edge))
			circle_edge.add_change_handler(self.on_edge_changed)
		return circle_edge

	def create_fillet_edge(self, kp, radius_param):
		fillet_edge = None
		if kp.uid in self._key_points:
			fillet_edge = Edge(self, EdgeType.FilletLineEdge)
			fillet_edge.name = "Edge" + str(self.edge_naming_index)
			fillet_edge.add_key_point(kp)
			fillet_edge.set_meta_data('r', radius_param.value)
			fillet_edge.set_meta_data_parameter('r', radius_param)
			self.edge_naming_index += 1
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, fillet_edge))
			self._edges[fillet_edge.uid] = fillet_edge
			self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, fillet_edge))
			fillet_edge.add_change_handler(self.on_edge_changed)
			for area_tuple in self._areas.items():
				area = area_tuple[1]
				if area.type == AreaType.EdgeLoop:
					kps = area.get_key_points()
					if kp in kps:
						area.add_edge(fillet_edge)
		return fillet_edge

	def create_nurbs_edge(self, kp):
		nurbs_edge = None
		if kp.uid in self._key_points:
			nurbs_edge = Edge(self, EdgeType.NurbsEdge)
			nurbs_edge.name = "Edge" + str(self.edge_naming_index)
			nurbs_edge.add_key_point(kp)
			self.edge_naming_index += 1
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, nurbs_edge))
			self._edges[nurbs_edge.uid] = nurbs_edge
			self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, nurbs_edge))
			nurbs_edge.add_change_handler(self.on_edge_changed)
		return nurbs_edge

	def create_text(self, key_point, value, height):
		text = Text(self, key_point, value, height)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, text))
		self._texts[text.uid] = text
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, text))
		text.add_change_handler(self.on_text_changed)
		return text

	def create_attribute(self, kp, name, default_value, height):
		attribute = Attribute(self, kp, name, default_value, height)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, attribute))
		self._texts[attribute.uid] = attribute
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, attribute))
		attribute.add_change_handler(self.on_text_changed)
		return attribute

	def create_line_edge(self, key_point1, key_point2):
		line_edge = Edge(self, EdgeType.LineEdge)
		line_edge.name = "Edge" + str(self.edge_naming_index)
		self.edge_naming_index += 1
		line_edge.add_key_point(key_point1)
		line_edge.add_key_point(key_point2)
		self.add_edge(line_edge)
		return line_edge

	def create_arc_edge(self, center_key_point, start_angle, end_angle, radius):
		arc_edge = Edge(self, EdgeType.ArcEdge)
		arc_edge.name = "Edge" + str(self.edge_naming_index)
		self.edge_naming_index += 1
		arc_edge.add_key_point(center_key_point)
		arc_edge.set_meta_data("sa", start_angle)
		arc_edge.set_meta_data("ea", end_angle)
		arc_edge.set_meta_data("r", radius)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, arc_edge))
		self._edges[arc_edge.uid] = arc_edge
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, arc_edge))
		arc_edge.add_change_handler(self.on_edge_changed)
		return arc_edge

	def get_new_unique_area_name(self, name):
		unique = False
		counter = 1
		new_name = name
		while not unique:
			found = False
			for area_tuple in self._areas.items():
				if area_tuple[1].name == new_name:
					found = True
					new_name = name + str(counter)
					counter += 1
			if not found:
				unique = True
		return new_name

	def create_area(self):
		area = EdgeLoopArea(self)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, area))
		self._areas[area.uid] = area
		area.name = self.get_new_unique_area_name("New Area")
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, area))
		area.add_change_handler(self.on_area_changed)
		return area

	def create_composite_area(self):
		area = CompositeArea(self)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, area))
		self._areas[area.uid] = area
		area.name = self.get_new_unique_area_name("New Area")
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, area))
		area.add_change_handler(self.on_area_changed)
		return area

	def get_edges(self):
		return self._edges.values()

	def get_key_points(self):
		return self._key_points.values()

	def get_texts(self):
		return self._texts.values()

	def clear_areas(self):
		areas_to_delete = []
		for area_tuple in self._areas.items():
			areas_to_delete.append(area_tuple[1])

		for area in areas_to_delete:
			area.delete()

	def on_kp_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
		if event.type == ChangeEvent.Deleted:
			if event.sender.uid in self._key_points:
				self._key_points.pop(event.sender.uid)

	def on_text_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def on_edge_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			if event.object.uid in self._edges:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
				self._edges.pop(event.object.uid)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
			event.object.remove_change_handler(self.on_edge_changed)

	def on_area_changed(self, event: ChangeEvent):
		if event.type == ChangeEvent.Deleted:
			if event.object.uid in self._areas:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
				self._areas.pop(event.object.uid)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
			event.object.remove_change_handler(self.on_area_changed)

	def on_sketch_instance_changed(self, event: ChangeEvent):
		if event.type == ChangeEvent.Deleted:
			if event.object.uid in self._sketch_instances:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
				self._sketch_instances.pop(event.object.uid)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
			event.object.remove_change_handler(self.on_sketch_instance_changed)

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'parameters': Parameters.serialize_json(self),
			'key_points': self._key_points,
			'edges': self._edges,
			'areas': self._areas,
			'texts': self._texts,
			'instances': self._sketch_instances,
			'threshold': self.threshold,
			'edge_naming_index': self.edge_naming_index,
			'type': self._geometry_type
		}

	@staticmethod
	def deserialize(data, param_parent):
		sketch = Sketch(param_parent)
		if data is not None:
			sketch.deserialize_data(data)
		return sketch

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		Parameters.deserialize_data(self, data['parameters'])
		self.threshold = data.get('threshold', 0.1)
		self.edge_naming_index = data.get('edge_naming_index', 0)
		for kp_data_tuple in data.get('key_points', {}).items():
			kp_data = kp_data_tuple[1]
			kp = KeyPoint.deserialize(kp_data, self)
			self._key_points[kp.uid] = kp
			kp.add_change_handler(self.on_kp_changed)
		for edge_data_tuple in data.get('edges', {}).items():
			edge_data = edge_data_tuple[1]
			edge = Edge.deserialize(self, edge_data)
			self._edges[edge.uid] = edge
			edge.add_change_handler(self.on_edge_changed)
		for text_data_tuple in data.get('texts', {}).items():
			text_data = text_data_tuple[1]
			text_type = text_data.get('type', Text.SimpleTextType)
			if text_type == Text.SimpleTextType:
				text = Text.deserialize(self, text_data)
			elif text_type == Text.AttributeType:
				text = Attribute.deserialize(self, text_data)
			self._texts[text.uid] = text
			text.add_change_handler(self.on_text_changed)

		for area_data_tuple in data.get('areas', {}).items():
			area_data = area_data_tuple[1]
			area = Area.deserialize(area_data, self)
			self._areas[area.uid] = area
			area.add_change_handler(self.on_area_changed)

		for sketch_instance_tuple in data.get('instances', {}).items():
			sketch_instance_data = sketch_instance_tuple[1]
			sketch_instance = SketchInstance.deserialize(self, sketch_instance_data)
			self._sketch_instances[sketch_instance.uid] = sketch_instance
			sketch_instance.add_change_handler(self.on_sketch_instance_changed)

		if self.edge_naming_index == 0:
			for edge_tuple in self._edges.items():
				edge = edge_tuple[1]
				if "Edge" in edge.name:
					try:
						index = int(edge.name.replace("Edge", ""))
						self.edge_naming_index = max(self.edge_naming_index, index)
					except ValueError:
						pass
			self.edge_naming_index += 1


class Text(IdObject, ObservableObject):
	Bottom = 0
	Top = 1
	Center = 2
	Left = 0
	Right = 1
	SimpleTextType = 0
	AttributeType = 1

	def __init__(self, sketch, key_point=None, value="", height=0.01, angle=0, vertical_alignment=Center,
							 horizontal_alignment=Center):
		IdObject.__init__(self)
		ObservableObject.__init__(self)
		self._sketch = sketch
		self._vertical_alignment = vertical_alignment
		self._horizontal_alignment = horizontal_alignment
		self._value = value
		self._height = height
		self._angle = angle
		self._key_point = key_point

	@property
	def text_type(self):
		return Text.SimpleTextType

	@property
	def name(self):
		return self._value

	@property
	def key_point(self):
		return self._key_point

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, value):
		old_value = self._value
		self._value = value
		self.changed(ValueChangeEvent(self, 'value', old_value, value))

	@property
	def vertical_alignment(self):
		return self._vertical_alignment

	@vertical_alignment.setter
	def vertical_alignment(self, value):
		self._vertical_alignment = value
		self.changed(ValueChangeEvent(self, 'vertical_alignment', 0, value))

	@property
	def horizontal_alignment(self):
		return self._horizontal_alignment

	@horizontal_alignment.setter
	def horizontal_alignment(self, value):
		self._horizontal_alignment = value
		self.changed(ValueChangeEvent(self, 'horizontal_alignment', 0, value))

	@property
	def height(self):
		return self._height

	@height.setter
	def height(self, value):
		old_value = self._height
		self._height = value
		self.changed(ValueChangeEvent(self, 'height', old_value, value))

	@property
	def angle(self):
		return self._angle

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'kp': self._key_point.uid,
			'value': self._value,
			'height': self._height,
			'angle': self._angle,
			'valign': self._vertical_alignment,
			'halign': self._horizontal_alignment,
			'type': self.text_type
		}

	@staticmethod
	def deserialize(sketch, data):
		text = Text(sketch)
		if data is not None:
			text.deserialize_data(data)
		return text

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		self._key_point = self._sketch.get_keypoint(data['kp'])
		self._value = data['value']
		self._height = data['height']
		self._angle = data['angle']
		self._vertical_alignment = data['valign']
		self._horizontal_alignment = data['halign']


class Attribute(Text):
	def __init__(self, sketch, key_point=None, name="Attribute name", default_value="Default value", height=0.01):
		Text.__init__(self, sketch, key_point, default_value, height)
		self._name = name

	@property
	def text_type(self):
		return Text.AttributeType

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		old_value = self._name
		self._name = name
		self.changed(ValueChangeEvent(self, "name", old_value, name))

	def serialize_json(self):
		return {
			'text': Text.serialize_json(self),
			'name': self._name,
			'type': self.text_type
		}

	@staticmethod
	def deserialize(param_parent, data):
		att = Attribute(param_parent)
		if data is not None:
			att.deserialize_data(data)
		return att

	def deserialize_data(self, data):
		Text.deserialize_data(self, data['text'])
		self._name = data['name']


class PatternType(Enum):
	Circular = 0
	Diamond = 1
	Triangular = 2
	Square = 3
	Rectangular = 4


class Pattern(IdObject, NamedObservableObject):
	def __init__(self, sketch, type=PatternType.Circular, name="New pattern"):
		IdObject.__init__(self)
		NamedObservableObject.__init__(self, name)
		self._sketch = sketch
		self._type = type
		self._kps = []
		self._edges = []
		self._areas = []


class SketchInstance(ParametersInstance):
	def __init__(self, parent, name="New sketch instance"):
		ParametersInstance.__init__(self, name)
		self._parent = parent
		self._sketch = None
		self._offset = None
		self._scale = 1.0

	@property
	def sketch(self):
		if type(self._sketch) is not Sketch:
			self._sketch = self._parent.get_sketch(self._sketch)
			self._parameters = self._sketch
			self._current_standard_name = self._parameters.standard
			self._current_type_name = self._parameters.type
		return self._sketch

	@sketch.setter
	def sketch(self, value):
		self._sketch = value
		self._parameters = value

	@property
	def offset(self):
		if type(self._offset) is not KeyPoint:
			self._offset = self._parent.get_keypoint(self._offset)
		return self._offset

	@offset.setter
	def offset(self, value):
		self._offset = value

	@property
	def scale(self):
		return self._scale

	@scale.setter
	def scale(self, value):
		self._scale = value

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'no': NamedObservableObject.serialize_json(self),
			'sketch': self.sketch.uid,
			'offset': self.offset.uid,
			'scale': self._scale,
			'csn': self._current_standard_name,
			'ctn': self._current_type_name
		}

	@staticmethod
	def deserialize(parent, data):
		sketch_instance = SketchInstance(parent)
		if data is not None:
			sketch_instance.deserialize_data(data)
		return sketch_instance

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		NamedObservableObject.deserialize_data(self, data['no'])
		self._sketch = data['sketch']
		self._offset = data['offset']
		self._scale = data['scale']
		self._current_standard_name = data.get("csn", self._current_standard_name)
		self._current_type_name = data.get("ctn", self._current_type_name)

from enum import Enum

from Data.Paper import *
from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Objects import ObservableObject, NamedObservableObject
from Data.Parameters import Parameters
from Data.Plane import Plane
from Data.Sketch import Sketch
from Data.Vertex import Vertex


class Drawings(ObservableObject):
	def __init__(self, document):
		ObservableObject.__init__(self)
		self._headers = []
		self._borders = []
		self._drawings = []
		self._doc = document

	def create_header(self):
		header = Sketch(self._doc)
		header.name = "New Header"
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, header))
		self._doc.get_geometries().add_geometry(header)
		self._headers.append(header)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, header))
		return header

	def create_drawing(self, size, name, header, orientation):
		drawing = Drawing(self._doc, size, name, header, orientation)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, drawing))
		self._drawings.append(drawing)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, drawing))
		drawing.add_change_handler(self.drawing_changed)
		return drawing

	def get_headers(self):
		return list(self._headers)

	@property
	def name(self):
		return "Drawings"

	@property
	def items(self):
		return list(self._drawings)

	@property
	def length(self):
		return len(self._drawings)

	@property
	def item(self, index):
		return self._drawings[index]

	def get_header_uids(self):
		uids = []
		for header in self._headers:
			uids.append(header.uid)
		return uids

	def serialize_json(self):
		return {
			'headers': self.get_header_uids(),
			'drawings': self._drawings
		}

	def drawing_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
		if event.type == ChangeEvent.Deleted:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
			if type(event.sender) is Drawing:
				self._drawings.remove(event.sender)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))

	@staticmethod
	def deserialize(data, document):
		drawings = Drawings(document)
		if data is not None:
			drawings.deserialize_data(data)
		return drawings

	def deserialize_data(self, data):
		for uid in data['headers']:
			header = self._doc.get_geometries().get_geometry(uid)
			self._headers.append(header)
		for dwg_data in data['drawings']:
			drawing = Drawing.deserialize(dwg_data, self._doc)
			self._drawings.append(drawing)
			drawing.add_change_handler(self.drawing_changed)


class Drawing(Paper, Parameters):
	def __init__(self, document, size=[1, 1], name="New Drawing", header=None, orientation=Paper.Landscape):
		Paper.__init__(self, size, orientation)
		Parameters.__init__(self, name, document.get_parameters())
		self._doc = document
		self._views = []
		self._border_sketch = Sketch(self)
		self._header_sketch = header
		self._margins = [0.02, 0.02, 0.02, 0.02]
		self._fields = {}
		self.generate_border()
		Paper.add_change_handler(self, self.on_paper_changed)

	def on_paper_changed(self, event):
		if event.object is not None:
			if hasattr(event.object, '__iter__'):
				if "name" in event.object:
					if event.object['name'] == "margins" or event.object['name'] == "size":
						print("paper changed")
						self.generate_border()

	@property
	def document(self):
		return self._doc

	@property
	def header_sketch(self):
		return self._header_sketch

	@property
	def header(self):
		return self._header_sketch.name

	@property
	def border_sketch(self):
		return self._border_sketch

	def generate_border(self):
		alpha = "ABCDEFGHIJKLMNOP"
		sketch = self._border_sketch
		sketch.clear()
		self._doc.styles.get_edge_style_by_name("border").thickness = 0.0005
		m = self._margins
		sz = self.size
		border_width = sz[0] - m[0] - m[2]
		max_len = 0.1
		divisions = round(border_width / max_len)
		length = border_width / divisions

		pnt1 = sketch.create_keypoint(m[0], m[3], 0)
		pnt2 = sketch.create_keypoint(sz[0] - m[2], m[3], 0)
		pnt3 = sketch.create_keypoint(sz[0] - m[2], sz[1] - m[1], 0)
		pnt4 = sketch.create_keypoint(m[0], sz[1] - m[1], 0)

		sketch.create_line_edge(pnt1, pnt2).style_name = "border"
		sketch.create_line_edge(pnt2, pnt3).style_name = "border"
		sketch.create_line_edge(pnt3, pnt4).style_name = "border"
		sketch.create_line_edge(pnt4, pnt1).style_name = "border"

		for i in range(0, divisions):
			tkp = sketch.create_keypoint(m[0] + (i + 0.5) * length , 2 * m[3] / 3, 0)
			sketch.create_text(tkp, alpha[i], 0.005)
			tkp = sketch.create_keypoint(m[0] + (i + 0.5) * length,sz[1] - 2 * m[1] / 3, 0)
			sketch.create_text(tkp, alpha[i], 0.005)
			if i > 0:
				pnt1 = sketch.create_keypoint(m[0]  + i * length ,  m[3], 0)
				pnt2 = sketch.create_keypoint(m[0] + i * length , m[3] / 2, 0)
				sketch.create_line_edge(pnt1, pnt2).style_name = "border"
				pnt1 = sketch.create_keypoint(m[0] + i * length , sz[1] - m[1], 0)
				pnt2 = sketch.create_keypoint(m[0] + i * length , sz[1] - m[1] / 2, 0)
				sketch.create_line_edge(pnt1, pnt2).style_name = "border"

		border_height = sz[1] - m[1] - m[3]
		divisions = round(border_height / max_len)
		length = border_height / divisions
		for i in range(0, divisions):
			tkp = sketch.create_keypoint(2 * m[0] / 3, m[3] + (i + 0.5) * length, 0)
			sketch.create_text(tkp, str(i+1), 0.005)
			tkp = sketch.create_keypoint(sz[0] - 2 * m[2] / 3, m[3] + (i + 0.5) * length, 0)
			sketch.create_text(tkp, str(i+1), 0.005)
			if i > 0:
				pnt1 = sketch.create_keypoint(m[0], m[3] + i * length, 0)
				pnt2 = sketch.create_keypoint(m[0] / 2, m[3] + i * length, 0)
				sketch.create_line_edge(pnt1, pnt2).style_name = "border"
				pnt1 = sketch.create_keypoint(sz[0] - m[2], m[3] + i * length, 0)
				pnt2 = sketch.create_keypoint(sz[0] - m[2] / 2, m[3] + i * length, 0)
				sketch.create_line_edge(pnt1, pnt2).style_name = "border"

	def create_sketch_view(self, sketch, scale, offset):
		view = SketchView(self, sketch, scale, offset)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, view))
		self._views.append(view)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, view))
		view.add_change_handler(self.on_view_changed)
		return view

	def create_part_view(self, part, scale, offset):
		view = PartView(self, part, scale, offset)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, view))
		self._views.append(view)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, view))
		view.add_change_handler(self.on_view_changed)
		return view

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def add_field(self, name, value):
		field = Field(name, value)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, field))
		self._fields[name] = field
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, field))
		field.add_change_handler(self.on_field_changed)

	def get_field(self, name):
		if name in self._fields:
			return self._fields[name]
		else:
			return None

	def get_fields(self):
		return dict(self._fields)

	def get_views(self):
		return list(self._views)

	def on_view_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
		if event.type == ChangeEvent.Deleted:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
			self._views.remove(event.sender)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
			event.sender.remove_change_handler(self.on_view_changed)

	def on_field_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
		if event.object == "name":
			self._fields.pop(event.old_value)
			self._fields[event.sender.name] = event.sender

	def serialize_json(self):
		print("test")
		return {
			'paper': Paper.serialize_json(self),
			'name': self._name,
			'views': self._views,
			'border_sketch': self._border_sketch,
			'header_sketch': self._header_sketch.uid,
			'fields': self._fields
		}

	@staticmethod
	def deserialize(data, document):
		drawing = Drawing(document)
		if data is not None:
			drawing.deserialize_data(data)
		return drawing

	def deserialize_data(self, data):
		Paper.deserialize_data(self, data['paper'])
		self._name = data.get('name', "No name")

		self._header_sketch = self._doc.get_geometries().get_geometry(data['header_sketch'])
		for field_data_tuple in data.get('fields', {}).items():
			field_data = field_data_tuple[1]
			field = Field.deserialize(field_data)
			self._fields[field.name] = field
			field.add_change_handler(self.on_field_changed)
		for view_data in data.get('views', []):
			if view_data['view']['type'] == ViewType.SketchView.value:
				view = SketchView.deserialize(view_data, self)
				self._views.append(view)
				view.add_change_handler(self.on_view_changed)
			if view_data['view']['type'] == ViewType.PartView.value:
				view = PartView.deserialize(view_data, self)
				self._views.append(view)
				view.add_change_handler(self.on_view_changed)
		self.generate_border()


class Field(NamedObservableObject):
	def __init__(self, name="New Field", value="Field Value"):
		NamedObservableObject.__init__(self, name)
		self._value = value

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, value):
		old_value = self._value
		self._value = value
		self.changed(ValueChangeEvent(self, 'value', old_value, value))

	def serialize_json(self):
		return {
			'name': NamedObservableObject.serialize_json(self),
			'value': self.value
		}

	@staticmethod
	def deserialize(data):
		field = Field(data)
		if data is not None:
			field.deserialize_data(data)
		return field

	def deserialize_data(self, data):
		NamedObservableObject.deserialize_data(self, data['name'])
		self._value = data['value']


class ViewType(Enum):
	SketchView = 0
	PartView = 1


class View(NamedObservableObject):
	def __init__(self, drawing, name="New view", scale=1, offset=Vertex()):
		NamedObservableObject.__init__(self, name)
		self._drawing = drawing
		self._offset = offset
		self._scale = float(scale)
		self._view_type = ViewType.SketchView

	@property
	def view_type(self):
		return self._view_type

	@property
	def limits(self):
		return [0.0, 0.0, 0.0, 0.0]

	@property
	def scale(self):
		return self._scale

	@scale.setter
	def scale(self, value):
		old_value = self._scale
		self._scale = value
		self.changed(ValueChangeEvent(self, 'scale', old_value, value))

	@property
	def scale_name(self):
		if self._scale < 1:
			return "1 : " + str(1 / self._scale)
		else:
			return str(1 / self._scale) + " : 1"

	@scale_name.setter
	def scale_name(self, value):
		values = value.split(":")
		if len(values) == 2:
			self._scale = float(values[0]) / float(values[1])

	@property
	def offset(self):
		return self._offset

	@property
	def offset_values(self):
		return self._offset.xyz

	def serialize_json(self):
		return {
			'no': NamedObservableObject.serialize_json(self),
			'scale': self._scale,
			'offset': self._offset,
			'type': self._view_type.value
		}

	def deserialize_data(self, data):
		NamedObservableObject.deserialize_data(self, data['no'])
		self._scale = data['scale']
		self._offset = Vertex.deserialize(data['offset'])


class SketchView(View):
	def __init__(self, drawing, sketch=None, scale=1, offset=Vertex()):
		View.__init__(self, drawing, "New View", scale, offset)
		self._sketch = sketch
		self._view_type = ViewType.SketchView
		if sketch is not None:
			self._name = sketch.name
			self._sketch.add_change_handler(self.on_sketch_changed)

	@property
	def sketch(self):
		return self._sketch

	@property
	def limits(self):
		if self._sketch is not None:
			return self._sketch.get_limits()
		return super.limits

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def on_sketch_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self._sketch))

	def serialize_json(self):
		return {
			'view': View.serialize_json(self),
			'sketch': self._sketch.uid,
		}

	@staticmethod
	def deserialize(data, drawing):
		sketch_view = SketchView(drawing)
		if data is not None:
			sketch_view.deserialize_data(data)
		return sketch_view

	def deserialize_data(self, data):
		document = self._drawing.document
		View.deserialize_data(self, data['view'])
		self._sketch = document.get_geometries().get_geometry(data['sketch'])
		self._sketch.add_change_handler(self.on_sketch_changed)


class PartView(View):
	def __init__(self, drawing, part=None, scale=1, offset=Vertex()):
		View.__init__(self, drawing, "New View", scale, offset)
		self._part = part
		self._view_type = ViewType.PartView
		self._sketch = Sketch(None, drawing.document)
		if part is not None:
			self._name = part.name
			self._part.add_change_handler(self.on_part_changed)
			self.update_sketch()

	@property
	def sketch(self):
		return self._sketch

	@property
	def part(self):
		return self._part

	def update_sketch(self):
		if self._part.update_needed:
			self._part.update_geometry()
		section_datas = []
		if self._part is not None:
			self._sketch.clear()
			for surface in self._part.get_surfaces():
				plane = Plane()
				section_data = surface.get_section_by_plane(plane)
				if section_data is not None:
					section_datas.append(section_data)
			for section_data in section_datas:
				coords = section_data['coords']
				if len(coords) > 2:
					kp1 = self._sketch.create_key_point(coords[0][0], coords[0][1], coords[0][2])
					for i in range(1, len(coords)):
						kp2 = self._sketch.create_key_point(coords[i][0], coords[i][1], coords[i][2])
						self._sketch.create_line_edge(kp1, kp2)
						kp1 = kp2
			self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self))

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def on_part_changed(self, event):
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self._part))
		self.update_sketch()

	def serialize_json(self):
		return {
			'view': View.serialize_json(self),
			'part': self._part.uid
		}

	@staticmethod
	def deserialize(data, document):
		part_view = PartView()
		if data is not None:
			part_view.deserialize_data(data, document)
		return part_view

	def deserialize_data(self, data):
		doc = self._drawing.document
		View.deserialize_data(self, data['view'])
		self._part = doc.get_geometries().get_geometry(data['part'])
		self._part.add_change_handler(self.on_part_changed)
		self.update_sketch()

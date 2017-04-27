from Data.Paper import *
from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Objects import ObservableObject, NamedObservableObject
from Data.Parameters import Parameters
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
        header = Sketch(self._doc.get_parameters(), self._doc)
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
    def __init__(self, document, size=[1, 1], name="New Drawing", header=[0, 0, 0, 0], orientation=Paper.Landscape):
        Paper.__init__(self, size, orientation)
        Parameters.__init__(self, name, document.get_parameters())
        self._doc = document
        self._views = []
        self._border_sketch = None
        self._header_sketch = header
        self._margins = [0.02, 0.02, 0.02, 0.02]
        self._fields = {}

    @property
    def header_sketch(self):
        return self._header_sketch

    @property
    def header(self):
        return self._header_sketch.name

    def create_sketch_view(self, sketch, scale, offset):
        view = SketchView(sketch, scale, offset)
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
        self._border_sketch = data['border_sketch']
        self._header_sketch = self._doc.get_geometries().get_geometry(data['header_sketch'])
        for field_data_tuple in data.get('fields', {}).items():
            field_data = field_data_tuple[1]
            field = Field.deserialize(field_data)
            self._fields[field.name] = field
            field.add_change_handler(self.on_field_changed)
        for view_data in data.get('views', []):
            if view_data.get('type', SketchView) == SketchViewType:
                view = SketchView.deserialize(view_data, self._doc)
                self._views.append(view)
                view.add_change_handler(self.on_view_changed)


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


SketchViewType = 0
PartViewType = 1


class SketchView(NamedObservableObject):
    def __init__(self, sketch=None, scale=1, offset=Vertex()):
        NamedObservableObject.__init__(self, "New view")
        self._sketch = sketch
        self._offset = offset
        self._scale = float(scale)
        if sketch is not None:
            self._name = sketch.name

    @property
    def view_type(self):
        return SketchViewType

    @property
    def sketch(self):
        return self._sketch

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        old_value = self._scale
        self._scale = value
        self.changed(ValueChangeEvent(self,'scale', old_value, value))

    @property
    def offset(self):
        return self._offset

    @property
    def offset_values(self):
        return self._offset.xyz

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def serialize_json(self):
        return {
            'name': NamedObservableObject.serialize_json(self),
            'sketch': self._sketch.uid,
            'offset': self._offset,
            'scale': self._scale,
            'type': self.view_type
        }

    @staticmethod
    def deserialize(data, document):
        sketch_view = SketchView()
        if data is not None:
            sketch_view.deserialize_data(data, document)
        return sketch_view

    def deserialize_data(self, data, document):
        NamedObservableObject.deserialize_data(self, data['name'])
        self._scale = data['scale']
        self._offset = Vertex.deserialize(data['offset'])
        self._sketch = document.get_geometries().get_geometry(data['sketch'])

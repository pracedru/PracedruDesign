from Data.Paper import *
from Data.Events import ChangeEvent
from Data.Objects import ObservableObject
from Data.Parameters import Parameters
from Data.Sketch import Sketch


class Drawings(ObservableObject):
    def __init__(self, document):
        ObservableObject.__init__(self)
        self._headers = []
        self._borders = []
        self._drawings = []
        self._doc = document

    def create_header(self):
        header = Sketch(self._doc.get_parameters())
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, header))
        self._doc.get_geometries().add_geometry(header)
        self._headers.append(header)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, header))

    def create_drawing(self, size):
        drawing = Drawing(self._doc, size)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, drawing))
        self._drawings.append(drawing)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, drawing))
        drawing.add_change_handler(self.drawing_changed)
        return drawing

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

    def serialize_json(self):
        return {
            'drawings': self._drawings
        }

    def drawing_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    @staticmethod
    def deserialize(data, document):
        drawings = Drawings(document)
        if data is not None:
            drawings.deserialize_data(data)
        return drawings

    def deserialize_data(self, data):
        for dwg_data in data['drawings']:
            drawing = Drawing.deserialize(dwg_data, self._doc)
            self._drawings.append(drawing)


class Drawing(Paper, Parameters):
    def __init__(self, document, size=Sizes["A0"]):
        Paper.__init__(self, size)
        Parameters.__init__(self, "New Drawing", document.get_parameters())
        self._doc = document
        self._views = []
        self._border_sketch = None
        self._header_sketch = None
        self._name = "New Drawing"
        self._margins = [0.02, 0.02, 0.02, 0.02]

    @property
    def header_sketch(self):
        return self._header_sketch

    def serialize_json(self):
        return {
            'paper': Paper.serialize_json(self),
            'name': self._name,
            'views': self._views,
            'border_sketch': self._border_sketch,
            'header_sketch': self._header_sketch
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
        self._views = data['views']
        self._border_sketch = Sketch.deserialize(data['border_sketch'], None)
        self._header_sketch = Sketch.deserialize(data['header_sketch'], None)


class SketchView(ObservableObject):
    def __init__(self):
        pass
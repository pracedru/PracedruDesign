from Data import Paper
from Data.Events import ChangeEvent
from Data.Objects import ObservableObject


class Drawings(ObservableObject):
    def __init__(self, document):
        ObservableObject.__init__(self)
        self._drawings = []
        self._doc = document

    def create_drawing(self, size):
        drawing = Drawing(self._doc, size)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, drawing))
        self._drawings.append(drawing)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, drawing))
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


class Drawing(ObservableObject):
    def __init__(self, document, size=Paper.Sizes["A0"]):
        ObservableObject.__init__(self)
        self._size = size
        self._doc = document
        self._views = []

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value


from Data.Events import ChangeEvent
from Data.Objects import ObservableObject

Sizes = {
    "ISO A0": [1.189, .841],
    "ISO A1": [.841, .594],
    "ISO A2": [.594, .420],
    "ISO A3": [.420, .297],
    "ISO A4": [.297, .210],
    "ISO A5": [.210, .148],
    "ANSI E": [1.1176, .8636],
    "ANSI D": [.8636, .5588],
    "ANSI C": [.5588, .4318],
    "ANSI B": [.4318, .2794],
    "ANSI A": [.2794, .2159]
}


class Paper(ObservableObject):
    Landscape = 0
    Portrait = 1

    def __init__(self, size=Sizes["ISO A4"], orientation=Landscape):
        ObservableObject.__init__(self)
        self._size = size
        self._margins = [0.01, 0.01, 0.01, 0.01]
        self._orientation = orientation

    @property
    def size(self):
        if self._orientation == Paper.Landscape:
            return [max(self._size[0], self._size[1]), min(self._size[0], self._size[1])]
        else:
            return [min(self._size[0], self._size[1]), max(self._size[0], self._size[1])]

    @size.setter
    def size(self, value):
        old_value = self._size
        self._size = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged,
                                 {
                                     "name": "size",
                                     'new value': value,
                                     'old value': old_value
                                 }))

    @property
    def margins(self):
        return list(self._margins)

    @margins.setter
    def margins(self, value):
        old_value = self._size
        self._margins = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged,
                                 {
                                     "name": "margins",
                                     'new value': value,
                                     'old value': old_value
                                 }))

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter

    def orientation(self, value):
        old_value = self._orientation
        self._orientation = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged,
                                 {
                                     "name": "margins",
                                     'new value': value,
                                     'old value': old_value
                                 }))

    def serialize_json(self):
        return {
            'size': self._size,
            'margins': self._margins,
            'orientation': self._orientation
        }

    @staticmethod
    def deserialize(data):
        paper= Paper()
        if data is not None:
            paper.deserialize_data(data)
        return paper

    def deserialize_data(self, data):
        self._size = data.get('size', Sizes["ISO A4"])
        self._margins = data.get('margins', [0.01, 0.01, 0.01, 0.01])
        self._orientation = data.get('orientation', Paper.Landscape)

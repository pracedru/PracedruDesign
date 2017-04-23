from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Objects import ObservableObject
from Data.Sketch import Sketch


class Geometries(ObservableObject):
    def __init__(self, document):
        ObservableObject.__init__(self)
        self._doc = document
        self._geometries = {}

    @property
    def name(self):
        return "Geometries"

    def add_geometry(self, geometry: Geometry):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, geometry))
        self._geometries[geometry.uid] = geometry
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, geometry))
        geometry.add_change_handler(self.geometry_changed)

    def geometry_changed(self, event):
        self.changed(ChangeEvent(self, event.type, event.object))
        if event.type == ChangeEvent.Deleted:
            if type(event.object) is Geometry:
                if event.object.uid in self._geometries:
                    self._geometries.pop(event.object.uid)

    def items(self):
        return self._geometries.items()

    def serialize_json(self):
        return {
                'geoms': self._geometries
            }

    @staticmethod
    def deserialize(data, document):
        geometries = Geometries(document)
        geometries.deserialize_data(data, document)
        return geometries

    def deserialize_data(self, data, document):
        for geometry_uid in data['geoms']:
            geometry_data = data['geoms'][geometry_uid]
            geometry = None
            if geometry_data['type'] == Geometry.Sketch:
                geometry = Sketch.deserialize(geometry_data, document)
            if geometry is not None:
                self._geometries[geometry.uid] = geometry
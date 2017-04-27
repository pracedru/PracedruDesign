from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Objects import ObservableObject
from Data.Part import Part
from Data.Sketch import Sketch


class Geometries(ObservableObject):
    def __init__(self, document):
        ObservableObject.__init__(self)
        self._doc = document
        self._geometries = {}
        self._children = []

    @property
    def name(self):
        return "Geometries"

    def add_geometry(self, geometry: Geometry):
        self._geometries[geometry.uid] = geometry
        geometry.add_change_handler(self.geometry_changed)

    def geometry_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if isinstance(event.object, Geometry):
                if event.object.uid in self._geometries:
                    self._geometries.pop(event.object.uid)

    def get_geometry(self, uid):
        if uid in self._geometries:
            return self._geometries[uid]
        return None

    def child_geometry_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if isinstance(event.object, Geometry):
                if event.object in self._children:
                    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
                    self._children.remove(event.object)
                    self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def add_child(self, child_geometry):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, child_geometry))
        self._children.append(child_geometry)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, child_geometry))
        child_geometry.add_change_handler(self.child_geometry_changed)

    def get_sketches(self):
        sketches = []
        for geometry_tuple in self._geometries.items():
            geometry = geometry_tuple[1]
            if type(geometry) is Sketch:
                sketches.append(geometry)
        return sketches

    def get_sketch_by_name(self, name):
        for sketch in self.get_sketches():
            if sketch.name == name:
                return sketch
        return None

    def items(self):
        return self._children

    def _serialize_children(self):
        uids = []
        for geom in self._children:
            uids.append(geom.uid)
        return uids

    def serialize_json(self):
        return {
                'geoms': self._geometries,
                'children': self._serialize_children()
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
                geometry = Sketch.deserialize(geometry_data, document.get_parameters(), document)
            if geometry_data['type'] == Geometry.Part:
                geometry = Part.deserialize(geometry_data, document.get_parameters(), document)
            if geometry is not None:
                self._geometries[geometry.uid] = geometry
        for child_id in data.get("children", []):
            if child_id in self._geometries:
                child = self._geometries[child_id]
                self.add_child(child)
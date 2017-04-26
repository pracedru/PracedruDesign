from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Objects import ObservableObject
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
            if type(event.object) is Geometry:
                if event.object.uid in self._geometries:
                    self._geometries.pop(event.object.uid)

    def get_geometry(self, uid):
        if uid in self._geometries:
            return self._geometries[uid]
        return None

    def child_geometry_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if type(event.object) is Geometry:
                if event.object in self._children:
                    self._children.remove(event.object)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def add_child(self, child_geometry):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, child_geometry))
        self._children.append(child_geometry)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, child_geometry))
        child_geometry.add_change_handler(self.child_geometry_changed)

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
            if geometry is not None:
                self._geometries[geometry.uid] = geometry
        for child_id in data.get("children", []):
            child = self._geometries[child_id]
            self.add_child(child)
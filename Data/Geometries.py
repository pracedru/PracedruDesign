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

  @property
  def name(self):
    return "Geometries"

  def add_geometry(self, geometry: Geometry):
    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, geometry))
    self._geometries[geometry.uid] = geometry
    self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, geometry))
    geometry.add_change_handler(self.geometry_changed)

  def geometry_changed(self, event):
    if event.type == ChangeEvent.Deleted:
      if isinstance(event.object, Geometry):
        if event.object.uid in self._geometries:
          self._geometries.pop(event.object.uid)
    self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

  def get_geometry(self, uid):
    if uid in self._geometries:
      return self._geometries[uid]
    return None


  def get_sketches(self):
    sketches = []
    for geometry in self._geometries.values():
      if type(geometry) is Sketch:
        sketches.append(geometry)
    return sketches

  def get_parts(self):
    parts = []
    for geometry in self._geometries.values():
      if type(geometry) is Part:
        parts.append(geometry)
    return parts

  def get_sketch_by_name(self, name):
    for sketch in self.get_sketches():
      if sketch.name == name:
        return sketch
    return None

  def get_part_by_name(self, name):
    for part in self.get_parts():
      if part.name == name:
        return part
    return None

  def items(self):
    return self._geometries.values()



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
        geometry = Sketch.deserialize(geometry_data, document.get_parameters())
        geometry.add_change_handler(self.geometry_changed)
      if geometry_data['type'] == Geometry.Part:
        geometry = Part.deserialize(geometry_data, document.get_parameters())
      if geometry is not None:
        self._geometries[geometry.uid] = geometry
    # for child_id in data.get("children", []):
    #   if child_id in self._geometries:
    #     child = self._geometries[child_id]
    #     self.add_child(child)
    #     geometry.add_change_handler(self.child_geometry_changed)

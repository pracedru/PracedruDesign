from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Objects import IdObject, ObservableObject, NamedObservableObject


class Styles(ObservableObject):
  def __init__(self):
    ObservableObject.__init__(self)
    self._edge_styles = {}
    self._hatch_styles = {}

  def get_edge_style(self, uid):
    if uid in self._edge_styles:
      return self._edge_styles[uid]
    return None

  def get_edge_style_by_name(self, name):
    for style in self._edge_styles.values():
      if style.name == name:
        return style
    style = self.create_edge_style()
    style.name = name
    return style

  def get_edge_styles(self):
    return self._edge_styles.items()

  def create_edge_style(self):
    edge_style = EdgeStyle()
    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, edge_style))
    self._edge_styles[edge_style.uid] = edge_style
    self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, edge_style))
    edge_style.add_change_handler(self.on_edge_style_changed)
    return edge_style

  def on_edge_style_changed(self, event):
    self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

  def serialize_json(self):
    return {
      'edge_styles': self._edge_styles
    }

  @staticmethod
  def deserialize(data):
    styles = Styles()
    if data is not None:
      styles.deserialize_data(data)
    return styles

  def deserialize_data(self, data):
    for edge_style_tuple in data.get('edge_styles', {}).items():
      edge_style_data = edge_style_tuple[1]
      edge_style = EdgeStyle.deserialize(edge_style_data)
      self._edge_styles[edge_style.uid] = edge_style
      edge_style.add_change_handler(self.on_edge_style_changed)


class EdgeStyle(NamedObservableObject, IdObject):
  Black = [0, 0, 0]
  Continuous = 0
  Dashed = 1
  DotDashed = 2

  def __init__(self, name="New style", thickness=0.00033, color=Black, line_type=Continuous):
    NamedObservableObject.__init__(self, name)
    IdObject.__init__(self)
    self._thickness = thickness
    self._color = color
    self._line_type = line_type

  @property
  def color(self):
    return self._color

  @property
  def thickness(self):
    return self._thickness

  @thickness.setter
  def thickness(self, value):
    old_value = value
    self._thickness = value
    self.changed(ValueChangeEvent(self, 'thickness', old_value, value))

  @property
  def line_type(self):
    return self._line_type

  def serialize_json(self):
    return {
      'uid': IdObject.serialize_json(self),
      'no': NamedObservableObject.serialize_json(self),
      'thk': self._thickness,
      'color': self._color,
      'lt': self._line_type
    }

  @staticmethod
  def deserialize(data):
    edge_style = EdgeStyle()
    if data is not None:
      edge_style.deserialize_data(data)
    return edge_style

  def deserialize_data(self, data):
    IdObject.deserialize_data(self, data['uid'])
    NamedObservableObject.deserialize_data(self, data['no'])
    self._color = data['color']
    self._thickness = data['thk']
    self._line_type = data['lt']


class HatchStyle(NamedObservableObject, IdObject):
  def __init__(self, name="New hatch"):
    NamedObservableObject.__init__(self, name)
    IdObject.__init__(self)

  def serialize_json(self):
    return {
      'uid': IdObject.serialize_json(self),
      'no': NamedObservableObject.serialize_json(self)
    }

  def deserialize_data(self, data):
    IdObject.deserialize_data(self, data['uid'])
    NamedObservableObject.deserialize_data(self, data['no'])

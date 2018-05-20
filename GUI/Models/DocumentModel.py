from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt

from Data.Areas import Area
from Data.CalcSheetAnalysis import CalcSheetAnalysis
from Data.CalcTableAnalysis import CalcTableAnalysis
from Data.Document import Document
from Data.Drawings import Drawing, Drawings, Field, SketchView, PartView
from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Parameters import Parameters, Parameter
from Data.Part import Part, Feature
from Data.Point3d import KeyPoint
from Data.Sketch import Sketch, Edge, Text, Attribute
from Data.Style import EdgeStyle
from GUI import tr
from GUI.Icons import get_icon


class DocumentItemModel(QAbstractItemModel):
  def __init__(self, document: Document):
    QAbstractItemModel.__init__(self)
    self._new_item_added_listeners = []
    self._doc = document
    self._root_item = DocumentModelItem(document, self)
    self.populate()
    if document is not None:
      document.add_change_handler(self.on_document_changed)

  def add_new_item_added_listener(self, listener):
    self._new_item_added_listeners.append(listener)

  def on_new_item_added(self, item):
    row = item.parent().children().index(item)
    index = self.createIndex(row, 0, item)
    for listener in self._new_item_added_listeners:
      listener(index)

  def populate(self):
    glocal_params_item = DocumentModelItem(self._doc.get_parameters(), self, self._root_item)
    styles_item = DocumentModelItem(self._doc.get_styles(), self, self._root_item, "Styles")
    for style_tuple in self._doc.get_styles().get_edge_styles():
      DocumentModelItem(style_tuple[1], self, styles_item)
    for param_tuple in self._doc.get_parameters().get_all_parameters():
      DocumentModelItem(param_tuple[1], self, glocal_params_item)
    geoms_item = DocumentModelItem(self._doc.get_geometries(), self, self._root_item)
    for geom in self._doc.get_geometries().items():
      if type(geom) is Sketch:
        self.populate_sketch(geom, geoms_item)
      if type(geom) is Part:
        self.populate_part(geom, geoms_item)
        # DocumentModelItem(geom, self, geoms_item)
    analyses_item = DocumentModelItem(self._doc.get_analyses(), self, self._root_item)
    for analysis in self._doc.get_analyses().items():
      self.populate_analysis(analysis, analyses_item)
    self.populate_drawings()
    DocumentModelItem(None, self, self._root_item, "Reports")

  def populate_sketch(self, sketch, parent_item):
    geom_item = self.create_model_item(parent_item, sketch)
    for param_tuple in sketch.get_all_local_parameters():
      param_item = DocumentModelItem(param_tuple[1], self, geom_item.children()[0])
    for kp_tuple in sketch.get_key_points():
      kp_item = DocumentModelItem(kp_tuple[1], self, geom_item.children()[1], "Key point")
    for edge_tuple in sketch.get_edges():
      edge_item = DocumentModelItem(edge_tuple[1], self, geom_item.children()[2])
    for text_tuple in sketch.get_texts():
      text_item = DocumentModelItem(text_tuple[1], self, geom_item.children()[3])
    for area_tuple in sketch.get_areas():
      area_item = DocumentModelItem(area_tuple[1], self, geom_item.children()[4])
    return geom_item

  def populate_drawing(self, drawing, parent_item):
    drawing_item = self.create_model_item(parent_item, drawing)
    for field_tuple in drawing.get_fields().items():
      field_item = DocumentModelItem(field_tuple[1], self, drawing_item.children()[0])
    for view in drawing.get_views():
      view_item = DocumentModelItem(view, self, drawing_item)
    return drawing_item

  def populate_part(self, part, parent_item):
    geom_item = self.create_model_item(parent_item, part)
    for feature_key in part.get_feature_progression():
      feature = part.get_feature(feature_key)
      self.create_model_item(geom_item, feature)
    return geom_item

  def populate_drawings(self):
    drawings = self._doc.get_drawings()
    drawings_item = self.create_model_item(self._root_item, drawings)
    for header in drawings.get_headers():
      self.populate_sketch(header, drawings_item)
    for dwg in self._doc.get_drawings().items:
      self.populate_drawing(dwg, drawings_item)

  def parent(self, index: QModelIndex = None):
    if not index.isValid():
      return QModelIndex()
    model_item = index.internalPointer()
    if model_item is None:
      return QModelIndex()
    elif model_item == self._root_item:
      return QModelIndex()
    else:
      parent_item = model_item.parent()
      if parent_item is not None:
        elder_item = parent_item.parent()
        if elder_item is not None:
          row = elder_item.children().index(parent_item)
        else:
          row = 0
        return self.createIndex(row, 0, model_item.parent())
    return QModelIndex()

  def index(self, row, col, parent: QModelIndex = None, *args, **kwargs):
    if parent is None:
      return self.createIndex(row, col, self._root_item)
    if parent.internalPointer() is None:
      return self.createIndex(row, col, self._root_item)
    else:
      parent_model_item = parent.internalPointer()
      model_item = parent_model_item.children()[row]
      return self.createIndex(row, 0, model_item)

  def columnCount(self, parent=None, *args, **kwargs):
    return 1

  def rowCount(self, parent=None, *args, **kwargs):
    if parent is None:
      return 1
    if parent.internalPointer() is None:
      return 1
    else:
      return len(parent.internalPointer().children())

  def data(self, index: QModelIndex, role=None):
    col = index.column()
    row = index.row()
    data = None
    model_item = index.internalPointer()
    if role == Qt.DisplayRole or role == Qt.EditRole:
      return model_item.name
    elif role == Qt.DecorationRole:
      if type(model_item.data) is Parameters:
        return get_icon("params")
      elif type(model_item.data) is Parameter:
        return get_icon("param")
      elif type(model_item.data) is Sketch:
        return get_icon("sketch")
      elif type(model_item.data) is KeyPoint:
        return get_icon("kp")
      elif type(model_item.data) is Edge:
        return get_icon("edge")
      elif type(model_item.data) is Drawing:
        return get_icon("drawing")
      elif type(model_item.data) is Text:
        return get_icon("text")
      elif type(model_item.data) is EdgeStyle:
        return get_icon("edgestyle")
      elif type(model_item.data) is Attribute:
        return get_icon("attribute")
      elif type(model_item.data) is Field:
        return get_icon("field")
      elif type(model_item.data) is SketchView:
        return get_icon("sketchview")
      elif type(model_item.data) is PartView:
        return get_icon("partview")
      elif type(model_item.data) is Area:
        return get_icon("area")
      elif type(model_item.data) is Part:
        return get_icon("part")
      elif type(model_item.data) is CalcTableAnalysis:
        return get_icon("calctable")
      elif type(model_item.data) is CalcSheetAnalysis:
        return get_icon("calcsheet")
      elif type(model_item.data) is Feature:
        if model_item.data.feature_type == Feature.SketchFeature:
          return get_icon("sketch")
        if model_item.data.feature_type == Feature.RevolveFeature:
          return get_icon("revolve")
        if model_item.data.feature_type == Feature.ExtrudeFeature:
          return get_icon("extrude")
      return get_icon("default")
    return None

  def setData(self, index: QModelIndex, value, role=None):
    model_item = index.internalPointer()
    if role == Qt.EditRole:
      model_item.data.name = str(value)
      return True
    return False

  def headerData(self, p_int, qt_orientation, role=None):
    if role == Qt.DisplayRole:
      if qt_orientation == Qt.Vertical:
        return p_int
      else:
        return "Name"

  def flags(self, index: QModelIndex):
    col = index.column()
    row = index.row()
    model_item = index.internalPointer()
    default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
    if isinstance(model_item.data, Geometry):
      default_flags = default_flags | Qt.ItemIsEditable
    if isinstance(model_item.data, Parameter):
      default_flags = default_flags | Qt.ItemIsEditable
    if isinstance(model_item.data, Drawing):
      default_flags = default_flags | Qt.ItemIsEditable
    if isinstance(model_item.data, Feature):
      default_flags = default_flags | Qt.ItemIsEditable
    return default_flags

  def on_object_deleted(self, item):
    item.setParent(None)

  def on_document_changed(self, event):
    self.layoutAboutToBeChanged.emit()
    self.layoutChanged.emit()

  def on_before_object_removed(self, parent_item, event):
    self.layoutAboutToBeChanged.emit()

  def on_object_removed(self, parent_item, event):
    for child in parent_item.children():
      if child.data == event.object:
        child.setParent(None)
      for childschild in child.children():
        if childschild.data == event.object:
          childschild.setParent(None)
    self.layoutChanged.emit()

  def on_before_object_added(self, parent_item, object):
    self.layoutAboutToBeChanged.emit()

  def on_object_added(self, parent_item, object):
    item = self.create_model_item(parent_item, object)
    if item is not None:
      self.on_new_item_added(item)
    self.layoutChanged.emit()

  def create_model_item(self, parent_item, object):
    new_item = None
    if type(parent_item.data) is Sketch:
      if type(object) is Parameter:
        parameters_item = parent_item.children()[0]
        new_item = DocumentModelItem(object, self, parameters_item)
      elif type(object) is KeyPoint:
        kps_item = parent_item.children()[1]
        new_item = DocumentModelItem(object, self, kps_item, "Key point")
      elif type(object) is Edge:
        edges_item = parent_item.children()[2]
        new_item = DocumentModelItem(object, self, edges_item)
      elif isinstance(object, Text):
        anno_item = parent_item.children()[3]
        new_item = DocumentModelItem(object, self, anno_item)
      elif type(object) is Area:
        anno_item = parent_item.children()[4]
        new_item = DocumentModelItem(object, self, anno_item)
      else:
        new_item = DocumentModelItem(object, self, parent_item)
    elif type(parent_item.data) is Drawings and type(object) is Sketch:
      headers_item = parent_item.children()[0]
      new_item = self.create_model_item(headers_item, object)
    elif type(parent_item.data) is Drawing and type(object) is Field:
      fields_item = parent_item.children()[0]
      new_item = DocumentModelItem(object, self, fields_item)
    elif type(parent_item.data) is Part and type(object) is Feature:
      if type(object) is Feature:
        if object.feature_type == Feature.PlaneFeature:
          planes_item = parent_item.children()[0]
          new_item = DocumentModelItem(object, self, planes_item)
        elif object.feature_type == Feature.SketchFeature:
          sketch = object.get_objects()[0]
          new_item = self.populate_sketch(sketch, parent_item)
        else:
          new_item = DocumentModelItem(object, self, parent_item)
    else:
      new_item = DocumentModelItem(object, self, parent_item)
      if type(object) is Sketch:
        DocumentModelItem(None, self, new_item, "Parameters")
        DocumentModelItem(None, self, new_item, "Key Points")
        DocumentModelItem(None, self, new_item, "Edges")
        DocumentModelItem(None, self, new_item, "Annotation")
        DocumentModelItem(None, self, new_item, "Areas")
      if type(object) is Drawings:
        DocumentModelItem(None, self, new_item, "Headers")
      if type(object) is Drawing:
        DocumentModelItem(None, self, new_item, "Fields")
        self.populate_sketch(object.header_sketch, new_item)
      if type(object) is Part:
        DocumentModelItem(None, self, new_item, "Planes")

    return new_item


class DocumentModelItem(QObject):
  def __init__(self, data, model, parent=None, name="No name"):
    QObject.__init__(self, parent)
    self._data = data
    self._name = tr(name, 'model')
    self._model = model
    if data is not None:
      data.add_change_handler(self.data_changed)

  def __del__(self):
    # print("modelitem deleted")
    try:
      if self._data is not None:
        self._data.remove_change_handler(self.data_changed)
    except Exception as e:
      print(str(e))

  @property
  def name(self):
    if self._data is not None:
      if hasattr(self._data, "name"):
        return self._data.name
    return self._name

  @property
  def data(self):
    return self._data

  def data_changed(self, event: ChangeEvent):
    if event.type == ChangeEvent.BeforeObjectAdded:
      self._model.on_before_object_added(self, event.object)
    elif event.type == ChangeEvent.ObjectAdded:
      self._model.on_object_added(self, event.object)
    elif event.type == ChangeEvent.BeforeObjectRemoved:
      self._model.on_before_object_removed(self, event)
    elif event.type == ChangeEvent.ObjectRemoved:
      event.object.remove_change_handler(self.data_changed)
      self._model.on_object_removed(self, event)
    elif event.type == ChangeEvent.Deleted:
      self._model.on_object_deleted(self)

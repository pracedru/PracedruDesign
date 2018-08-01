from PyQt5.QtCore import *
from Business import *
from Business.SketchActions import remove_edge, remove_edges
from Data.Sketch import Edge
from Data.Parameters import *
from GUI.init import gui_scale

__author__ = 'mamj'

col_header = ["Edges"]


class EdgesModel(QAbstractTableModel):
  def __init__(self, doc):
    QAbstractItemModel.__init__(self)
    self._sketch = None
    self._gui_scale = gui_scale()
    self._doc = doc
    self._rows = []
    self.old_row_count = 0

  def set_sketch(self, sketch):
    self.layoutAboutToBeChanged.emit()
    if self._sketch is not None:
      self._sketch.remove_change_handler(self.on_sketch_changed)
      self._rows.clear()
    self._sketch = sketch
    for edge in self._sketch.get_edges():
      self._rows.append(edge.uid)
    self._sketch.add_change_handler(self.on_sketch_changed)
    self.layoutChanged.emit()

  def rowCount(self, model_index=None, *args, **kwargs):
    return len(self._rows)

  def columnCount(self, model_index=None, *args, **kwargs):
    return len(col_header)

  def data(self, model_index: QModelIndex, int_role=None):
    col = model_index.column()
    row = model_index.row()
    data = None
    if int_role == Qt.DisplayRole:
      edge_item = self._sketch.get_edge(self._rows[row])
      if edge_item is None:
        self._rows.pop(row)
        self.layoutChanged.emit()
        return None
      if col == 0:
        data = edge_item.name
    elif int_role == Qt.EditRole:
      edge_item = self._sketch.get_edge(self._rows[row])
      if col == 0:
        data = edge_item.name


    return data

  def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
    col = model_index.column()
    row = model_index.row()
    edge_item = self._sketch.get_edge(self._rows[row])
    if col == 0:
      # edge_item.name = value
      return True

    return False

  def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
    edge = self._sketch.get_edge(self._rows[row])
    remove_edge(self._doc, edge)
    #  self._edges.remove_edge(edge)

  def remove_rows(self, rows):
    edges = []
    for row in rows:
      edges.append(self._sketch.get_edge(self._rows[row]))
    remove_edges(self._doc, self._sketch, edges)

  def on_sketch_changed(self, event: ChangeEvent):
    if type(event.object) is Edge:
      if event.type == event.BeforeObjectAdded:
        self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
      if event.type == event.ObjectAdded:
        self._rows.append(event.object.uid)
        self.endInsertRows()
      if event.type == event.BeforeObjectRemoved:
        if event.object.uid in self._rows:
          row = self._rows.index(event.object.uid)
          self.beginRemoveRows(QModelIndex(), row, row)
      if event.type == event.ObjectRemoved:
        if event.object.uid in self._rows:
          self._rows.remove(event.object.uid)
          self.endRemoveRows()
      if event.type == event.Deleted:
        self._rows.remove(event.object.uid)
        self.layoutChanged.emit()
    if event.type == event.Cleared:
      self.beginRemoveRows(QModelIndex(), 0, len(self._rows) - 1)
      self._rows = []
      self.endRemoveRows()

  def flags(self, model_index: QModelIndex):
    default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
    return default_flags

  def headerData(self, p_int, orientation, int_role=None):
    if int_role == Qt.DisplayRole:
      if orientation == Qt.Vertical:
        return p_int
      else:
        return col_header[p_int]
    elif int_role == Qt.SizeHintRole:
      if orientation == Qt.Horizontal:
        return QSize(220 * self._gui_scale, 22 * self._gui_scale);
    else:
      return None

  def get_edge_object(self):
    return self._sketch

  def get_edge(self, row):
    return self._sketch.get_edge(self._rows[row])

  def get_index_from_edge(self, edge):
    row = self._rows.index(edge.uid)
    return self.index(row, 0)

from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox

from Business import *
from Business.SketchActions import *
from Data import Areas
from Data.Areas import Area
from Data.Parameters import *
from GUI.init import gui_scale

__author__ = 'mamj'

col_header = ["Areas"]


class AreasModel(QAbstractTableModel):
  def __init__(self, doc):
    QAbstractItemModel.__init__(self)
    self._sketch = None  # doc.get_areas()
    self._rows = []
    self._doc = doc
    self._gui_scale = gui_scale()
    # for area_tuple in self._areas.get_areas():
    #    self._rows.append(area_tuple[1].uid)
    # self._areas.add_change_handler(self.on_areas_changed)
    self.old_row_count = 0

  def set_sketch(self, sketch):
    self.layoutAboutToBeChanged.emit()
    if self._sketch is not None:
      self._sketch.remove_change_handler(self.on_sketch_changed)
      self._rows.clear()
    self._sketch = sketch
    for area in self._sketch.get_areas():
      self._rows.append(area.uid)
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
      area_item = self._sketch.get_area(self._rows[row])
      if col == 0:
        data = area_item.name
    elif int_role == Qt.EditRole:
      area_item = self._sketch.get_area(self._rows[row])
      if col == 0:
        data = area_item.name
    return data

  def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
    col = model_index.column()
    row = model_index.row()
    area_item = self._sketch.get_area(self._rows[row])
    if col == 0:
      area_item.name = value
      return True

    return False

  def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
    area = self._sketch.get_area(self._rows[row])
    remove_areas(self._doc, [area])

  def remove_rows(self, rows):
    areas = []
    for row in rows:
      areas.append(self._sketch.get_area(self._rows[row]))
    remove_areas(self._doc, self._sketch, areas)

  def on_areas_changed(self, event: ChangeEvent):
    if event.type == event.BeforeObjectAdded:
      self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
    if event.type == event.ObjectAdded:
      self._rows.append(event.object.uid)
      self.endInsertRows()
    if event.type == event.BeforeObjectRemoved:
      try:
        row = self._rows.index(event.object.uid)
        self.beginRemoveRows(QModelIndex(), row, row)
      except ValueError:
        pass
    if event.type == event.ObjectRemoved:
      try:
        self._rows.remove(event.object.uid)
        self.endRemoveRows()
      except ValueError:
        pass
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
        return QSize(220 * self._gui_scale, 22 * self._gui_scale)
    else:
      return None

  def get_areas_object(self):
    return self._sketch

  def get_area(self, row):
    return self._sketch.get_area(self._rows[row])

  def get_index_from_area(self, area):
    row = self._rows.index(area.uid)
    return self.index(row, 0)

  def on_sketch_changed(self, event: ChangeEvent):
    if issubclass(type(event.object), Area):
      if event.type == event.BeforeObjectAdded:
        # print("area before object added " + event.object.name)
        self.beginInsertRows(QModelIndex(), len(self._rows), len(self._rows))
      if event.type == event.ObjectAdded:
        # print("area ObjectAdded " + event.object.name)
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

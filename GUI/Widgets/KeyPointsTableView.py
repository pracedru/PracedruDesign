from PyQt5.QtCore import QEvent, QRect, QItemSelectionModel
from PyQt5.QtCore import QItemSelection
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QMessageBox

from GUI.init import gui_scale
from GUI.Models.KeyPointsModel import KeyPointsModel


class KeyPointsTableView(QTableView):
  def __init__(self, parent, doc, main_window):
    QTableView.__init__(self, parent)
    self._main_window = main_window
    self._doc = doc
    guiscale = gui_scale()
    self._key_points_model = KeyPointsModel(self._doc)
    self.setModel(self._key_points_model)
    #self.setColumnWidth(0, 130 * guiscale)
    #self.setColumnWidth(1, 130 * guiscale)
    self.selectionModel().selectionChanged.connect(self.on_kp_selection_changed)
    self.installEventFilter(self)
    self.hide_unselected_key_points = True
    self._throw_selection_changed_event = True

  def set_sketch(self, sketch):
    self.selectionModel().clear()
    self.update_hidden_rows()
    self._key_points_model.set_sketch(sketch)
    self.resizeColumnsToContents()

  def on_kp_selection_changed(self, selection):
    if self._throw_selection_changed_event:
      selection_model = self.selectionModel()
      indexes = selection_model.selectedIndexes()
      selected_key_points = []
      for index in indexes:
        selected_key_points.append(self._key_points_model.get_key_point(index.row()))
      self._main_window.on_kp_selection_changed_in_table(selected_key_points)

  def set_selected_kps(self, selected_kps):
    # self._edges_model.get_index
    self._throw_selection_changed_event = False
    first = True
    self.selectionModel().clear()
    for kp in selected_kps:
      index = self._key_points_model.get_index_from_key_point(kp)
      if first:
        sel_type = QItemSelectionModel.ClearAndSelect
        first = False
      else:
        sel_type = QItemSelectionModel.Select
      self.selectionModel().select(index, sel_type)
    self.update_hidden_rows()
    self._throw_selection_changed_event = True

  def on_delete(self):
    txt = "Are you sure you want to delete this Key point?"
    ret = QMessageBox.warning(self, "Delete key point?", txt, QMessageBox.Yes | QMessageBox.Cancel)
    if ret == QMessageBox.Yes:
      selection_model = self.selectionModel()
      indexes = selection_model.selectedIndexes()
      selected_rows = []
      for index in indexes:
        selected_rows.append(index.row())
      self._key_points_model.remove_rows(selected_rows)

  def on_arrow_up(self):
    pass

  def on_arrow_down(self):
    pass

  def eventFilter(self, obj, event):
    if event.type() == QEvent.KeyPress:
      if event.key() == Qt.Key_Delete:
        self.on_delete()
        return True
      if event.key() == Qt.UpArrow:
        self.on_arrow_up()
      if event.key() == Qt.DownArrow:
        self.on_arrow_down()

    return False

  def update_hidden_rows(self):
    rowcount = self._key_points_model.rowCount()
    selection_model = self.selectionModel()
    indexes = selection_model.selectedIndexes()
    selected_rows = set()
    for index in indexes:
      selected_rows.add(index.row())
    for i in range(rowcount):
      if self.hide_unselected_key_points and len(selected_rows) > 0:
        hide = i not in selected_rows
        if hide:
          self.hideRow(i)
        else:
          self.showRow(i)
      else:
        self.showRow(i)
        # print("row " + str(i) + "hidden: " + str(self.isRowHidden(i)))

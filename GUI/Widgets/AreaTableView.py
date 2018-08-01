from PyQt5.QtCore import QEvent, QItemSelectionModel
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QMessageBox

from GUI.init import gui_scale
from GUI.Models.AreasModel import AreasModel


class AreaTableView(QTableView):
  def __init__(self, parent, doc, main_window):
    QTableView.__init__(self, parent)
    self._main_window = main_window
    self._doc = doc
    guiscale = gui_scale()
    self._areas_model = AreasModel(self._doc)
    self.parameters_sort_model = QSortFilterProxyModel()
    self.parameters_sort_model.setSourceModel(self._areas_model)
    self.parameters_sort_model.setSortCaseSensitivity(False)
    self.setModel(self.parameters_sort_model)
    self.setSortingEnabled(True)

    self.selectionModel().selectionChanged.connect(self.on_area_selection_changed)
    self.installEventFilter(self)
    self._throw_selection_changed_event = True

  def set_sketch(self, sketch):
    self._areas_model.set_sketch(sketch)
    self.resizeColumnsToContents()

  def on_area_selection_changed(self, selection):
    if self._throw_selection_changed_event:
      selection_model = self.selectionModel()
      indexes = selection_model.selectedIndexes()
      selected_areas = []
      for index in indexes:
        ndx = self.parameters_sort_model.mapToSource(index)
        selected_areas.append(self._areas_model.get_area(ndx.row()))
      self._main_window.on_area_selection_changed_in_table(selected_areas)

  def on_delete(self):
    txt = "Are you sure you want to delete this area?"
    ret = QMessageBox.warning(self, "Delete area?", txt, QMessageBox.Yes | QMessageBox.Cancel)
    if ret == QMessageBox.Yes:
      selection_model = self.selectionModel()
      indexes = selection_model.selectedIndexes()
      selected_rows = []
      for index in indexes:
        ndx = self.parameters_sort_model.mapToSource(index)
        selected_rows.append(ndx.row())
      self._areas_model.remove_rows(selected_rows)

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

  def set_selected_areas(self, selected_areas):
    self._throw_selection_changed_event = False
    first = True
    self.selectionModel().clear()
    for area in selected_areas:
      index = self._areas_model.get_index_from_area(area)
      if first:
        sel_type = QItemSelectionModel.ClearAndSelect
        first = False
      else:
        sel_type = QItemSelectionModel.Select
      ndx = self.parameters_sort_model.mapFromSource(index)
      self.selectionModel().select(ndx, sel_type)
    self._throw_selection_changed_event = True

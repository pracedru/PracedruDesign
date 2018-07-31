from PyQt5.QtCore import QEvent, QRect, QItemSelectionModel
from PyQt5.QtCore import QItemSelection
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QMessageBox

from GUI.init import gui_scale
from GUI.Models.EdgesModel import EdgesModel


class EdgesTableView(QTableView):
  def __init__(self, parent, doc, main_window):
    QTableView.__init__(self, parent)
    self._main_window = main_window
    self._doc = doc
    guiscale = gui_scale()
    self._edges_model = EdgesModel(self._doc)
    self.parameters_sort_model = QSortFilterProxyModel()
    self.parameters_sort_model.setSourceModel(self._edges_model)
    self.parameters_sort_model.setSortCaseSensitivity(False)
    self.setModel(self.parameters_sort_model)
    self.setSortingEnabled(True)
    self.setColumnWidth(0, 260 * guiscale)
    self.selectionModel().selectionChanged.connect(self.on_edge_selection_changed)
    self.installEventFilter(self)
    self.hide_unselected_edges = True
    self._throw_selection_changed_event = True

  def set_sketch(self, sketch):
    self.selectionModel().clear()
    self.update_hidden_rows()
    self._edges_model.set_sketch(sketch)

  def on_edge_selection_changed(self, selection):
    if self._throw_selection_changed_event:
      selection_model = self.selectionModel()
      indexes = selection_model.selectedIndexes()
      selected_edges = []
      for index in indexes:
        ndx = self.parameters_sort_model.mapToSource(index)
        selected_edges.append(self._edges_model.get_edge(ndx.row()))
      self._main_window.on_edge_selection_changed_in_table(selected_edges)

  def set_selected_edges(self, selected_edges):
    # self._edges_model.get_index
    self._throw_selection_changed_event = False
    first = True
    self.selectionModel().clear()
    for edge in selected_edges:
      index = self._edges_model.get_index_from_edge(edge)
      if first:
        sel_type = QItemSelectionModel.ClearAndSelect
        first = False
      else:
        sel_type = QItemSelectionModel.Select
      ndx = self.parameters_sort_model.mapFromSource(index)
      self.selectionModel().select(ndx, sel_type)
    self.update_hidden_rows()
    self._throw_selection_changed_event = True

  def on_delete(self):
    txt = "Are you sure you want to delete this edge?"
    ret = QMessageBox.warning(self, "Delete edge?", txt, QMessageBox.Yes | QMessageBox.Cancel)
    if ret == QMessageBox.Yes:
      selection_model = self.selectionModel()
      indexes = selection_model.selectedIndexes()
      selected_rows = []
      for index in indexes:
        ndx = self.parameters_sort_model.mapToSource(index)
        selected_rows.append(ndx.row())
      self._edges_model.remove_rows(selected_rows)

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
    rowcount = self._edges_model.rowCount()
    selection_model = self.selectionModel()
    indexes = selection_model.selectedIndexes()
    selected_rows = set()
    for index in indexes:
      selected_rows.add(index.row())
    for i in range(rowcount):
      if self.hide_unselected_edges and len(selected_rows) > 0:
        hide = i not in selected_rows
        if hide:
          self.hideRow(i)
        else:
          self.showRow(i)
      else:
        self.showRow(i)

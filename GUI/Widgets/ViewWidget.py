from PyQt5.QtWidgets import QStackedWidget

from Business import create_add_sketch_to_document
from GUI.Widgets.CalcSheetView import CalcSheetView
from GUI.Widgets.CalcTableView import CalcTableView
from GUI.Widgets.DrawingEditorView import DrawingEditorViewWidget
from GUI.Widgets.PartView import PartViewWidget
from GUI.Widgets.SketchEditorView import SketchEditorViewWidget

__author__ = 'mamj'


class ViewWidget(QStackedWidget):
  def __init__(self, main_window, document):
    QStackedWidget.__init__(self, main_window)
    self._doc = document
    self._sketchView = SketchEditorViewWidget(self, document, main_window)
    self._partView = PartViewWidget(self, document)
    self._drawingView = DrawingEditorViewWidget(self, document, main_window)
    self._calcTableView = CalcTableView(self, document, main_window)
    self._calcSheetView = CalcSheetView(self, document, main_window)
    self.addWidget(self._sketchView)
    self.addWidget(self._partView)
    self.addWidget(self._drawingView)
    self.addWidget(self._calcTableView)
    self.addWidget(self._calcSheetView)

  @property
  def sketch_view(self):
    return self._sketchView

  @property
  def drawing_view(self):
    return self._drawingView

  @property
  def part_view(self):
    return self._partView

  def set_sketch_view(self, sketch):
    self.setCurrentIndex(0)
    self._sketchView.set_sketch(sketch)

  def set_drawing_view(self, drawing):
    self.setCurrentIndex(2)
    self._drawingView.drawing = drawing

  def on_zoom_fit(self):
    if self.currentIndex() == 0:
      self._sketchView.on_zoom_fit()
    elif self.currentIndex() == 2:
      self._drawingView.on_zoom_fit()

  def set_part_view(self, part):
    self.setCurrentIndex(1)
    self._partView.set_part(part)

  def set_calc_table_view(self, calc_table):
    self.setCurrentIndex(3)
    self._calcTableView.set_calc_table(calc_table)

  def set_calc_sheet_view(self, calc_sheet):
    self.setCurrentIndex(4)
    self._calcSheetView.set_calc_sheet(calc_sheet)

  def on_area_selection_changed_in_table(self, selected_areas):
    self.sketch_view.set_selected_areas(selected_areas)

  def on_kp_selection_changed_in_table(self, selected_key_points):
    self._sketchView.set_selected_key_points(selected_key_points)

  def on_edge_selection_changed_in_table(self, selected_edges):
    self._sketchView.set_selected_edges(selected_edges)

  def on_create_sketch(self):
    if self.currentIndex() == 0:
      create_add_sketch_to_document(self._document)
    elif self.currentIndex() == 1:
      self._partView.on_create_add_sketch_to_part()
    elif self.currentIndex() == 2:
      self._drawingView.on_create_add_sketch_to_drawing()

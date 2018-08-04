from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog

from Business.DrawingActions import add_sketch_to_drawing
from Data.Vertex import Vertex
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class DrawingSketchView():
  def __init__(self, main_window):
    self._main_window = main_window
    self._insert_sketch_action = None
    self._states = main_window.states
    self._drawing_editor_view = main_window.drawing_editor_view
    self._drawing_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._drawing_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._drawing_editor_view.add_escape_event_handler(self.on_escape)
    self._states.add_sketch = False
    self._states.move_sketch = False
    self.init_ribbon()

  def init_ribbon(self):
    self._insert_sketch_action = self._main_window.add_action("Insert\nsketch",
                                                      "addsketchview",
                                                      "Insert sketch in drawing",
                                                      True,
                                                      self.on_insert_sketch,
                                                      checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Drawing")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._insert_sketch_action, True))

  def on_insert_sketch(self):
    view = self._drawing_editor_view
    view.on_escape()
    if view.drawing is None:
      return
    view.setCursor(Qt.CrossCursor)
    self._states.add_sketch = True
    self._main_window.update_ribbon_state()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.add_sketch:
      view = self._drawing_editor_view
      doc = self._main_window.document
      drawing = view.drawing

      offset = Vertex(x, y)
      scale = 1
      parts = []
      for sketch in doc.get_geometries().get_sketches():
        parts.append(sketch.name)
      value = QInputDialog.getItem(self._main_window, "Select sketch", "sketch:", parts, 0, True)
      sketch = doc.get_geometries().get_sketch_by_name(value[0])
      add_sketch_to_drawing(doc, drawing, sketch, scale, offset)
      view.on_escape()

  def on_escape(self):
    self._states.add_sketch = False

  def update_ribbon_state(self):
    self._insert_sketch_action.setChecked(self._states.add_sketch)

  @staticmethod
  def initializer(main_window):
    return DrawingSketchView(main_window)

plugin_initializers.append(DrawingSketchView.initializer)
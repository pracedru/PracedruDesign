from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QDialog

from Business.SketchActions import create_key_point, create_circle
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchCircleDraw():
  def __init__(self, main_window):
    self._main_window = main_window
    self._add_circle_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.draw_circle_edge = False
    self.init_ribbon()

  def init_ribbon(self):
    self._add_circle_action = self._main_window.add_action("Add\ncircle",
                                                           "addcircle",
                                                           "Add circle edge to sketch",
                                                           True,
                                                           self.on_add_circle,
                                                           checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_circle_action, True))

  def on_add_circle(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_kp = True
    self._states.draw_circle_edge = True
    self._main_window.update_ribbon_state()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.draw_circle_edge:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch
      coincident_threshold = 5 / scale
      kp = create_key_point(doc, sketch, x, y, 0.0, coincident_threshold)
      params = []
      params.sort()
      for param_tuple in sketch.get_all_parameters():
        params.append(param_tuple[1].name)
      value = QInputDialog.getItem(self._main_window, "Set radius parameter", "Parameter:", params, 0, True)
      if value[1] == QDialog.Accepted:
        radius_param = sketch.get_parameter_by_name(value[0])
        if radius_param is None:
          radius_param = sketch.create_parameter(value[0], 1.0)
        create_circle(doc, sketch, kp, radius_param)
      self.on_escape()

  def on_escape(self):
    self._states.draw_circle_edge = False

  def update_ribbon_state(self):
    self._add_circle_action.setChecked(self._states.draw_circle_edge)

  @staticmethod
  def initializer(main_window):
    return SketchCircleDraw(main_window)

plugin_initializers.append(SketchCircleDraw.initializer)
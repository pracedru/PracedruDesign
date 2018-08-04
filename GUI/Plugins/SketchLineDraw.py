from PyQt5.QtCore import Qt

from Business.SketchActions import get_create_keypoint, create_line
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchLineDraw():
  def __init__(self, main_window):
    self._main_window = main_window
    self._add_line_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    #self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.draw_line_edge = False
    self._last_kp = None
    self.init_ribbon()

  def init_ribbon(self):
    self._add_line_action = self._main_window.add_action("Add\nline",
                                                         "addline",
                                                         "Add line edge to edges",
                                                         True,
                                                         self.on_add_line,
                                                         checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_line_action, True))

  def on_add_line(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_kp = True
    self._states.draw_line_edge = True
    self._main_window.update_ribbon_state()
    doc = self._main_window.document
    doc.set_status("Click on sketch to select or add point.", 0, True)

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.draw_line_edge:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch
      current_kp = None
      if view.kp_hover is None:
        coincident_threshold = 5 / scale
        current_kp = get_create_keypoint(sketch, x, y, coincident_threshold)
        view.selected_key_points.append(current_kp)
      else:
        current_kp = view.kp_hover
        view.selected_key_points.append(view.kp_hover)
      if current_kp is not None and self._last_kp is not None:
        #sketch.create_line_edge(self._last_kp, current_kp)
        create_line(sketch, self._last_kp, current_kp)
        if not self._states.multi_select:
          view.selected_key_points.clear()
          self._last_kp = None
          view.on_escape()
          return
        else:
          view.selected_key_points.remove(view.selected_key_points[0])
      else:
        doc.set_status("Click on sketch to select or add point. Hold CTRL to conintue drawing.", 50, True)
      self._last_kp = current_kp

  def on_escape(self):
    self._states.draw_line_edge = False

  def update_ribbon_state(self):
    self._add_line_action.setChecked(self._states.draw_line_edge)

  @staticmethod
  def initializer(main_window):
    return SketchLineDraw(main_window)

plugin_initializers.append(SketchLineDraw.initializer)
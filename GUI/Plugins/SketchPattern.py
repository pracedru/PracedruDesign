from PyQt5.QtCore import Qt

from Business.SketchActions import create_key_point
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchPattern():
  def __init__(self, main_window):
    self._main_window = main_window
    self._pattern_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.pattern_edges = False
    self._edges_to_pattern = []
    self._areas_to_pattern = []
    self._scale_reference = None
    self.init_ribbon()

  def init_ribbon(self):
    self._pattern_action = self._main_window.add_action("Make\nPattern",
                                                        "pattern",
                                                        "Pattern selected items",
                                                        True,
                                                        self.on_pattern,
                                                        checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Operate")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._pattern_action, True))
    self._pattern_action.setEnabled(False)

  def on_pattern(self):
    self._edges_to_scale = self._sketch_editor_view.selected_edges
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.OpenHandCursor)
    self._states.select_edge = True
    self._states.select_area = True
    self._states.pattern_edges = True
    if len(self._edges_to_scale) > 0:
      self._main_window.document.set_status("Items to pattern", 0, True)
    else:
      self._main_window.document.set_status("Select edges to scale (press CTRL to multi select.)", 0, True)
    self._main_window.update_ribbon_state()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.scale_edges:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch


  def on_escape(self):
    self._states.pattern_edges = False
    self._edges_to_pattern = []
    self._areas_to_pattern = []

  def update_ribbon_state(self):
    self._pattern_action.setChecked(self._states.pattern_edges)

  @staticmethod
  def initializer(main_window):
    return SketchPattern(main_window)

plugin_initializers.append(SketchPattern.initializer)
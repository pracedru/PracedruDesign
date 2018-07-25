from PyQt5.QtCore import Qt

from Business.SketchActions import create_key_point, create_nurbs_edge
from GUI import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchSplineDraw():
  def __init__(self, main_window):
    self._main_window = main_window
    self._add_spline_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.draw_spline_edge = False
    self.init_ribbon()

  def init_ribbon(self):
    self._add_spline_action = self._main_window.add_action("Insert\nspline",
                                                         "addnurbs",
                                                         "Insert spline in sketch",
                                                         True,
                                                         self.on_add_spline,
                                                         checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_spline_action, True))

  def on_add_spline(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_kp = True
    self._states.draw_spline_edge = True
    self._states.select_edge = False
    self._main_window.update_ribbon_state()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.draw_spline_edge:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch
      if view.kp_hover is None:
        coincident_threshold = 5 / scale
        kp = create_key_point(doc, sketch, x, y, 0.0, coincident_threshold)
        view.selected_key_points.append(kp)
      else:
        kp = view.kp_hover
      if len(view.selected_edges) == 0:
        spline_edge = create_nurbs_edge(doc, sketch, kp)
        view.selected_edges.append(spline_edge)
      else:
        spline_edge = view.selected_edges[0]
        spline_edge.add_key_point(kp)

  def on_escape(self):
    self._states.draw_spline_edge = False

  def update_ribbon_state(self):
    self._add_spline_action.setChecked(self._states.draw_spline_edge)

  @staticmethod
  def initializer(main_window):
    return SketchSplineDraw(main_window)

plugin_initializers.append(SketchSplineDraw.initializer)
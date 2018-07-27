from math import log10

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QInputDialog, QDialog

from Business.SketchActions import create_key_point, find_all_similar, set_similar_x, set_similar_y
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.Ribbon.RibbonTextbox import RibbonTextbox


class SketchParametry():
  def __init__(self, main_window):
    self._main_window = main_window

    self._set_sim_x_action = None
    self._set_sim_y_action = None
    self._find_all_sim_action = None

    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.set_similar_x = False
    self._states.set_similar_y = False
    self._similar_coords = set()
    self._similar_threshold = 1
    self._last_kp = None
    self.init_ribbon()

  def init_ribbon(self):
    main_win = self._main_window
    self._set_sim_x_action = main_win.add_action("Set simil.\nx coords",
                                                 "setsimx",
                                                 "Set similar x coordinate values",
                                                 True,
                                                 self.on_set_sim_x,
                                                 checkable=True)
    self._set_sim_y_action = main_win.add_action("Set simil.\ny coords",
                                                 "setsimy",
                                                 "Set similar y coordinate values",
                                                 True,
                                                 self.on_set_sim_y,
                                                 checkable=True)
    self._find_all_sim_action = main_win.add_action("Find all\nsimmilar",
                                                    "allsim",
                                                    "find all similar coordinate values and make parameters",
                                                    True,
                                                    self.on_find_all_similar)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    param_pane = sketch_tab.get_ribbon_pane("Parametry")
    param_pane.add_ribbon_widget(RibbonButton(param_pane, self._set_sim_x_action, True))
    param_pane.add_ribbon_widget(RibbonButton(param_pane, self._set_sim_y_action, True))
    param_pane.add_ribbon_widget(RibbonButton(param_pane, self._find_all_sim_action, True))
    thresshold_text_box = RibbonTextbox(str(1), self.on_similar_thresshold_changed)
    grid = param_pane.add_grid_widget(200)
    grid.addWidget(QLabel("Thresshold"), 0, 0)
    grid.addWidget(thresshold_text_box, 0, 1)

  def on_set_sim_x(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_kp = True
    self._states.set_similar_x = True
    self._states.allow_move = False
    self._main_window.update_ribbon_state()
    self._sketch_editor_view.update()
    doc = self._main_window.document
    doc.set_status("Click on keypoint to find and set x parameter on similar x comp.", 0, True)

  def on_set_sim_y(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_kp = True
    self._states.set_similar_y = True
    self._states.allow_move = False
    self._main_window.update_ribbon_state()
    self._sketch_editor_view.update()
    doc = self._main_window.document
    doc.set_status("Click on keypoint to find and set x parameter on similar y comp.", 0, True)

  def on_find_all_similar(self):
    view = self._sketch_editor_view
    sketch = view.sketch
    doc = self._main_window.document
    if sketch is not None:
      find_all_similar(doc, sketch, int(round(log10(1 / self._similar_threshold))))
      view.update()

  def on_similar_thresshold_changed(self, event):
    value = float(event)
    self._similar_threshold = value

  def on_mouse_move(self, scale, x, y):
    update_view = False
    view = self._sketch_editor_view
    if self._states.set_similar_x and view.kp_hover is not None:
      sketch = view.sketch
      key_points = sketch.get_key_points()
      self._similar_coords.clear()
      for kp_tuple in key_points:
        key_point = kp_tuple[1]
        x1 = key_point.x
        if abs(x1 - view.kp_hover.x) < self._similar_threshold:
          self._similar_coords.add(key_point)
          update_view = True
      view._selected_key_points = list(self._similar_coords)
    if self._states.set_similar_y and view.kp_hover is not None:
      sketch = view.sketch
      key_points = sketch.get_key_points()
      self._similar_coords.clear()
      for kp_tuple in key_points:
        key_point = kp_tuple[1]
        y1 = key_point.y
        if abs(y1 - view.kp_hover.y) < self._similar_threshold:
          self._similar_coords.add(key_point)
          update_view = True
      view._selected_key_points = list(self._similar_coords)
    return update_view

  def on_mouse_press(self, scale, x, y):
    #                             ****    Find Similar params    ****
    if self._states.set_similar_x or self._states.set_similar_y:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch
      params = []
      for param_tuple in sketch.get_all_parameters():
        params.append(param_tuple[1].name)
      value = QInputDialog.getItem(self._main_window, "Set parameter", "Parameter:", params, 0, True)
      if self._states.set_similar_x and value[1] == QDialog.Accepted:
        set_similar_x(doc, sketch, self._similar_coords, value[0])
        view.update()
        view.on_escape()
      else:
        pass
        # view.on_escape()
      if self._states.set_similar_y and value[1] == QDialog.Accepted:
        set_similar_y(doc, sketch, self._similar_coords, value[0])
        view.update()
        view.on_escape()
      else:
        pass
        # view.on_escape()

  def on_escape(self):
    self._states.set_similar_x = False
    self._states.set_similar_y = False

  def update_ribbon_state(self):
    self._set_sim_x_action.setChecked(self._states.set_similar_x)
    self._set_sim_y_action.setChecked(self._states.set_similar_y)

  @staticmethod
  def initializer(main_window):
    return SketchParametry(main_window)

plugin_initializers.append(SketchParametry.initializer)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from Business.SketchActions import create_key_point, create_text, create_all_areas
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchGenerateAreas():
  def __init__(self, main_window):
    self._main_window = main_window
    self._generate_areas_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    # self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    # self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.generate_areas = False
    self.init_ribbon()

  def init_ribbon(self):
    self._generate_areas_action = self._main_window.add_action("Create\nAreas",
                                                               "createareas",
                                                               "Create areas from all edges",
                                                               True,
                                                               self.on_generate_areas)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._generate_areas_action, True))

  def on_generate_areas(self):
    self._sketch_editor_view.on_escape()
    sketch = self._sketch_editor_view.sketch
    view = self._sketch_editor_view
    if sketch is None:
      return

    go = False
    if len(sketch.get_areas()) > 0:
      txt = "This will replace all existing areas with new areas generated from the edges."
      txt += "Are you sure you want to do this?"
      ret = QMessageBox.warning(self._main_window, "Create areas?", txt, QMessageBox.Yes | QMessageBox.Cancel)
      if ret == QMessageBox.Yes:
        go = True
    else:
      go = True
    if go:
      create_all_areas(self._main_window.document, sketch)
      view.update()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    pass

  def on_escape(self):
    pass

  def update_ribbon_state(self):
    pass

  @staticmethod
  def initializer(main_window):
    return SketchGenerateAreas(main_window)

plugin_initializers.append(SketchGenerateAreas.initializer)
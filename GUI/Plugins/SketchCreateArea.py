from PyQt5.QtCore import Qt

from Business.SketchActions import create_attribute, find_all_areas, create_area
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchCreateArea():
  def __init__(self, main_window):
    self._main_window = main_window
    self._create_area_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.create_area = False

    self.init_ribbon()

  def init_ribbon(self):
    self._create_area_action = self._main_window.add_action("Create\narea",
                                                            "createarea",
                                                            "Create area from selected edges",
                                                            True,
                                                            self.on_create_area,
                                                            checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._create_area_action, True))

  def on_create_area(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_edges = True
    self._states.create_area = True
    self._main_window.update_ribbon_state()
    doc = self._main_window.document
    doc.set_status("Click on edges to create area. Hold CTRL to multi select.", 0, True)

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.create_area:
      self.check_edge_loop()


  def check_edge_loop(self):
    view = self._sketch_editor_view
    doc = self._main_window.document
    sketch = view.sketch
    branches = find_all_areas(view.selected_edges)
    for branch in branches:
      if branch['enclosed']:
        create_area(sketch, branch)
        view.on_escape()
        view.update()
        break

  def on_escape(self):
    self._states.create_area = False

  def update_ribbon_state(self):
    self._create_area_action.setChecked(self._states.create_area)

  @staticmethod
  def initializer(main_window):
    return SketchCreateArea(main_window)

plugin_initializers.append(SketchCreateArea.initializer)
from PyQt5.QtCore import Qt

from Business.SketchActions import create_key_point, create_attribute, find_all_areas, create_area
from GUI import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchCreateCompositeArea():
  def __init__(self, main_window):
    self._main_window = main_window
    self._create_composite_area_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.create_composite_area = False
    self._base_area = None
    self._subtracted_areas = []
    self.init_ribbon()

  def init_ribbon(self):
    self._create_composite_area_action = self._main_window.add_action("Create\nComp. Area",
                                                            "createcomparea",
                                                            "Create composite area from existing areas",
                                                                      True,
                                                                      self.on_create_composite_area,
                                                                      checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._create_composite_area_action, True))

  def on_create_composite_area(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_area = True
    self._states.create_composite_area = True
    self._base_area = None
    self._subtracted_areas = []
    self._main_window.document.set_status("Select base area for new composite area", 0, True)
    self._main_window.update_ribbon_state()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.create_composite_area:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch
      if view.area_hover is not None and self._base_area is None:
        self._base_area = view.area_hover
        doc.set_status("Area Accepted", 33, True)
      elif self._base_area is not None:
        pass

  def on_escape(self):
    self._states.create_composite_area = False

  def update_ribbon_state(self):
    self._create_composite_area_action.setChecked(self._states.create_composite_area)

  @staticmethod
  def initializer(main_window):
    return SketchCreateCompositeArea(main_window)

plugin_initializers.append(SketchCreateCompositeArea.initializer)
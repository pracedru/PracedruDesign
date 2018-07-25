from PyQt5.QtCore import Qt

from Business.SketchActions import create_key_point, create_attribute
from GUI import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchAttrubuteDraw():
  def __init__(self, main_window):
    self._main_window = main_window
    self._add_attribute_action = None
    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.add_attribute = False

    self.init_ribbon()

  def init_ribbon(self):
    self._add_attribute_action = self._main_window.add_action("Add\nattribute",
                                                         "addattribute",
                                                         "Add attribute to sketch",
                                                              True,
                                                              self.on_add_attribute,
                                                              checkable=True)
    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    insert_pane = sketch_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_attribute_action, True))

  def on_add_attribute(self):
    self._sketch_editor_view.on_escape()
    if self._sketch_editor_view.sketch is None:
      return
    self._sketch_editor_view.setCursor(Qt.CrossCursor)
    self._states.select_kp = True
    self._states.add_attribute = True
    self._main_window.update_ribbon_state()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    if self._states.add_attribute:
      view = self._sketch_editor_view
      doc = self._main_window.document
      sketch = view.sketch
      coincident_threshold = 5 / scale
      kp = create_key_point(doc, sketch, x, y, 0.0, coincident_threshold)
      create_attribute(doc, sketch, kp, "Attribute name", "Default value", 0.007)
      self.on_escape()

  def on_escape(self):
    self._states.add_attribute = False

  def update_ribbon_state(self):
    self._add_attribute_action.setChecked(self._states.add_attribute)

  @staticmethod
  def initializer(main_window):
    return SketchAttrubuteDraw(main_window)

plugin_initializers.append(SketchAttrubuteDraw.initializer)
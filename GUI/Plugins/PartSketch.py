from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QDialog

from Business.PartAction import create_add_sketch_to_part, insert_sketch_in_part
from GUI.Widgets.SimpleDialogs import SketchDialog
from GUI.init import plugin_initializers, tr

from GUI.Ribbon.RibbonButton import RibbonButton


class PartSketch():
  def __init__(self, main_window):
    self._main_window = main_window
    self._insert_sketch_action = None
    self._states = main_window.states
    self._part_editor_view = main_window.part_editor_view
    # self._part_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._drawing_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    # self._part_editor_view.add_escape_event_handler(self.on_escape)
    # self._states.add_sketch = False

    self.init_ribbon()

  def init_ribbon(self):
    self._create_sketch_action = self._main_window.add_action("Create\nsketch",
                                                              "addsketchview",
                                                              "Create sketch in part",
                                                              True,
                                                              self.on_create_sketch,
                                                              checkable=False)
    self._insert_sketch_action = self._main_window.add_action("Insert\nsketch",
                                                      "addsketchview",
                                                      "Insert sketch in part",
                                                      True,
                                                      self.on_insert_sketch,
                                                      checkable=False)
    ribbon = self._main_window.ribbon
    part_tab = ribbon.get_ribbon_tab("Part")
    insert_pane = part_tab.get_ribbon_pane("Insert")
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._insert_sketch_action, True))
    insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._create_sketch_action, True))

  def on_create_sketch(self):
    view = self._part_editor_view
    view.on_escape()
    if view.part is None:
      return
    planes = []
    for plane_feature in view.part.get_plane_features():
      planes.append(plane_feature.name)
    value = QInputDialog.getItem(self._main_window, "Select plane for sketch", "plane name:", planes, 0, False)
    if value[1] == QDialog.Accepted:
      for plane_feature in view.part.get_plane_features():
        if plane_feature.name == value[0]:
          create_add_sketch_to_part(view.part, plane_feature)
          view.scale_to_content()

  def on_insert_sketch(self):
    view = self._part_editor_view
    view.on_escape()
    doc = view.part.document
    if view.part is None:
      return
    sketch_dialog = SketchDialog(self._main_window, doc, view.part)
    value = sketch_dialog.exec_()
    if value == QDialog.Accepted:
      sketch_name = sketch_dialog.sketch()
      plane_name = sketch_dialog.plane()
      sketch = doc.get_geometries().get_sketch_by_name(sketch_name)
      for plane in view.part.get_plane_features():
        if plane.name == plane_name:
          break
      insert_sketch_in_part(view.part, sketch, plane)
      view.redraw_drawables()
      view.scale_to_content()

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    pass

  def on_escape(self):
    pass

  def update_ribbon_state(self):
    self._insert_sketch_action.setChecked(self._states.add_sketch)

  @staticmethod
  def initializer(main_window):
    return PartSketch(main_window)

plugin_initializers.append(PartSketch.initializer)
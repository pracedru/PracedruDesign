from PyQt5.QtCore import Qt

from Business.SketchActions import create_key_point
from Data.Sketch import Text
from Data.Vertex import Vertex
#from GUI import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.init import plugin_initializers


class DrawingSelect():
  def __init__(self, main_window):
    self._main_window = main_window

    self._states = main_window.states
    self._drawing_editor_view = main_window.drawing_editor_view
    self._drawing_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    self._drawing_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    self._drawing_editor_view.add_mouse_release_event_handler(self.on_mouse_release)
    self._drawing_editor_view.add_escape_event_handler(self.on_escape)
    self._states.select_view = True
    self._states.multi_select = False
    self._view_move = None
    self.init_ribbon()

  def init_ribbon(self):
    pass

  def clear_hover(self):
    update_view = False
    view = self._drawing_editor_view
    if view.view_hover is not None:
      update_view = True
    view.view_hover = None
    return update_view

  def on_mouse_release(self, q_mouse_event):
    if q_mouse_event.button() == 1:
      self._view_move = None

  def on_mouse_move(self, scale, x, y):
    view = self._drawing_editor_view
    drawing = view.drawing

    update_view = self.clear_hover()

    if self._states.left_button_hold:
      if self._view_move is not None:
        self._view_move.offset.x = x
        self._view_move.offset.y = y

    for dwg_view in drawing.get_views():
      dist = dwg_view.offset.distance(Vertex(x, y))
      if dist < 10 / scale:
        view.view_hover = dwg_view
        update_view = True

    return update_view

  def on_mouse_press(self, scale, x, y):
    view = self._drawing_editor_view
    drawing = view.drawing
    if self._states.select_view:
      if view.view_hover is not None:
        if view.view_hover in view.selected_views:
          self._view_move = view.view_hover
        else:
          if self._states.multi_select:
            view.selected_views.append(view.view_hover)
          else:
            view.selected_views.clear()
            view.selected_views.append(view.view_hover)
      else:
        view.selected_views.clear()
        view.update()

  def on_escape(self):
    view = self._drawing_editor_view
    self._states.select_view = True
    view.selected_views.clear()

  def update_ribbon_state(self):
    pass

  @staticmethod
  def initializer(main_window):
    return DrawingSelect(main_window)

plugin_initializers.append(DrawingSelect.initializer)
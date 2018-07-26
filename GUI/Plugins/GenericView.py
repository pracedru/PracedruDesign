from math import log10

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from Business.SketchActions import create_key_point, find_all_similar
from GUI import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.Ribbon.RibbonTextbox import RibbonTextbox


class GenericView():
  def __init__(self, main_window):
    self._main_window = main_window

    self._zoom_fit_action = None
    self._show_area_names_action = None
    self._show_kp_action = None
    self._show_hidden_params_action = None

    self._states = main_window.states
    self._sketch_editor_view = main_window.sketch_editor_view
    # self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
    # self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
    # self._sketch_editor_view.add_escape_event_handler(self.on_escape)
    self._states.show_key_points = False
    self._states.show_area_names = True
    self._states.show_params = False

    self.init_ribbon()

  def init_ribbon(self):
    main_win = self._main_window
    self._zoom_fit_action = main_win.add_action("Zoom\nfit",
                                                 "zoomfit",
                                                 "Zoom to fit contents",
                                                 True,
                                                 self.on_zoom_fit,
                                                 checkable=False)
    self._show_area_names_action = main_win.add_action("Show area\nNames",
                                                      "showareanames",
                                                      "Show area names",
                                                      True,
                                                      self.on_show_area_names,
                                                      checkable=True)
    self._show_kp_action = main_win.add_action("Show key\npoints",
                                                 "showkeypoints",
                                                 "Show keypoints as circles",
                                                 True,
                                                 self.on_show_kp,
                                                 checkable=True)
    self._show_hidden_params_action = main_win.add_action("Show hidden\nparameters",
                                               "hideparams",
                                               "Show hidden parameters",
                                               True,
                                               self.on_show_params,
                                               checkable=True)

    ribbon = self._main_window.ribbon
    sketch_tab = ribbon.get_ribbon_tab("Sketch")
    drawing_tab = ribbon.get_ribbon_tab("Drawing")
    sketch_view_pane = sketch_tab.get_ribbon_pane("View")
    sketch_view_pane.add_ribbon_widget(RibbonButton(sketch_view_pane, self._zoom_fit_action, True))
    sketch_view_pane.add_ribbon_widget(RibbonButton(sketch_view_pane, self._show_area_names_action, True))
    sketch_view_pane.add_ribbon_widget(RibbonButton(sketch_view_pane, self._show_kp_action, True))
    sketch_view_pane.add_ribbon_widget(RibbonButton(sketch_view_pane, self._show_hidden_params_action, True))

    drawing_view_pane = drawing_tab.get_ribbon_pane("View")
    drawing_view_pane.add_ribbon_widget(RibbonButton(drawing_view_pane, self._zoom_fit_action, True))

  def on_zoom_fit(self):
    self._main_window.on_zoom_fit()

  def on_show_area_names(self):
    self._states.show_area_names = not self._states.show_area_names

  def on_show_kp(self):
    self._states.show_key_points = not self._states.show_key_points

  def on_show_params(self):
    self._states.show_params = not self._states.show_params

  def on_mouse_move(self, scale, x, y):
    pass

  def on_mouse_press(self, scale, x, y):
    pass


  def on_escape(self):
    pass

  def update_ribbon_state(self):
    self._show_area_names_action.setChecked(self._states.show_area_names)
    self._show_kp_action.setChecked(self._states.show_key_points)
    self._show_hidden_params_action.setChecked(self._states.show_params)

  @staticmethod
  def initializer(main_window):
    return GenericView(main_window)

plugin_initializers.append(GenericView.initializer)
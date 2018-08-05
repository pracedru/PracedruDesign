from math import pi

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from Business.SketchActions import get_create_keypoint, add_arc
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.Widgets.SimpleDialogs import AddArcDialog


class SketchArcDraw():
	def __init__(self, main_window):
		self._main_window = main_window
		self._add_arc_action = None
		self._states = main_window.states
		self._sketch_editor_view = main_window.sketch_editor_view
		self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
		self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
		self._sketch_editor_view.add_escape_event_handler(self.on_escape)
		self._states.draw_arc_edge = False
		self.init_ribbon()

	def init_ribbon(self):
		self._add_arc_action = self._main_window.add_action("Add\narc",
																												"addarc",
																												"Add arc edge to sketch",
																												True,
																												self.on_add_arc,
																												checkable=True)
		ribbon = self._main_window.ribbon
		sketch_tab = ribbon.get_ribbon_tab("Sketch")
		insert_pane = sketch_tab.get_ribbon_pane("Insert")
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_arc_action, True))

	def on_add_arc(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.draw_arc_edge = True
		self._main_window.update_ribbon_state()

	def on_mouse_move(self, scale, x, y):
		pass

	def on_mouse_press(self, scale, x, y):
		if self._states.draw_arc_edge:
			view = self._sketch_editor_view
			coincident_threshold = 5 / scale
			sketch = view.sketch
			add_arc_widget = AddArcDialog(self._main_window, sketch)
			result = add_arc_widget.exec_()
			doc = self._main_window.document
			if result == QDialog.Accepted:
				kp = get_create_keypoint(sketch, x, y, coincident_threshold)
				radius_param = sketch.get_parameter_by_name(add_arc_widget.radius_param())
				start_angle_param = sketch.get_parameter_by_name(add_arc_widget.start_angle_param())
				end_angle_param = sketch.get_parameter_by_name(add_arc_widget.end_angle_param())
				if radius_param is None:
					radius_param = sketch.create_parameter(add_arc_widget.radius_param(), 1.0)
				if start_angle_param is None:
					start_angle_param = sketch.create_parameter(add_arc_widget.start_angle_param(), 0.0)
				if end_angle_param is None:
					end_angle_param = sketch.create_parameter(add_arc_widget.end_angle_param(), pi)
				add_arc(doc, sketch, kp, radius_param, start_angle_param, end_angle_param)
			view.on_escape()

	def on_escape(self):
		self._states.draw_arc_edge = False

	def update_ribbon_state(self):
		self._add_arc_action.setChecked(self._states.draw_arc_edge)

	@staticmethod
	def initializer(main_window):
		return SketchArcDraw(main_window)


plugin_initializers.append(SketchArcDraw.initializer)

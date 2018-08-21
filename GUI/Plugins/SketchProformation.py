from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from Business.SketchActions import create_mirror, create_pattern
from Data.Proformer import ProformerType
from GUI.Widgets.SimpleDialogs import SketchMirrorDialog, SketchPatternDialog
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchPattern():
	def __init__(self, main_window):
		self._main_window = main_window
		self._pattern_action = None
		self._mirror_action = None
		self._states = main_window.states
		self._sketch_editor_view = main_window.sketch_editor_view
		self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
		self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
		self._sketch_editor_view.add_escape_event_handler(self.on_escape)
		self._states.add_pattern = False
		self._states.add_mirror = False
		self._kps_to_proform = []
		self._edges_to_proform = []
		self._areas_to_proform = []

		self.init_ribbon()

	def init_ribbon(self):
		self._pattern_action = self._main_window.add_action("Make\nPattern",
																												"pattern",
																												"Pattern selected items",
																												True,
																												self.on_pattern,
																												checkable=True)

		self._mirror_action = self._main_window.add_action("Mirror",
																												"mirror",
																												"Mirror selected items",
																												True,
																												self.on_mirror,
																												checkable=True)

		ribbon = self._main_window.ribbon
		sketch_tab = ribbon.get_ribbon_tab("Sketch")
		edit_pane = sketch_tab.get_ribbon_pane("Edit")
		edit_pane.add_ribbon_widget(RibbonButton(edit_pane, self._pattern_action, True))
		edit_pane.add_ribbon_widget(RibbonButton(edit_pane, self._mirror_action, True))

	def on_pattern(self):
		view = self._sketch_editor_view
		if self._sketch_editor_view.sketch is None:
			return
		doc = self._main_window.document
		sketch = view.sketch
		for kp in view.selected_key_points:
			self._kps_to_proform.append(kp)
		for edge in view.selected_edges:
			self._edges_to_proform.append(edge)
		for area in view.selected_areas:
			self._areas_to_proform.append(area)
		if len(self._areas_to_proform)==0 and len(self._edges_to_proform)==0 and len(self._kps_to_proform)==0:
			view.on_escape()
			doc.set_status("Please select geometry to pattern.")
			return
		spd = SketchPatternDialog(self._main_window, sketch)

		value = spd.exec_()
		if value == QDialog.Accepted:
			count = spd.count
			pattern_type = spd.pattern_type
			create_pattern(sketch, pattern_type, self._kps_to_proform, self._edges_to_proform, self._areas_to_proform, count)
		view.on_escape()

	def on_mirror(self):
		view = self._sketch_editor_view
		if view.sketch is None:
			return

		doc = self._main_window.document
		sketch = view.sketch
		for kp in view.selected_key_points:
			self._kps_to_proform.append(kp)
		for edge in view.selected_edges:
			self._edges_to_proform.append(edge)
		for area in view.selected_areas:
			self._areas_to_proform.append(area)

		if len(self._areas_to_proform)==0 and len(self._edges_to_proform)==0 and len(self._kps_to_proform)==0:
			view.on_escape()
			doc.set_status("Please select geometry to mirror.")
			return

		smd = SketchMirrorDialog(self._main_window, sketch)
		value = smd.exec_()
		if value == QDialog.Accepted:
			mirror_type = smd.mirror_type
			create_mirror(sketch, mirror_type, self._kps_to_proform, self._edges_to_proform, self._areas_to_proform)
		view.on_escape()
		#self._states.add_mirror = True


	def on_mouse_move(self, scale, x, y):
		pass

	def on_mouse_press(self, scale, x, y):
		if self._states.scale_edges:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch

	def on_escape(self):
		self._states.add_pattern = False
		self._states.add_mirror = False
		self._kps_to_proform = []
		self._edges_to_proform = []
		self._areas_to_proform = []

	def update_ribbon_state(self):
		self._pattern_action.setChecked(self._states.add_pattern)
		self._mirror_action.setChecked(self._states.add_mirror)

	@staticmethod
	def initializer(main_window):
		return SketchPattern(main_window)


plugin_initializers.append(SketchPattern.initializer)

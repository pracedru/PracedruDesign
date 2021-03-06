from math import pi

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QDialog

from Business.ParameterActions import get_create_parameters
from Business.SketchActions import get_create_keypoint, create_line, add_sketch_instance_to_sketch, create_nurbs_edge, add_arc, \
	create_circle, create_fillet, create_text, create_attribute
from GUI.Widgets.SimpleDialogs import AddArcDialog, SingleParameterDialog, MultiParameterDialog
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchLineDraw():
	def __init__(self, main_window):
		self._main_window = main_window
		self._add_line_action = None
		self._add_spline_action = None
		self._add_sketch_instance_action = None
		self._add_arc_action = None
		self._add_circle_action = None
		self._add_fillet_action = None
		self._add_text_action = None
		self._add_attribute_action = None
		self._states = main_window.states
		self._sketch_editor_view = main_window.sketch_editor_view
		self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
		# self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
		self._sketch_editor_view.add_escape_event_handler(self.on_escape)
		self._states.draw_line_edge = False
		self._states.add_sketch_instance = False
		self._states.draw_spline_edge = False
		self._states.draw_arc_edge = False
		self._states.draw_circle_edge = False
		self._states.add_fillet_edge = False
		self._states.add_text = False
		self._states.add_attribute = False
		self._last_kp = None
		self.init_ribbon()


	def init_ribbon(self):
		self._add_line_action = self._main_window.add_action("Add\nline",
																												 "addline",
																												 "Add line edge to edges",
																												 True,
																												 self.on_add_line,
																												 checkable=True)
		self._add_spline_action = self._main_window.add_action("Insert\nspline",
																													 "addnurbs",
																													 "Insert spline in sketch",
																													 True,
																													 self.on_add_spline,
																													 checkable=True)
		self._add_sketch_instance_action = self._main_window.add_action("Add\nInstance",
																																		"addsketch",
																																		"Add sketch instance to this sketch",
																																		True,
																																		self.on_add_sketch_instance,
																																		checkable=True)
		self._add_circle_action = self._main_window.add_action("Add\ncircle",
																													 "addcircle",
																													 "Add circle edge to sketch",
																													 True,
																													 self.on_add_circle,
																													 checkable=True)
		self._add_arc_action = self._main_window.add_action("Add\narc",
																												"addarc",
																												"Add arc edge to sketch",
																												True,
																												self.on_add_arc,
																												checkable=True)
		self._add_fillet_action = self._main_window.add_action("Add\nfillet",
																													 "addfillet",
																													 "Add fillet edge to existing sketch",
																													 True,
																													 self.on_add_fillet,
																													 checkable=True)
		self._add_text_action = self._main_window.add_action("Add\ntext",
																												 "addtext",
																												 "Add text to sketch",
																												 True,
																												 self.on_add_text,
																												 checkable=True)
		self._add_attribute_action = self._main_window.add_action("Add\nattribute",
																															"addattribute",
																															"Add attribute to sketch",
																															True,
																															self.on_add_attribute,
																															checkable=True)
		ribbon = self._main_window.ribbon
		sketch_tab = ribbon.get_ribbon_tab("Sketch")
		insert_pane = sketch_tab.get_ribbon_pane("Insert")
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_line_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_spline_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_arc_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_circle_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_fillet_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_text_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_attribute_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._add_sketch_instance_action, True))

	def on_add_line(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.draw_line_edge = True
		self._main_window.update_ribbon_state()
		doc = self._main_window.document
		doc.set_status("Click on sketch to select or add point.", 0, True)

	def on_add_spline(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.draw_spline_edge = True
		self._states.select_edge = False
		self._main_window.update_ribbon_state()

	def on_add_sketch_instance(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.add_sketch_instance = True
		self._states.select_kp = True
		self._main_window.update_ribbon_state()
		doc = self._main_window.document
		doc.set_status("Click on sketch to select or add point for the sketch instance insert point.", 0, True)

	def on_add_arc(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.draw_arc_edge = True
		self._main_window.update_ribbon_state()

	def on_add_circle(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.draw_circle_edge = True
		self._main_window.update_ribbon_state()

	def on_add_fillet(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.add_fillet_edge = True
		self._main_window.update_ribbon_state()

	def on_add_text(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_kp = True
		self._states.add_text = True
		self._main_window.update_ribbon_state()

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
		#                                     ***        Line         ***
		if self._states.draw_line_edge:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			current_kp = None
			if view.kp_hover is None:
				coincident_threshold = 5 / scale
				current_kp = get_create_keypoint(sketch, x, y, coincident_threshold)
				view.selected_key_points.append(current_kp)
			else:
				current_kp = view.kp_hover
				view.selected_key_points.append(view.kp_hover)
			if current_kp is not None and self._last_kp is not None:
				# sketch.create_line_edge(self._last_kp, current_kp)
				create_line(sketch, self._last_kp, current_kp)
				if not self._states.multi_select:
					view.selected_key_points.clear()
					self._last_kp = None
					view.on_escape()
					return
				else:
					view.selected_key_points.remove(view.selected_key_points[0])
			else:
				doc.set_status("Click on sketch to select or add point. Hold CTRL to conintue drawing.", 50, True)
			self._last_kp = current_kp
		#                                     ***        Spline       ***
		if self._states.draw_spline_edge:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			if view.kp_hover is None:
				coincident_threshold = 5 / scale
				kp = get_create_keypoint(sketch, x, y, coincident_threshold)
				view.selected_key_points.append(kp)
			else:
				kp = view.kp_hover
			if len(view.selected_edges) == 0:
				spline_edge = create_nurbs_edge(doc, sketch, kp)
				view.selected_edges.append(spline_edge)
			else:
				spline_edge = view.selected_edges[0]
				spline_edge.add_key_point(kp)

		#                                     ***        Arch         ***
		if self._states.draw_arc_edge:
			view = self._sketch_editor_view
			coincident_threshold = 5 / scale
			sketch = view.sketch
			#add_arc_widget = AddArcDialog(self._main_window, sketch)
			add_arc_widget = MultiParameterDialog(self._main_window, sketch, "Create Arc", ["Radius", "Start angle", "End angle"])
			result = add_arc_widget.exec_()
			doc = self._main_window.document
			if result == QDialog.Accepted:
				kp = get_create_keypoint(sketch, x, y, coincident_threshold)
				params = get_create_parameters(sketch, add_arc_widget.parameter_results)
				radius_param = params["Radius"]
				start_angle_param = params["Start angle"]
				end_angle_param = params["End angle"]
				add_arc(doc, sketch, kp, radius_param, start_angle_param, end_angle_param)
			view.on_escape()
		#                                     ***        Circle       ***
		if self._states.draw_circle_edge:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			coincident_threshold = 5 / scale
			kp = get_create_keypoint(sketch, x, y, coincident_threshold)
			params = []
			params.sort()
			for param in sketch.get_all_parameters():
				params.append(param.name)
			#value = QInputDialog.getItem(self._main_window, "Set radius parameter", "Parameter:", params, 0, True)
			spd = SingleParameterDialog(self._main_window, sketch, "Create Fillet")
			dialog_result = spd.exec_()
			if dialog_result == QDialog.Accepted:
				param_name = spd.dimensions["param_1_name"]
				param_value = spd.dimensions["param_1_value"]
				radius_param = sketch.get_parameter_by_name(param_name)
				if radius_param is None:
					radius_param = sketch.create_parameter(param_name, param_value)
				create_circle(doc, sketch, kp, radius_param)
			view.on_escape()

		#                                     *** Add Sketch Instance ***
		if self._states.add_sketch_instance:
			view = self._sketch_editor_view
			self._states.add_sketch_instance = False
			sketch = view.sketch
			parent = sketch.parent

			if view.kp_hover is None:
				coincident_threshold = 5 / scale
				current_kp = get_create_keypoint(sketch, x, y, coincident_threshold)
			else:
				current_kp = view.kp_hover

			sketch_list = []
			for item in parent.get_sketches():
				if item is not sketch:
					sketch_list.append(item.name)

			value = QInputDialog.getItem(self._main_window, "Select sketch", "sketch:", sketch_list, 0, True)
			sketch_to_insert = None
			for item in parent.get_sketches():
				if item.name == value[0]:
					sketch_to_insert = parent.get_sketch_by_name(value[0])
			if sketch_to_insert is not None:
				add_sketch_instance_to_sketch(sketch, sketch_to_insert, current_kp)
			view.on_escape()

		#                                     *** Add Fillet ***
		if self._states.add_fillet_edge:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			if view.kp_hover is not None:
				edges = view.kp_hover.get_edges()
				if len(edges) != 2:
					view.selected_key_points.remove(view.kp_hover)
				if not self._states.multi_select:
					params = []
					params.sort()
					for param in sketch.get_all_parameters():
						params.append(param.name)
					spd = SingleParameterDialog(self._main_window, sketch, "Create Fillet")
					#value = QInputDialog.getItem(self._main_window, "Set radius parameter", "Parameter:", params, 0, True)
					dialog_result = spd.exec_()
					if dialog_result == QDialog.Accepted:
						param_name = spd.dimensions["param_1_name"]
						param_value = spd.dimensions["param_1_value"]
						radius_param = sketch.get_parameter_by_name(param_name)
						if radius_param is None:
							radius_param = sketch.create_parameter(param_name, param_value)
						for kp in view.selected_key_points:
							create_fillet(doc, sketch, kp, radius_param)
						view.on_escape()
				else:
					pass

		#                                     *** Add Text ***
		if self._states.add_text:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			coincident_threshold = 5 / scale
			kp = get_create_keypoint(sketch, x, y, coincident_threshold)
			create_text(doc, sketch, kp, "New Text", 0.003)
			view.on_escape()

		#                                     *** Add Attribute ***
		if self._states.add_attribute:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			coincident_threshold = 5 / scale
			kp = get_create_keypoint(sketch, x, y, coincident_threshold)
			create_attribute(doc, sketch, kp, "Attribute name", "Default value", 0.007)
			self.on_escape()

	def on_escape(self):
		self._states.draw_line_edge = False
		self._states.add_sketch_instance = False
		self._states.draw_spline_edge = False
		self._states.draw_arc_edge = False
		self._states.draw_circle_edge = False
		self._states.add_fillet_edge = False
		self._states.add_text = False
		self._states.add_attribute = False
		self._last_kp = None

	def update_ribbon_state(self):
		self._add_line_action.setChecked(self._states.draw_line_edge)
		self._add_sketch_instance_action.setChecked(self._states.add_sketch_instance)
		self._add_spline_action.setChecked(self._states.draw_spline_edge)
		self._add_arc_action.setChecked(self._states.draw_arc_edge)
		self._add_circle_action.setChecked(self._states.draw_circle_edge)
		self._add_fillet_action.setChecked(self._states.add_fillet_edge)
		self._add_text_action.setChecked(self._states.add_text)
		self._add_attribute_action.setChecked(self._states.add_attribute)

	@staticmethod
	def initializer(main_window):
		return SketchLineDraw(main_window)


plugin_initializers.append(SketchLineDraw.initializer)

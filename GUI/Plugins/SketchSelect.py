from PyQt5.QtCore import Qt

from Data.Sketch import Text, Alignment
from Data.Vertex import Vertex
# from GUI import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.init import plugin_initializers


class SketchSelect():
	def __init__(self, main_window):
		self._main_window = main_window
		self._add_line_action = None
		self._states = main_window.states
		self._sketch_editor_view = main_window.sketch_editor_view
		self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
		self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
		self._sketch_editor_view.add_escape_event_handler(self.on_escape)
		self._states.select_kp = True
		self._states.select_edge = True
		self._states.select_area = True
		self._states.select_text = True
		self._states.multi_select = False
		self._states.select_instance = True
		self.init_ribbon()

	def init_ribbon(self):
		pass

	def on_mouse_move(self, scale, x, y):
		update_view = False
		view = self._sketch_editor_view
		sketch = view.sketch
		key_points = sketch.get_keypoints()

		if view.kp_hover is not None:
			view.kp_hover = None
			update_view = True
		if view.edge_hover is not None:
			view.edge_hover = None
			update_view = True
		if view.text_hover is not None:
			view.text_hover = None
			update_view = True
		if view.area_hover is not None:
			view.area_hover = None
			update_view = True
		if view.instance_hover is not None:
			view.instance_hover = None
			update_view = True

		#                             ****    Keypoint Hover    ****
		if self._states.select_kp:
			for key_point in key_points:
				x1 = key_point.x
				y1 = key_point.y
				if abs(x1 - x) < 5 / scale and abs(y1 - y) < 5 / scale:
					view.kp_hover = key_point
					update_view = True
					break

		#                             ****    Edge Hover    ****
		if self._states.select_edge and view.kp_hover is None:
			smallest_dist = 10e10
			closest_edge = None
			for edge in sketch.get_edges():
				dist = edge.distance(Vertex(x, y, 0), None)
				if dist < smallest_dist:
					smallest_dist = dist
					closest_edge = edge
			if smallest_dist * scale < 10:
				view.edge_hover = closest_edge
				update_view = True

		#                             ****    Area Hover    ****
		if self._states.select_area and view.kp_hover is None and view.edge_hover is None:
			for area in sketch.get_areas():
				if area.inside(Vertex(x, y, 0)):
					view.area_hover = area
					update_view = True

		#                             ****    Text Hover    ****
		if self._states.select_text and view.edge_hover is None and view.kp_hover is None:
			for text in sketch.get_texts():
				key_point = text.key_point
				x1 = key_point.x
				y1 = key_point.y
				if text.horizontal_alignment == Alignment.Left:
					x1 -= text.height * len(text.value) / 2
				elif text.horizontal_alignment == Alignment.Right:
					x1 += text.height * len(text.value) / 2
				if text.vertical_alignment == Alignment.Top:
					y1 += text.height / 2
				elif text.vertical_alignment == Alignment.Bottom:
					y1 -= text.height / 2
				if abs(y1 - y) < text.height and abs(x1 - x) < text.height * len(text.value) / 2:
					view.text_hover = text
					update_view = True
					break

		if self._states.select_instance:
			for instance in sketch.sketch_instances:
				if instance.inside(Vertex(x, y, 0)):
					view.instance_hover = instance
					update_view = True

		return update_view

	def on_mouse_press(self, scale, x, y):
		view = self._sketch_editor_view
		sketch = view.sketch
		if sketch is None:
			return
		key_points = sketch.get_keypoints()

		#                             ****    Keypoint select    ****
		if view.kp_hover is not None and self._states.select_kp:
			if self._states.multi_select:
				view.selected_key_points.append(view.kp_hover)
			else:
				view.selected_key_points = [view.kp_hover]
			view.update()
			self._main_window.on_kp_selection_changed_in_view(view.selected_key_points)
		elif view.kp_hover is None and self._states.select_kp and len(
				view.selected_edges) == 0 and not self._states.draw_line_edge:
			view.selected_key_points = []
			view.update()
			self._main_window.on_kp_selection_changed_in_view(view.selected_key_points)

		#                             ****    Edge select    ****
		if self._states.select_edge and view.edge_hover is not None and view.kp_hover is None:
			if self._states.multi_select:
				if view.edge_hover in view.selected_edges:
					view.selected_edges.remove(view.edge_hover)
				else:
					view.selected_edges.append(view.edge_hover)
			else:
				view.selected_edges = [view.edge_hover]
			view.update()
			self._main_window.on_edge_selection_changed_in_view(view.selected_edges)
		elif self._states.select_edge and view.edge_hover is None:
			view.selected_edges = []
			view.update()
			self._main_window.on_edge_selection_changed_in_view(view.selected_edges)

		#                             ****    Area select    ****
		if self._states.select_area:
			if view.area_hover is not None:
				if self._states.multi_select:
					view.selected_areas.append(view.area_hover)
				else:
					view.selected_areas = [view.area_hover]

				view.selected_edges = []
				for area in view.selected_areas:
					for edge in area.get_edges():
						view.selected_edges.append(edge)
				self._main_window.on_edge_selection_changed_in_view(view.selected_edges)
				self._main_window.on_area_selection_changed_in_view(view.selected_areas)
				view.update()
			else:
				if not self._states.multi_select:
					view.selected_areas = []
					view.update()

		#                             ****    Text select    ****
		if self._states.select_text:
			if view.text_hover is not None:
				if self._states.multi_select:
					view.selected_texts.append(view.text_hover)
				else:
					view.selected_texts = [view.text_hover]
			else:
				view.selected_texts = []
			self._main_window.on_text_selection_changed_in_view(view.selected_texts)

		if self._states.select_instance:
			if view.instance_hover is not None:
				if self._states.multi_select:
					view.selected_instances.append(view.instance_hover)
					view.update()
				else:
					view.selected_instances = [view.instance_hover]
			else:
				view.selected_instances = []

	def on_escape(self):
		view = self._sketch_editor_view
		self._states.select_kp = True
		self._states.select_edge = True
		self._states.select_area = True
		view.selected_key_points.clear()
		view.selected_edges.clear()
		view.selected_areas.clear()

	def update_ribbon_state(self):
		pass

	@staticmethod
	def initializer(main_window):
		return SketchSelect(main_window)


plugin_initializers.append(SketchSelect.initializer)

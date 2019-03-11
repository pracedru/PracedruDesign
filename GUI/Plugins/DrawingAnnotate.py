from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.init import plugin_initializers


class DrawingAnnotate():
	def __init__(self, main_window):
		self._main_window = main_window
		self._states = main_window.states
		self._insert_dim_annotation = None

		self._drawing_editor_view = main_window.drawing_editor_view
		self._drawing_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
		self._drawing_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
		self._drawing_editor_view.add_mouse_release_event_handler(self.on_mouse_release)
		self._drawing_editor_view.add_escape_event_handler(self.on_escape)
		self._drawing_editor_view.add_delete_event_handler(self.on_delete)
		self._states.dimming = False
		# self._states.multi_select = False

		self.init_ribbon()

	def init_ribbon(self):
		self._insert_dim_annotation = self._main_window.add_action("Dim", "insertdimannotation",
																									"Insert dimension annotation in drawing", True,
																									self.on_insert_dim_ann_in_drawing)
		ribbon = self._main_window.ribbon
		sketch_tab = ribbon.get_ribbon_tab("Drawing")
		annotation_pane = sketch_tab.get_ribbon_pane("Annotation")
		annotation_pane.add_ribbon_widget(RibbonButton(annotation_pane, self._insert_dim_annotation, True))
		# insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._insert_sketch_action, True))

	def on_insert_dim_ann_in_drawing(self):
		pass

	def on_mouse_release(self, q_mouse_event):
		pass

	def on_mouse_move(self, scale, x, y, dx, dy):
		pass

	def on_mouse_press(self, scale, x, y):
		pass

	def on_delete(self):
		pass

	def on_escape(self):
		pass

	def update_ribbon_state(self):
		pass

	@staticmethod
	def initializer(main_window):
		return DrawingAnnotate(main_window)

plugin_initializers.append(DrawingAnnotate.initializer)
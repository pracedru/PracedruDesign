from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from Business.SketchActions import create_all_areas, find_all_areas, create_area, create_composite_area
from GUI.init import plugin_initializers

from GUI.Ribbon.RibbonButton import RibbonButton


class SketchGenerateAreas():
	def __init__(self, main_window):
		self._main_window = main_window
		self._generate_areas_action = None
		self._create_area_action = None
		self._create_composite_area_action = None
		self._states = main_window.states
		self._sketch_editor_view = main_window.sketch_editor_view
		self._sketch_editor_view.add_mouse_press_event_handler(self.on_mouse_press)
		# self._sketch_editor_view.add_mouse_move_event_handler(self.on_mouse_move)
		self._sketch_editor_view.add_escape_event_handler(self.on_escape)
		self._states.generate_areas = False
		self._states.create_area = False
		self._states.create_composite_area = False
		self._base_area = None
		self._subtracted_areas = []
		self.init_ribbon()

	def init_ribbon(self):
		self._generate_areas_action = self._main_window.add_action("Create\nAreas",
																															 "createareas",
																															 "Create areas from all edges",
																															 True,
																															 self.on_generate_areas)
		self._create_area_action = self._main_window.add_action("Create\narea",
																														"createarea",
																														"Create area from selected edges",
																														True,
																														self.on_create_area,
																														checkable=True)
		self._create_composite_area_action = self._main_window.add_action("Create\nComp. Area",
																																			"addcompositearea",
																																			"Create composite area from existing areas",
																																			True,
																																			self.on_create_composite_area,
																																			checkable=True)
		ribbon = self._main_window.ribbon
		sketch_tab = ribbon.get_ribbon_tab("Sketch")
		insert_pane = sketch_tab.get_ribbon_pane("Insert")
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._generate_areas_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._create_area_action, True))
		insert_pane.add_ribbon_widget(RibbonButton(insert_pane, self._create_composite_area_action, True))

	def on_generate_areas(self):
		self._sketch_editor_view.on_escape()
		sketch = self._sketch_editor_view.sketch
		view = self._sketch_editor_view
		if sketch is None:
			return

		go = False
		if len(sketch.get_areas()) > 0:
			txt = "This will replace all existing areas with new areas generated from the edges."
			txt += "Are you sure you want to do this?"
			ret = QMessageBox.warning(self._main_window, "Create areas?", txt, QMessageBox.Yes | QMessageBox.Cancel)
			if ret == QMessageBox.Yes:
				go = True
		else:
			go = True
		if go:
			create_all_areas(self._main_window.document, sketch)
			view.update()

	def on_create_area(self):
		self._sketch_editor_view.on_escape()
		if self._sketch_editor_view.sketch is None:
			return
		self._sketch_editor_view.setCursor(Qt.CrossCursor)
		self._states.select_edges = True
		self._states.create_area = True
		self._main_window.update_ribbon_state()
		doc = self._main_window.document
		doc.set_status("Click on edges to create area. Hold CTRL to multi select.", 0, True)

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

	def check_edge_loop(self):
		view = self._sketch_editor_view
		doc = self._main_window.document
		sketch = view.sketch
		branches = find_all_areas(view.selected_edges)
		for branch in branches:
			if branch['enclosed']:
				create_area(sketch, branch)
				view.on_escape()
				view.update()
				break

	def on_mouse_move(self, scale, x, y):
		pass

	def on_mouse_press(self, scale, x, y):
		if self._states.create_area:
			self.check_edge_loop()

		if self._states.create_composite_area:
			view = self._sketch_editor_view
			doc = self._main_window.document
			sketch = view.sketch
			if view.area_hover is not None and self._base_area is None:
				self._base_area = view.area_hover
				doc.set_status("Select areas to subtract. Hold CTRL to select multiple areas.", 33, True)
			elif view.area_hover is not None and self._base_area is not None:
				if view.area_hover != self._base_area:
					self._subtracted_areas.append(view.area_hover)
					if self._states.multi_select:
						pass
					else:
						create_composite_area(sketch, self._base_area, self._subtracted_areas)
						view.update()
						view.on_escape()

	def on_escape(self):
		self._base_area = None
		self._subtracted_areas = []
		self._states.create_composite_area = False
		self._states.create_area = False

	def update_ribbon_state(self):
		self._create_area_action.setChecked(self._states.create_area)
		self._create_composite_area_action.setChecked(self._states.create_composite_area)

	@staticmethod
	def initializer(main_window):
		return SketchGenerateAreas(main_window)


plugin_initializers.append(SketchGenerateAreas.initializer)

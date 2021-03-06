import traceback
from math import *

from PyQt5.QtCore import QEvent, QPoint, Qt, QPointF
from PyQt5.QtGui import QColor, QLinearGradient, QTransform, QPen, QPainter, QBrush
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, QWidget

from Business.SketchActions import *
from Data.Style import BrushType
from GUI.GeometryViews.SketchView import get_sketch_view

from GUI.init import is_dark_theme
from GUI.Widgets.NewDrawers import *



class SketchEditorViewWidget(QWidget):
	def __init__(self, parent, document, main_window):

		QWidget.__init__(self, parent)
		self._main_window = main_window
		self._states = main_window.get_states()
		self.setMouseTracking(True)
		self._doc = document
		self._is_dark_theme = is_dark_theme()
		self._sketch = None
		self._scale = 1.0
		self._offset = Vertex()
		self._mouse_position = None
		self._move_ref_pos = None
		self._pan_ref_pos = None
		self._selected_edges = []
		self._selected_key_points = []
		self._selected_texts = []
		self._selected_areas = []
		self._selected_instances = []
		self._kp_move = None
		self._kp_hover = None
		self._edge_hover = None
		self._text_hover = None
		self._area_hover = None
		self._instance_hover = None
		self._mouse_press_event_handlers = []
		self._mouse_move_event_handlers = []
		self._escape_event_handlers = []
		self.installEventFilter(self)
		if self._is_dark_theme:
			self._axis_pen = QPen(QColor(40, 50, 80), 1)
			self._gradient_color_top = QColor(80, 80, 90)
			self._gradient_color_bottom = QColor(50, 50, 60)
		else:
			self._axis_pen = QPen(QColor(140, 150, 180), 1)
			self._gradient_color_top = QColor(220, 220, 230)
			self._gradient_color_bottom = QColor(170, 170, 180)

	@property
	def scale(self):
		return self._scale

	@property
	def sketch(self):
		return self._sketch

	@property
	def kp_hover(self):
		return self._kp_hover

	@kp_hover.setter
	def kp_hover(self, value):
		self._kp_hover = value

	@property
	def edge_hover(self):
		return self._edge_hover

	@edge_hover.setter
	def edge_hover(self, value):
		self._edge_hover = value

	@property
	def area_hover(self):
		return self._area_hover

	@area_hover.setter
	def area_hover(self, value):
		self._area_hover = value

	@property
	def instance_hover(self):
		return self._instance_hover

	@instance_hover.setter
	def instance_hover(self, value):
		self._instance_hover = value

	@property
	def text_hover(self):
		return self._text_hover

	@text_hover.setter
	def text_hover(self, value):
		self._text_hover = value

	@property
	def selected_texts(self):
		return self._selected_texts

	@selected_texts.setter
	def selected_texts(self, value):
		self._selected_texts = value
		self.update()

	@property
	def selected_key_points(self):
		return self._selected_key_points

	@selected_key_points.setter
	def selected_key_points(self, value):
		self._selected_key_points = value
		self.update()

	@property
	def selected_edges(self):
		return self._selected_edges

	@selected_edges.setter
	def selected_edges(self, value):
		self._selected_edges = value
		self.update()

	@property
	def selected_areas(self):
		return self._selected_areas

	@selected_areas.setter
	def selected_areas(self, value):
		self._selected_areas = value
		self.update()

	@property
	def selected_instances(self):
		return self._selected_instances

	@selected_instances.setter
	def selected_instances(self, value):
		self._selected_instances = value
		self.update()


	def eventFilter(self, obj, event):
		if event.type() == QEvent.KeyPress:
			if event.key() == Qt.Key_Delete:
				self.on_delete()
				return True
			if event.key() == Qt.Key_Control:
				self._states.multi_select = True
			if event.key() == Qt.Key_Escape:
				self.on_escape()
		if event.type() == QEvent.KeyRelease:
			if event.key() == Qt.Key_Control:
				self._states.multi_select = False
		if event.type() == QEvent.GraphicsSceneMouseDoubleClick:
			print("double click")
		return False

	def add_mouse_press_event_handler(self, event_handler):
		self._mouse_press_event_handlers.append(event_handler)

	def add_mouse_move_event_handler(self, event_handler):
		self._mouse_move_event_handlers.append(event_handler)

	def add_escape_event_handler(self, event_handler):
		self._escape_event_handlers.append(event_handler)

	def on_zoom_fit(self):
		if self._sketch is None:
			return
		limits = self._sketch.get_limits()
		x_min = limits[0]
		x_max = limits[2]
		y_min = limits[1]
		y_max = limits[3]
		y_scale = 1
		x_scale = 1

		if (y_max - y_min) != 0:
			y_scale = self.height() / (y_max - y_min)
		if (x_max - x_min) != 0:
			x_scale = self.width() / (x_max - x_min)
		scale = min(y_scale, x_scale) * 0.9
		self._offset.x = -(x_min + (x_max - x_min) / 2)
		self._offset.y = -(y_min + (y_max - y_min) / 2)
		self._scale = scale
		self.update()

	def on_delete(self):
		txt = "Are you sure you want to delete these geometries?"
		ret = QMessageBox.warning(self, "Delete geometries?", txt, QMessageBox.Yes | QMessageBox.Cancel)
		if ret == QMessageBox.Yes:
			remove_key_points(self._sketch, self._selected_key_points)
			remove_edges(self._sketch, self._selected_edges)
			remove_texts(self._sketch, self._selected_texts)
			self._selected_key_points.clear()
			self._selected_edges.clear()

	def on_escape(self):

		self.setCursor(Qt.ArrowCursor)
		self._doc.set_status("", 0, True)
		for event_handler in self._escape_event_handlers:
			event_handler()
		self._main_window.update_ribbon_state()

	def set_sketch(self, sketch):
		self._sketch = sketch
		self.on_escape()
		self.update()

	def mouseReleaseEvent(self, q_mouse_event):
		if q_mouse_event.button() == 4:
			self._states.middle_button_hold = False
			return
		if q_mouse_event.button() == 1:
			self._states.left_button_hold = False
			self._kp_move = None
			return

	def on_create_composite_area(self):
		self.on_escape()
		self._states.create_composite_area = True
		self._doc.set_status("Select base area for new area", 0, True)
		self._main_window.update_ribbon_state()

	def mouseMoveEvent(self, q_mouse_event):
		self.update_status()
		position = q_mouse_event.pos()
		update_view = False
		if self._mouse_position is not None:
			mouse_move_x = self._mouse_position.x() - position.x()
			mouse_move_y = self._mouse_position.y() - position.y()
		else:
			mouse_move_x = 0
			mouse_move_y = 0
		self._mouse_position = position
		width = self.width() / 2
		height = self.height() / 2
		scale = self._scale
		x = (self._mouse_position.x() - width) / scale - self._offset.x
		y = -((self._mouse_position.y() - height) / scale + self._offset.y)
		sketch = self._sketch
		if sketch is None:
			return

		if self._states.middle_button_hold:
			self._offset.x -= mouse_move_x / scale
			self._offset.y += mouse_move_y / scale
			update_view = True
		if self._states.left_button_hold:
			if self._kp_move is not None:
				if self._kp_move.get_x_parameter() is None:
					self._kp_move.x = x
					update_view = True
				if self._kp_move.get_y_parameter() is None:
					self._kp_move.y = y
					update_view = True

		for event_handler in self._mouse_move_event_handlers:
			if event_handler(scale, x, y):
				update_view = True

		if update_view:
			self.update()

	def mousePressEvent(self, q_mouse_event):
		self.setFocus()
		position = q_mouse_event.pos()
		if q_mouse_event.button() == 4:
			self._states.middle_button_hold = True
			self._pan_ref_pos = position
			return
		if q_mouse_event.button() == 1:
			self._states.left_button_hold = True
			self._move_ref_pos = position

		half_width = self.width() / 2
		half_height = self.height() / 2
		scale = self._scale
		x = (self._mouse_position.x() - half_width) / scale - self._offset.x
		y = -((self._mouse_position.y() - half_height) / scale + self._offset.y)

		#                             ****    Keypoint move    ****
		if self._states.left_button_hold and self._kp_hover is not None and self._states.allow_move:
			if self._kp_hover in self._selected_key_points and self._kp_hover.editable:
				self._kp_move = self._kp_hover

		for event_handler in self._mouse_press_event_handlers:
			event_handler(scale, x, y)

	def wheelEvent(self, event):
		if self._mouse_position is not None:
			delta = event.angleDelta().y() / 8
			if self._scale + self._scale * (delta * 0.01) > 0:
				self._scale += self._scale * (delta * 0.01)
				width = self.width() / 2
				height = self.height() / 2
				scale = self._scale
				x = self._mouse_position.x() - width
				y = self._mouse_position.y() - height
				distx = x / scale
				disty = y / scale
				self._offset.x -= distx * (delta * 0.01)
				self._offset.y += disty * (delta * 0.01)
				self.update()

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)


		p1 = QPoint(0, 0)
		p2 = QPoint(self.width(), self.height())
		p3 = QPoint(0, self.height())
		gradient = QLinearGradient(p1, p3)

		gradient.setColorAt(0, self._gradient_color_top)
		gradient.setColorAt(1, self._gradient_color_bottom)

		qp.fillRect(event.rect(), gradient)
		qp.setRenderHint(QPainter.HighQualityAntialiasing)

		cx = self._offset.x * self._scale + self.width() / 2
		cy = -self._offset.y * self._scale + self.height() / 2

		qp.setPen(self._axis_pen)
		if self.width() > cx > 0:
			qp.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
		if self.height() > cy > 0:
			qp.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

		qp.save()
		qp.translate(self.width()/2, self.height()/2)
		qp.scale(self._scale, self._scale)
		qp.translate(self._offset.x, -self._offset.y)

		try:
			self.draw_instances(event, qp)
			self.draw_areas(event, qp)
			self.draw_edges(event, qp)
			self.draw_texts(event, qp)
		except Exception as e:
			print(str(e))
			traceback.print_exc()

		qp.restore()
		qp.end()

	def draw_texts(self, event, qp: QPainter):
		if self._sketch is None:
			return
		normal_pen = QPen(QColor(0, 0, 0), 2)
		kp_pen_hover = QPen(QColor(0, 120, 255), 3)
		kp_pen_hl = QPen(QColor(180, 50, 0), 3)
		qp.setPen(normal_pen)
		for text in self._sketch.get_texts():
			if type(text) is Text:
				draw_text(text, qp, 1/self._scale)
			elif type(text) is Attribute:
				draw_attribute(text, qp, 1/self._scale)
		if self._text_hover is not None:
			qp.setPen(kp_pen_hover)
			if type(self._text_hover) is Text:
				draw_text(self._text_hover, qp, 1/self._scale)
			elif type(self._text_hover) is Attribute:
				draw_attribute(self._text_hover, qp, 1/self._scale)
		qp.setPen(kp_pen_hl)
		for text in self._selected_texts:
			if type(text) is Text:
				draw_text(text, qp, 1/self._scale)
			elif type(text) is Attribute:
				draw_attribute(text, qp, 1/self._scale)

	def draw_edges(self, event, qp):
		edge_thickness = 6000/self._scale
		if not self._states.show_thickness:
			edge_thickness = 0
		pens = create_pens(self._doc, edge_thickness)
		pens_hover = create_pens(self._doc, edge_thickness, QColor(100, 100, 200), 2)
		pens_select_high = create_pens(self._doc, edge_thickness, QColor(255, 0, 0), 3)
		pens_select = create_pens(self._doc, edge_thickness, QColor(255, 255, 255))
		if self._is_dark_theme:
			kp_pen = QPen(QColor(0, 200, 200), 1/self._scale)
			kp_pen_hl = QPen(QColor(190, 0, 0), 3/self._scale)
			kp_pen_hover = QPen(QColor(0, 60, 150), 3/self._scale)
		else:
			kp_pen = QPen(QColor(0, 100, 200), 1/self._scale)
			kp_pen_hl = QPen(QColor(180, 50, 0), 3/self._scale)
			kp_pen_hover = QPen(QColor(0, 120, 255), 3/self._scale)

		if self._sketch is None:
			return

		edges = self._sketch.get_edges()

		for edge in edges:
			draw_edge(edge, qp, pens, None)

		for edge in self._selected_edges:
			draw_edge(edge, qp, pens_select_high, None)

		for edge in self._selected_edges:
			draw_edge(edge, qp, pens_select, None)

		if self._edge_hover is not None:
			draw_edge(self._edge_hover, qp, pens_hover, None)

		qp.setPen(pens['default'])

		key_points = self._sketch.get_keypoints()
		for kp in key_points:
			qp.setPen(kp_pen)
			key_point = kp

			if self._kp_hover is key_point and self._states.select_kp:
				qp.setPen(kp_pen_hover)

			if self._states.show_key_points or self._kp_hover is key_point or self._states.set_similar_x or self._states.set_similar_y:
				draw_kp(qp, key_point, self._scale)

		qp.setPen(kp_pen_hl)

		for key_point in self._selected_key_points:
			draw_kp(qp, key_point, self._scale)

	def draw_areas(self, event, qp: QPainter):
		if self._sketch is None:
			return

		area_brush = QBrush(QColor(150, 150, 150, 80))
		area_hover_brush = QBrush(QColor(150, 150, 200, 80))
		area_selected_brush = QBrush(QColor(150, 150, 200, 120))
		areas = self._sketch.get_areas()

		qp.setPen(Qt.NoPen)

		for area in areas:
			brush = area_brush
			if area in self._selected_areas:
				brush = area_selected_brush
			if area == self._area_hover:
				brush = area_hover_brush

			draw_area(area, qp, self._states.show_area_names or area in self._selected_areas, brush, 1/self._scale, None)
			if area.brush is not None:
				if area.brush.type == BrushType.Solid:
					brush = QBrush(QColor(0, 0, 0))
				else:
					brush = QBrush(QColor(0, 0, 0), Qt.HorPattern)
				transform = QTransform().scale(1 / self._scale, 1 / self._scale).rotate(area.brush_rotation)
				brush.setTransform(transform)

				draw_area(area, qp, self._states.show_area_names or area in self._selected_areas, brush, 1/self._scale, None)

	def draw_instances(self, event, qp):

		if self._sketch is None:
			return

		for sketch_inst in self._sketch.sketch_instances:
			si = sketch_inst.sketch
			os = sketch_inst.offset/sketch_inst.scale
			pens = create_pens(self._doc, 6000/(self._scale*sketch_inst.scale))

			sketch_view = get_sketch_view(si)
			sketch_view.draw_instance(qp, pens, sketch_inst.scale, 1 / self._scale, os, Vertex(), sketch_inst.rotation, sketch_inst.uid)
			#draw_sketch(qp, si, sketch_inst.scale , 1/self._scale, os, Vertex(), sketch_inst.rotation, pens, {}, sketch_inst.uid)

		if self._instance_hover is not None:
			sketch_inst = self._instance_hover
			si = sketch_inst.sketch
			os = sketch_inst.offset / sketch_inst.scale
			hover_pens = create_pens(self._doc, 6000 / (self._scale * sketch_inst.scale), QColor(100, 100, 200), 1)
			sketch_view = get_sketch_view(si)
			sketch_view.draw_instance(qp, hover_pens, sketch_inst.scale, 1 / self._scale, os, Vertex(), sketch_inst.rotation, sketch_inst.uid)
			#draw_sketch(qp, si, sketch_inst.scale, 1 / self._scale, os, Vertex(), sketch_inst.rotation, hover_pens, {}, sketch_inst.uid)

		for sketch_inst in self._selected_instances:
			si = sketch_inst.sketch
			os = sketch_inst.offset / sketch_inst.scale
			sel_pens = create_pens(self._doc, 6000 / (self._scale * sketch_inst.scale), QColor(255, 0, 0), 2)
			sketch_view = get_sketch_view(si)
			sketch_view.draw_instance(qp, sel_pens, sketch_inst.scale, 1/self._scale, os, Vertex(), sketch_inst.rotation, sketch_inst.uid)
			#draw_sketch(qp, si, sketch_inst.scale, 1 / self._scale, os, Vertex(), sketch_inst.rotation, sel_pens, {},sketch_inst.uid)

	def update_status(self):
		self._doc.set_status("")


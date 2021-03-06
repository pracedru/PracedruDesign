from PyQt5 import QtGui

from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QWidget

from Business.DrawingActions import *
from Data.Vertex import Vertex
from GUI.GeometryViews.SketchView import get_sketch_view
from GUI.init import is_dark_theme
from GUI.Widgets.NewDrawers import *
import GUI.Widgets.Drawers

class DrawingEditorViewWidget(QWidget):
	def __init__(self, parent, document, main_window):
		QWidget.__init__(self, parent)
		self._main_window = main_window
		self._states = main_window.get_states()
		self._doc = document
		self._drawing = None
		self._is_dark_theme = is_dark_theme()
		self._scale = 1000
		self._offset = Vertex()
		self._mouse_position = None
		self.setMouseTracking(True)
		self._view_hover = None
		self._selected_views = []
		self._mouse_press_event_handlers = []
		self._mouse_move_event_handlers = []
		self._mouse_release_event_handlers = []
		self._escape_event_handlers = []
		self._delete_event_handlers = []
		if self._is_dark_theme:
			self._kp_pen = QPen(QColor(0, 200, 200), 1)
			self._kp_pen_hl = QPen(QColor(190, 0, 0), 3)
			self._kp_pen_hover = QPen(QColor(0, 60, 150), 3)
			self._paper_color = QColor(200, 200, 200)

		else:
			self._kp_pen = QPen(QColor(0, 100, 200), 1)
			self._kp_pen_hl = QPen(QColor(180, 50, 0), 3)
			self._kp_pen_hover = QPen(QColor(0, 120, 255), 3)
			self._paper_color = QColor(255, 255, 255)
		self.installEventFilter(self)

	@property
	def drawing(self):
		return self._drawing

	@drawing.setter
	def drawing(self, drawing):
		self._drawing = drawing
		self.update()

	@property
	def view_hover(self):
		return self._view_hover

	@view_hover.setter
	def view_hover(self, value):
		self._view_hover = value

	@property
	def selected_views(self):
		return self._selected_views

	def add_mouse_press_event_handler(self, event_handler):
		self._mouse_press_event_handlers.append(event_handler)

	def add_mouse_move_event_handler(self, event_handler):
		self._mouse_move_event_handlers.append(event_handler)

	def add_mouse_release_event_handler(self, event_handler):
		self._mouse_release_event_handlers.append(event_handler)

	def add_escape_event_handler(self, event_handler):
		self._escape_event_handlers.append(event_handler)

	def add_delete_event_handler(self, event_handler):
		self._delete_event_handlers.append(event_handler)

	def on_zoom_fit(self):
		if self._drawing is None:
			return
		x_min = 0
		x_max = self._drawing.size[0]
		y_min = 0
		y_max = self._drawing.size[1]
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

	def on_add_field(self):
		add_field_to_drawing(self._doc, self._drawing)

	def on_delete(self):
		for event_handler in self._delete_event_handlers:
			event_handler()
		self.update()

	def on_escape(self):
		self._states.add_part = False
		self.setCursor(Qt.ArrowCursor)
		for event_handler in self._escape_event_handlers:
			event_handler()
		self._main_window.update_ribbon_state()
		self.update()

	def on_create_header(self):
		create_empty_header()

	def on_create_add_sketch_to_drawing(self):
		pass

	def on_insert_part(self):
		self.on_escape()
		if self._drawing is None:
			return
		self.setCursor(Qt.CrossCursor)
		self._states.add_part = True
		self._main_window.update_ribbon_state()

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

	def mouseReleaseEvent(self, q_mouse_event):
		if q_mouse_event.button() == 4:
			self._states.middle_button_hold = False
		if q_mouse_event.button() == 1:
			self._states.left_button_hold = False
		for event_handler in self._mouse_release_event_handlers:
			event_handler(q_mouse_event)

	def mousePressEvent(self, q_mouse_event):
		self.setFocus()
		position = q_mouse_event.pos()
		half_width = self.width() / 2
		half_height = self.height() / 2
		scale = self._scale
		x = (self._mouse_position.x() - half_width) / scale - self._offset.x
		y = -((self._mouse_position.y() - half_height) / scale + self._offset.y)
		if q_mouse_event.button() == 4:
			self._states.middle_button_hold = True
			self._pan_ref_pos = position
			return
		if q_mouse_event.button() == 1:
			self._states.left_button_hold = True
			self._move_ref_pos = position
		position = q_mouse_event.pos()

		if self._states.add_part:
			offset = Vertex(x, y)
			scale = 1
			parts = []
			for part in self._doc.get_geometries().get_parts():
				parts.append(part.name)
			value = QInputDialog.getItem(self, "Select part", "parts:", parts, 0, True)
			part = self._doc.get_geometries().get_part_by_name(value[0])
			if part is not None:
				add_part_to_drawing(self._doc, self._drawing, part, scale, offset)
			self.on_escape()

		for event_handler in self._mouse_press_event_handlers:
			event_handler(scale, x, y)

	def mouseMoveEvent(self, q_mouse_event):
		update_view = False
		position = q_mouse_event.pos()
		if self._mouse_position is not None:
			mouse_move_x = self._mouse_position.x() - position.x()
			mouse_move_y = self._mouse_position.y() - position.y()
		else:
			mouse_move_x = 0
			mouse_move_y = 0
		self._mouse_position = position
		dx = -mouse_move_x / self._scale
		dy = mouse_move_y / self._scale
		if self._states.middle_button_hold:
			self._offset.x += dx
			self._offset.y += dy

		if self._states.middle_button_hold:
			self.update()

		half_width = self.width() / 2
		half_height = self.height() / 2
		scale = self._scale
		x = (self._mouse_position.x() - half_width) / scale - self._offset.x
		y = -((self._mouse_position.y() - half_height) / scale + self._offset.y)

		for event_handler in self._mouse_move_event_handlers:
			if event_handler(scale, x, y, dx, dy):
				update_view = True

		if update_view:
			self.update()

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
		qp = QtGui.QPainter()
		qp.begin(self)
		p1 = QPoint(0, 0)
		p2 = QPoint(self.width(), self.height())
		p3 = QPoint(0, self.height())
		gradient = QLinearGradient(p1, p3)
		if self._is_dark_theme:
			gradient.setColorAt(0, QColor(80, 80, 90))
			gradient.setColorAt(1, QColor(50, 50, 60))
		else:
			gradient.setColorAt(0, QColor(220, 220, 230))
			gradient.setColorAt(1, QColor(170, 170, 180))
		qp.fillRect(event.rect(), gradient)
		qp.setRenderHint(QtGui.QPainter.Antialiasing)
		self.draw_drawing(event, qp)
		qp.end()

	def draw_drawing(self, event, qp):
		if self._drawing is not None:
			sc = self._scale
			pens = create_pens(self._doc, 1)
			half_width = self.width() / 2
			half_height = self.height() / 2
			center = Vertex(half_width, half_height)
			cx = self._offset.x * sc + half_width
			cy = -self._offset.y * sc + half_height
			rect = QRectF(QPointF(cx, cy), QPointF(cx + self._drawing.size[0] * sc, cy - self._drawing.size[1] * sc))
			qp.fillRect(rect, self._paper_color)
			self.draw_border(event, qp, cx, cy, pens)
			self.draw_header(event, qp, cx, cy, center, pens)
			self.draw_views(event, qp, center, pens)

	def draw_views(self, event, qp, center, pens):
		sc = self._scale

		for view in self._drawing.get_views():
			edge_thickness = 1/view.scale
			if not self._states.show_thickness:
				edge_thickness = 0
			scale = sc * view.scale
			pens = create_pens(self._doc, edge_thickness)
			offset = Vertex(self._offset.x / view.scale, self._offset.y / view.scale)
			c = Vertex(center.x + view.offset.x * sc, center.y - view.offset.y * sc)
			#draw_sketch(qp, view.sketch, scale, 0.0002 * sc, offset, c, 0, pens, {})
			sketch_view = get_sketch_view(view.sketch)
			sketch_view.draw_instance(qp, pens, scale, 0.0002 * sc, offset, c, 0)
		if self._view_hover is not None:
			scale = sc * self._view_hover.scale
			cx = self._offset.x * sc + self.width() / 2 + self._view_hover.offset.x * sc
			cy = -self._offset.y * sc + self.height() / 2 - self._view_hover.offset.y * sc
			qp.setPen(self._kp_pen_hover)
			GUI.Widgets.Drawers.draw_vertex(qp, self._view_hover.offset, sc, self._offset, center)
			l = self._view_hover.limits
			rect = QRectF(QPointF(l[0]*scale + cx, -l[1]*scale + cy), QPointF(l[2]*scale + cx, -l[3]*scale + cy))
			qp.drawRect(rect)
		for view in self._selected_views:
			scale = sc * view.scale
			cx = self._offset.x * sc + self.width() / 2 + view.offset.x * sc
			cy = -self._offset.y * sc + self.height() / 2 - view.offset.y * sc
			qp.setPen(self._kp_pen_hl)
			GUI.Widgets.Drawers.draw_vertex(qp, view.offset, sc, self._offset, center)
			l = view.limits
			rect = QRectF(QPointF(l[0] * scale + cx, -l[1] * scale + cy), QPointF(l[2] * scale + cx, -l[3] * scale + cy))
			qp.drawRect(rect)

	def draw_header(self, event, qp, cx, cy, center, pens):
		sketch = self._drawing.header_sketch
		limits = sketch.get_limits()
		header_width = limits[2] - limits[0]
		header_height = limits[3] - limits[1]
		m = self._drawing.margins
		sz = self._drawing.size
		offset = Vertex(sz[0] - header_width - m[2] + self._offset.x, m[3] + self._offset.y)
		draw_sketch(qp, sketch, self._scale, 0.0002 * self._scale, offset, center,0 , pens, self._drawing.get_fields())

	def draw_sketch_view(self, event, qp, cx, cy, contour_pen, hatch_pen, annotation_pen, sketch_view):
		pass

	def draw_border(self, event, qp, cx, cy, pens):
		sketch = self._drawing.border_sketch
		c = Vertex(cx, cy)
		draw_sketch(qp, sketch, self._scale, 0.0002 * self._scale, Vertex(), c, 0, pens, {})
		return

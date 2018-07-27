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
from GUI.init import is_dark_theme
from GUI.Widgets.Drawers import draw_sketch, create_pens


class DrawingEditorViewWidget(QWidget):
  def __init__(self, parent, document, main_window):
    QWidget.__init__(self, parent)
    self._main_window = main_window
    self._states = main_window.get_states()
    self._doc = document
    self._drawing = None
    self._is_dark_theme = is_dark_theme()
    self._scale = 100
    self._offset = Vertex()
    self._mouse_position = None
    self.setMouseTracking(True)
    self.installEventFilter(self)

  def set_drawing(self, drawing):
    self._drawing = drawing
    self.update()

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

  def on_escape(self):
    self._states.add_sketch = False
    self._states.add_part = False
    self.setCursor(Qt.ArrowCursor)
    self._main_window.update_ribbon_state()

  def on_insert_sketch(self):
    self.on_escape()
    if self._drawing is None:
      return
    self.setCursor(Qt.CrossCursor)
    self._states.add_sketch = True
    self._main_window.update_ribbon_state()

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
      return
    if q_mouse_event.button() == 1:
      self._states.left_button_hold = False
      self._kp_move = None
      return

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
    if self._states.add_sketch:
      offset = Vertex(x, y)
      scale = 1
      parts = []
      for sketch in self._doc.get_geometries().get_sketches():
        parts.append(sketch.name)
      value = QInputDialog.getItem(self, "Select sketch", "sketch:", parts, 0, True)
      sketch = self._doc.get_geometries().get_sketch_by_name(value[0])
      add_sketch_to_drawing(self._doc, self._drawing, sketch, scale, offset)
      self.on_escape()
    if self._states.add_part:
      offset = Vertex(x, y)
      scale = 1
      parts = []
      for part in self._doc.get_geometries().get_parts():
        parts.append(part.name)
      value = QInputDialog.getItem(self, "Select part", "parts:", parts, 0, True)
      part = self._doc.get_geometries().get_part_by_name(value[0])
      add_part_to_drawing(self._doc, self._drawing, part, scale, offset)
      self.on_escape()

  def mouseMoveEvent(self, q_mouse_event):
    position = q_mouse_event.pos()
    if self._mouse_position is not None:
      mouse_move_x = self._mouse_position.x() - position.x()
      mouse_move_y = self._mouse_position.y() - position.y()
    else:
      mouse_move_x = 0
      mouse_move_y = 0
    self._mouse_position = position
    if self._states.middle_button_hold:
      self._offset.x -= mouse_move_x / self._scale
      self._offset.y += mouse_move_y / self._scale

    if self._states.middle_button_hold:
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
      border_pen = QPen(QtGui.QColor(0, 0, 0), 0.0005 * sc)
      pens = create_pens(self._doc, sc)
      half_width = self.width() / 2
      half_height = self.height() / 2
      center = Vertex(half_width, half_height)
      cx = self._offset.x * sc + half_width
      cy = -self._offset.y * sc + half_height
      rect = QRectF(QPointF(cx, cy), QPointF(cx + self._drawing.size[0] * sc, cy - self._drawing.size[1] * sc))
      qp.fillRect(rect, QColor(255, 255, 255))
      self.draw_border(event, qp, cx, cy, border_pen)
      self.draw_header(event, qp, cx, cy, center, pens)
      self.draw_views(event, qp, center, pens)

  def draw_views(self, event, qp, center, pens):
    sc = self._scale
    for view in self._drawing.get_views():
      scale = sc * view.scale
      offset = Vertex(self._offset.x / view.scale, self._offset.y / view.scale)
      c = Vertex(center.x + view.offset.x * sc, center.y - view.offset.y * sc)
      draw_sketch(qp, view.sketch, scale, offset, c, pens, {})

  def draw_header(self, event, qp, cx, cy, center, pens):
    sketch = self._drawing.header_sketch
    limits = sketch.get_limits()
    header_width = limits[2] - limits[0]
    header_height = limits[3] - limits[1]
    m = self._drawing.margins
    sz = self._drawing.size
    offset = Vertex(sz[0] - header_width - m[2] + self._offset.x, m[3] + self._offset.y)
    draw_sketch(qp, sketch, self._scale, offset, center, pens, self._drawing.get_fields())

  def draw_sketch_view(self, event, qp, cx, cy, contour_pen, hatch_pen, annotation_pen, sketch_view):
    pass

  def draw_border(self, event, qp, cx, cy, border_pen):
    sc = self._scale
    sz = self._drawing.size
    shadow_pen = QPen(QtGui.QColor(150, 150, 150), 2)
    rect = QRectF(QPointF(cx, cy), QPointF(cx + sz[0] * sc, cy - sz[1] * sc))
    qp.setPen(shadow_pen)
    qp.drawRect(rect)
    qp.setPen(border_pen)
    m = self._drawing.margins
    rect = QRectF(QPointF(cx + m[0] * sc, cy - m[3] * sc), QPointF(cx + sz[0] * sc - m[2] * sc, cy - sz[1] * sc + m[1] * sc))
    qp.drawRect(rect)
    border_lines = []
    border_width = sz[0] - m[0] - m[2]
    max_len = 0.1
    divisions = round(border_width / max_len)
    length = border_width / divisions
    for i in range(1, divisions):
      pnt1 = QPointF(cx + m[0] * sc + i * length * sc, cy - m[3] * sc)
      pnt2 = QPointF(cx + m[0] * sc + i * length * sc, cy - m[3] * sc / 2)
      line = QLineF(pnt1, pnt2)
      border_lines.append(line)
      pnt1 = QPointF(cx + m[0] * sc + i * length * sc, cy - sz[1] * sc + m[1] * sc)
      pnt2 = QPointF(cx + m[0] * sc + i * length * sc, cy - sz[1] * sc + m[1] * sc / 2)
      line = QLineF(pnt1, pnt2)
      border_lines.append(line)
    border_height = sz[1] - m[1] - m[3]
    divisions = round(border_height / max_len)
    length = border_height / divisions
    for i in range(1, divisions):
      pnt1 = QPointF(cx + m[0] * sc, cy - m[3] * sc - i * length * sc)
      pnt2 = QPointF(cx + m[0] * sc / 2, cy - m[3] * sc - i * length * sc)
      line = QLineF(pnt1, pnt2)
      border_lines.append(line)
      pnt1 = QPointF(cx + sz[0] * sc - m[2] * sc, cy - m[3] * sc - i * length * sc)
      pnt2 = QPointF(cx + sz[0] * sc - m[2] * sc / 2, cy - m[3] * sc - i * length * sc)
      line = QLineF(pnt1, pnt2)
      border_lines.append(line)
    qp.drawLines(border_lines)

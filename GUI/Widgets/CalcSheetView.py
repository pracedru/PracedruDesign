from PyQt5 import QtGui

from PyQt5.QtCore import QEvent, Qt, QPoint, QRectF, QPointF
from PyQt5.QtGui import QLinearGradient, QColor, QPen
from PyQt5.QtWidgets import QWidget

from Data.Vertex import Vertex
from GUI.init import is_dark_theme
from GUI.Widgets.Drawers import create_pens


class CalcSheetView(QWidget):
  def __init__(self, parent, document, main_window):
    QWidget.__init__(self, parent)
    self._main_window = main_window
    self._doc = document
    self._sheet = None
    self.setMouseTracking(True)
    self._scale = 1.0
    self._is_dark_theme = is_dark_theme()
    self._mouse_position = None
    self._offset = Vertex()
    self.installEventFilter(self)

  def set_calc_sheet(self, sheet):
    self._sheet = sheet
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

  def mouseReleaseEvent(self, q_mouse_event):
    pass

  def mousePressEvent(self, q_mouse_event):
    pass

  def mouseMoveEvent(self, q_mouse_event):
    position = q_mouse_event.pos()
    if self._mouse_position is not None:
      mouse_move_x = self._mouse_position.x() - position.x()
      mouse_move_y = self._mouse_position.y() - position.y()
    else:
      mouse_move_x = 0
      mouse_move_y = 0
    self._mouse_position = position
    #if self._states.middle_button_hold:
    #  self._offset.x -= mouse_move_x / self._scale
    #  self._offset.y += mouse_move_y / self._scale

    #if self._states.middle_button_hold:
    #  self.update()

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
    self.draw_sheet(event, qp)
    qp.end()

  def draw_sheet(self, event, qp):
    if self._sheet is not None:
      sc = self._scale
      border_pen = QPen(QtGui.QColor(0, 0, 0), 0.0005 * sc)
      pens = create_pens(self._doc, sc)
      half_width = self.width() / 2
      half_height = self.height() / 2
      center = Vertex(half_width, half_height)
      cx = self._offset.x * sc + half_width
      cy = -self._offset.y * sc + half_height
      rect = QRectF(QPointF(cx, cy), QPointF(cx + self._sheet.size[0] * sc, cy - self._sheet.size[1] * sc))
      qp.fillRect(rect, QColor(255, 255, 255))
      self.draw_border(event, qp, cx, cy, border_pen)

  def draw_border(self, event, qp, cx, cy, border_pen):
    sc = self._scale
    sz = self._sheet.size
    shadow_pen = QPen(QtGui.QColor(150, 150, 150), 2)
    rect = QRectF(QPointF(cx, cy), QPointF(cx + sz[0] * sc, cy - sz[1] * sc))
    qp.setPen(shadow_pen)
    qp.drawRect(rect)
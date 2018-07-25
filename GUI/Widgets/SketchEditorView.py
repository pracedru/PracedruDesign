from math import *

from PyQt5.QtCore import QEvent, QPoint
from PyQt5.QtGui import QColor, QLinearGradient
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, QWidget

from Business.SketchActions import *

from Data.Vertex import Vertex
from GUI import is_dark_theme
from GUI.Widgets.Drawers import *
from GUI.Widgets.SimpleDialogs import AddArcDialog


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
    self._similar_coords = set()
    self._kp_hover = None
    self._kp_move = None
    self._edge_hover = None
    self._text_hover = None
    self._area_hover = None
    self._mouse_press_event_handlers = []
    self._mouse_move_event_handlers = []
    self._escape_event_handlers = []
    self.similar_threshold = 1
    self.installEventFilter(self)

  @property
  def sketch(self):
    return self._sketch

  @property
  def kp_hover(self):
    return self._kp_hover

  @property
  def edge_hover(self):
      return self._edge_hover

  @property
  def area_hover(self):
      return self._area_hover

  @property
  def selected_key_points(self):
    return self._selected_key_points

  @property
  def selected_edges(self):
    return self._selected_edges

  @property
  def selected_areas(self):
    return self._selected_areas

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

  def on_find_all_similar(self):
    if self._sketch is not None:
      find_all_similar(self._doc, self._sketch, int(round(log10(1 / self.similar_threshold))))

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

  def on_similar_thresshold_changed(self, value):
    self.similar_threshold = value

  def on_delete(self):
    txt = "Are you sure you want to delete these geometries?"
    ret = QMessageBox.warning(self, "Delete geometries?", txt, QMessageBox.Yes | QMessageBox.Cancel)
    if ret == QMessageBox.Yes:
      pass
      remove_key_points(self._doc, self._sketch, self._selected_key_points)
      remove_edges(self._doc, self._sketch, self._selected_edges)
      self._selected_key_points.clear()
      self._selected_edges.clear()

  def set_selected_areas(self, selected_areas):
    self._selected_areas = selected_areas
    self.update()

  def set_selected_key_points(self, selected_key_points):
    self._selected_key_points = selected_key_points
    self.update()

  def set_selected_edges(self, selected_edges):
    self._selected_edges = selected_edges
    self.update()

  def on_escape(self):
    self._states.set_similar_x = False
    self._states.set_similar_y = False
    self._states.create_composite_area = False
    self._states.select_edge = True
    self._selected_key_points.clear()
    self._selected_edges.clear()
    self.setCursor(Qt.ArrowCursor)
    self._doc.set_status("", 0, True)
    for event_handler in self._escape_event_handlers:
      event_handler()
    self._main_window.update_ribbon_state()

  def on_set_similar_x_coordinates(self):
    self.on_escape()
    self._states.set_similar_x = True
    self._states.select_kp = True
    self._main_window.update_ribbon_state()

  def on_set_similar_y_coordinates(self):
    self.on_escape()
    self._states.set_similar_y = True
    self._states.select_kp = True
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
    key_points = sketch.get_key_points()
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

    self._kp_hover = None
    self._edge_hover = None
    self._text_hover = None
    self._area_hover = None

    if self._states.select_kp:
      for kp_tuple in key_points:
        key_point = kp_tuple[1]
        x1 = key_point.x
        y1 = key_point.y
        if abs(x1 - x) < 5 / scale and abs(y1 - y) < 5 / scale:
          self._kp_hover = key_point
          update_view = True
          break

    if self._states.select_edge and self._kp_hover is None:
      smallest_dist = 10e10
      closest_edge = None
      for edge_tuple in sketch.get_edges():
        edge = edge_tuple[1]
        dist = edge.distance(Vertex(x, y, 0))
        if dist < smallest_dist:
          smallest_dist = dist
          closest_edge = edge
      if smallest_dist * scale < 10:
        self._edge_hover = closest_edge
        update_view = True

    if self._states.select_text and self._edge_hover is None and self._kp_hover is None:
      for text_tuple in sketch.get_texts():
        text = text_tuple[1]
        key_point = text.key_point
        x1 = key_point.x
        y1 = key_point.y
        if text.horizontal_alignment == Text.Left:
          x1 -= text.height * len(text.value) / 2
        elif text.horizontal_alignment == Text.Right:
          x1 += text.height * len(text.value) / 2
        if text.vertical_alignment == Text.Top:
          y1 += text.height / 2
        elif text.vertical_alignment == Text.Bottom:
          y1 -= text.height / 2
        if abs(y1 - y) < text.height and abs(x1 - x) < text.height * len(text.value) / 2:
          self._text_hover = text
          update_view = True
          break

    if self._states.set_similar_x and self._kp_hover is not None:
      self._similar_coords.clear()
      for kp_tuple in key_points:
        key_point = kp_tuple[1]
        x1 = key_point.x
        if abs(x1 - self._kp_hover.x) < self.similar_threshold:
          self._similar_coords.add(key_point)
          update_view = True

    if self._states.set_similar_y and self._kp_hover is not None:
      self._similar_coords.clear()
      for kp_tuple in key_points:
        key_point = kp_tuple[1]
        y1 = key_point.y
        if abs(y1 - self._kp_hover.y) < self.similar_threshold:
          self._similar_coords.add(key_point)
          update_view = True


    if self._states.select_area and self._kp_hover is None and self._edge_hover is None:
      for area_tuple in sketch.get_areas():
        area = area_tuple[1]
        if area.inside(Vertex(x, y, 0)):
          self._area_hover = area
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
    position = q_mouse_event.pos()

    half_width = self.width() / 2
    half_height = self.height() / 2
    scale = self._scale
    x = (self._mouse_position.x() - half_width) / scale - self._offset.x
    y = -((self._mouse_position.y() - half_height) / scale + self._offset.y)

    #                             ****    Find Similar params    ****
    if self._states.set_similar_x or self._states.set_similar_y:
      params = []
      for param_tuple in self._sketch.get_all_parameters():
        params.append(param_tuple[1].name)
      value = QInputDialog.getItem(self, "Set parameter", "Parameter:", params, 0, True)
      if self._states.set_similar_x and value[1] == QDialog.Accepted:
        self._states.set_similar_x = False
        set_similar_x(self._doc, self._sketch, self._similar_coords, value[0])
      else:
        self._states.set_similar_x = False
      if self._states.set_similar_y and value[1] == QDialog.Accepted:
        self._states.set_similar_y = False
        set_similar_y(self._doc, self._sketch, self._similar_coords, value[0])
      else:
        self._states.set_similar_y = False

    #                             ****    Text select    ****
    if self._states.select_text:
      if self._text_hover is not None:
        if self._states.multi_select:
          self._selected_texts.append(self._text_hover)
        else:
          self._selected_texts = [self._text_hover]
      else:
        self._selected_texts = []
      self._main_window.on_text_selection_changed_in_view(self._selected_texts)

    #                             ****    Keypoint move    ****
    if self._states.left_button_hold and self._kp_hover is not None:
      if self._kp_hover in self._selected_key_points:
        self._kp_move = self._kp_hover

    #                             ****    Edge select    ****
    if self._states.select_edge and self._edge_hover is not None and self._kp_hover is None:
      if self._states.multi_select:
        if self._edge_hover in self._selected_edges:
          self._selected_edges.remove(self._edge_hover)
        else:
          self._selected_edges.append(self._edge_hover)
      else:
        self._selected_edges = [self._edge_hover]
      self.update()
      self._main_window.on_edge_selection_changed_in_view(self._selected_edges)
    elif self._states.select_edge and self._edge_hover is None:
      self._selected_edges = []
      self.update()
      self._main_window.on_edge_selection_changed_in_view(self._selected_edges)

    #                             ****    Keypoint select    ****
    if self._kp_hover is not None and self._states.select_kp:
      if self._states.multi_select:
        self._selected_key_points.append(self._kp_hover)
      else:
        self._selected_key_points = [self._kp_hover]
      self.update()
      self._main_window.on_kp_selection_changed_in_view(self._selected_key_points)
    elif self._kp_hover is None and self._states.select_kp and len(
        self._selected_edges) == 0 and not self._states.draw_line_edge:
      self._selected_key_points = []
      self.update()
      self._main_window.on_kp_selection_changed_in_view(self._selected_key_points)

    #                             ****    Area select    ****
    if self._states.select_area:
      if self._area_hover is not None:
        if self._states.multi_select:
          self._selected_areas.append(self._area_hover)
        else:
          self._selected_areas = [self._area_hover]

        self._selected_edges = []
        for area in self._selected_areas:
          for edge in area.get_edges():
            self._selected_edges.append(edge)
        self._main_window.on_edge_selection_changed_in_view(self._selected_edges)
        self.update()
      else:
        if not self._states.multi_select:
          self._selected_areas = []
          self.update()

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
    if self._is_dark_theme:
      axis_pen = QPen(QColor(40, 50, 80), 1)
      gradient.setColorAt(0, QColor(80, 80, 90))
      gradient.setColorAt(1, QColor(50, 50, 60))
    else:
      axis_pen = QPen(QColor(140, 150, 180), 1)
      gradient.setColorAt(0, QColor(220, 220, 230))
      gradient.setColorAt(1, QColor(170, 170, 180))
    qp.fillRect(event.rect(), gradient)
    qp.setRenderHint(QPainter.Antialiasing)

    cx = self._offset.x * self._scale + self.width() / 2
    cy = -self._offset.y * self._scale + self.height() / 2

    qp.setPen(axis_pen)
    if self.width() > cx > 0:
      qp.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
    if self.height() > cy > 0:
      qp.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

    self.draw_areas(event, qp)
    self.draw_edges(event, qp)
    self.draw_texts(event, qp)
    qp.end()

  def draw_texts(self, event, qp: QPainter):
    if self._sketch is None:
      return
    sc = self._scale
    half_width = self.width() / 2
    half_height = self.height() / 2
    center = Vertex(half_width, half_height)
    normal_pen = QPen(QColor(0, 0, 0), 2)
    kp_pen_hover = QPen(QColor(0, 120, 255), 3)
    kp_pen_hl = QPen(QColor(180, 50, 0), 3)
    qp.setPen(normal_pen)
    for text_tuple in self._sketch.get_texts():
      text = text_tuple[1]
      if type(text) is Text:
        draw_text(text, qp, sc, self._offset, center)
      elif type(text) is Attribute:
        draw_attribute(text, qp, sc, self._offset, center, {})
    if self._text_hover is not None:
      qp.setPen(kp_pen_hover)
      if type(self._text_hover) is Text:
        draw_text(self._text_hover, qp, sc, self._offset, center)
      elif type(self._text_hover) is Attribute:
        draw_attribute(self._text_hover, qp, sc, self._offset, center, {})
    qp.setPen(kp_pen_hl)
    for text in self._selected_texts:
      if type(text) is Text:
        draw_text(text, qp, sc, self._offset, center)
      elif type(text) is Attribute:
        draw_attribute(text, qp, sc, self._offset, center, {})

  def draw_edges(self, event, qp):
    pens = create_pens(self._doc, 6000)
    pens_hover = create_pens(self._doc, 12000, QColor(100, 100, 200))
    pens_select_high = create_pens(self._doc, 18000, QColor(255, 0, 0))
    pens_select = create_pens(self._doc, 6000, QColor(255, 255, 255))
    if self._is_dark_theme:
      kp_pen = QPen(QColor(0, 200, 200), 1)
      kp_pen_hl = QPen(QColor(190, 0, 0), 3)
      kp_pen_hover = QPen(QColor(0, 60, 150), 3)
    else:
      kp_pen = QPen(QColor(0, 100, 200), 1)
      kp_pen_hl = QPen(QColor(180, 50, 0), 3)
      kp_pen_hover = QPen(QColor(0, 120, 255), 3)
    half_width = self.width() / 2
    half_height = self.height() / 2
    center = Vertex(half_width, half_height)
    scale = self._scale
    if self._sketch is None:
      return

    edges = self._sketch.get_edges()

    for edge_tuple in edges:
      edge = edge_tuple[1]
      draw_edge(edge, qp, scale, self._offset, center, pens)

    for edge in self._selected_edges:
      draw_edge(edge, qp, scale, self._offset, center, pens_select_high)

    for edge in self._selected_edges:
      draw_edge(edge, qp, scale, self._offset, center, pens_select)

    if self._edge_hover is not None:
      draw_edge(self._edge_hover, qp, scale, self._offset, center, pens_hover)

    qp.setPen(pens['default'])

    key_points = self._sketch.get_key_points()
    for kp_tuple in key_points:
      qp.setPen(kp_pen)
      key_point = kp_tuple[1]

      if self._states.set_similar_x or self._states.set_similar_y:
        if key_point in self._similar_coords:
          qp.setPen(kp_pen_hl)
      if self._kp_hover is key_point and self._states.select_kp:
        qp.setPen(kp_pen_hover)

      if self._states.show_key_points or self._kp_hover is key_point or self._states.set_similar_x or self._states.set_similar_y:
        draw_kp(qp, key_point, scale, self._offset, center)

    qp.setPen(kp_pen_hl)

    for key_point in self._selected_key_points:
      draw_kp(qp, key_point, scale, self._offset, center)

  def draw_areas(self, event, qp: QPainter):
    if self._sketch is None:
      return
    # pens_select_high = create_pens(self._doc, 18000, QColor(255, 0, 0))
    area_brush = QBrush(QColor(150, 150, 150, 80))
    area_hover_brush = QBrush(QColor(150, 150, 200, 80))
    area_selected_brush = QBrush(QColor(150, 150, 200, 120))
    areas = self._sketch.get_areas()
    qp.setPen(Qt.NoPen)
    half_width = self.width() / 2
    half_height = self.height() / 2
    scale = self._scale
    center = Vertex(half_width, half_height)
    for area_tuple in areas:
      area = area_tuple[1]
      brush = area_brush
      if area in self._selected_areas:
        brush = area_selected_brush
      if area == self._area_hover:
        brush = area_hover_brush
      draw_area(area, qp, scale, self._offset, half_height, half_width, True, brush)

  def update_status(self):
    self._doc.set_status("")
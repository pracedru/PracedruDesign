from math import *

from PyQt5 import QtGui
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget

import Business
from Business.SketchActions import *
from Data.Sketch import Edge
from Data.Vertex import Vertex
from GUI import is_dark_theme
from GUI.Widgets.Drawers import *


class SketchViewWidget(QWidget):
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
        self._kp_hover = None
        self._kp_move = None
        self._edge_hover = None
        self.installEventFilter(self)

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

    def on_find_all_similar(self):
        if self._sketch is not None:
            find_all_similar(self._doc, self._sketch)

    def on_delete(self):
        txt = "Are you sure you want to delete these geometries?"
        ret = QMessageBox.warning(self, "Delete geometries?", txt, QMessageBox.Yes | QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            pass
            Business.remove_key_points(self._doc, self._selected_key_points)
            Business.remove_edges(self._doc, self._selected_edges)
            Business.remove_areas(self._doc, self._selected_areas)
            self._selected_key_points.clear()
            self._selected_edges.clear()
            self._selected_areas.clear()

    def set_selected_key_points(self, selected_key_points):
        self._selected_key_points = selected_key_points
        self.update()

    def set_selected_edges(self, selected_edges):
        self._selected_edges = selected_edges
        self.update()

    def on_escape(self):
        self._states.set_similar_x = False
        self._states.set_similar_y = False
        self._states.draw_line_edge = False
        self._states.create_area = False
        self._states.set_fillet_kp = False
        self._main_window.update_ribbon_state()

    def on_add_line(self):
        self.on_escape()
        self._states.select_kp = True
        self._states.draw_line_edge = True
        self._main_window.update_ribbon_state()

    def set_sketch(self, sketch):
        self._sketch = sketch
        self.update()

    def mouseReleaseEvent(self, q_mouse_event):
        if q_mouse_event.button() == 4:
            self._states.middle_button_hold = False
            return
        if q_mouse_event.button() == 1:
            self._states.left_button_hold = False
            self._kp_move = None
            return

    def mouseMoveEvent(self, q_mouse_event):
        position = q_mouse_event.pos()
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
            self._offset.x -= mouse_move_x/scale
            self._offset.y += mouse_move_y/scale
        if self._states.left_button_hold:
            if self._kp_move is not None:
                if self._kp_move.get_x_parameter() is None:
                    self._kp_move.x = x
                if self._kp_move.get_y_parameter() is None:
                    self._kp_move.y = y
        self._kp_hover = None
        self._edge_hover = None
        if self._states.select_kp:
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                x1 = key_point.x
                y1 = key_point.y
                if abs(x1 - x) < 5 / scale and abs(y1 - y) < 5 / scale:
                    self._kp_hover = key_point
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

        if self._states.set_similar_x and self._kp_hover is not None:
            self._similar_coords.clear()
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                x1 = key_point.x
                if abs(x1 - self._kp_hover.x) < self.similar_threshold:
                    self._similar_coords.add(key_point)

        if self._states.set_similar_y and self._kp_hover is not None:
            self._similar_coords.clear()
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                y1 = key_point.y
                if abs(y1 - self._kp_hover.y) < self.similar_threshold:
                    self._similar_coords.add(key_point)

        if self._states.set_similar_x or self._states.select_kp or self._states.select_edge or self._states.set_similar_y:
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

        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        x = (self._mouse_position.x() - width) / scale - self._offset.x
        y = -((self._mouse_position.y() - height) / scale + self._offset.y)
        if self._states.set_similar_x or self._states.set_similar_y:
            params = []
            for param_tuple in self._doc.get_parameters().get_all_parameters():
                params.append(param_tuple[1].name)
            value = QInputDialog.getItem(self, "Set parameter", "Parameter:", params, 0, True)
        if self._states.set_similar_x and value[1] == QDialog.Accepted:
            self._states.set_similar_x = False
            Business.set_similar_x(self._doc, self._similar_coords, value[0])
        else:
            self._states.set_similar_x = False
        if self._states.set_similar_y and value[1] == QDialog.Accepted:
            self._states.set_similar_y = False
            Business.set_similar_y(self._doc, self._similar_coords, value[0])
        else:
            self._states.set_similar_y = False

        if self._states.left_button_hold and self._kp_hover is not None:
            if self._kp_hover in self._selected_key_points:
                self._kp_move = self._kp_hover
        if self._states.select_edge and self._edge_hover is not None and self._kp_hover is None:
            if self._states.multi_select:
                if self._edge_hover in self._selected_edges:
                    self._selected_edges.remove(self._edge_hover)
                else:
                    self._selected_edges.append(self._edge_hover)
            else:
                self._selected_edges = [self._edge_hover]
            self.update()
            # self.parent().on_edge_selection_changed_in_view(self._selected_edges)
        elif self._states.select_edge and self._edge_hover is None:
            self._selected_edges = []
            self.update()
            # self.parent().on_edge_selection_changed_in_view(self._selected_edges)

        if self._kp_hover is not None and self._states.select_kp:
            if self._states.multi_select or self._states.draw_line_edge:
                self._selected_key_points.append(self._kp_hover)
            else:
                self._selected_key_points = [self._kp_hover]
            self.update()
            # self.parent().on_kp_selection_changed_in_view(self._selected_key_points)
        elif self._kp_hover is None and self._states.select_kp and len(self._selected_edges) == 0 and not self._states.draw_line_edge:
            self._selected_key_points = []
            self.update()
            # self.parent().on_kp_selection_changed_in_view(self._selected_key_points)

        if self._states.draw_line_edge:
            doc = self._doc
            sketch = self._sketch
            if self._kp_hover is None:
                coincident_threshold = 5/scale
                kp = create_key_point(doc, sketch, x, y, 0.0, coincident_threshold)
                self._selected_key_points.append(kp)
            if len(self._selected_key_points) == 2:
                sketch.create_line_edge(self._selected_key_points[0], self._selected_key_points[1])
                self._selected_key_points.clear()
        if self._states.set_fillet_kp:
            if self._kp_hover is not None:
                doc = self._doc
                edges = self._kp_hover.get_edges()
                if len(edges) == 2:
                    param_name = "New Fillet radius"
                    param = self._doc.get_parameters().get_parameter_by_name(param_name)
                    if param is None:
                        param = self._doc.get_parameters().create_parameter(param_name, 1.0)
                    create_fillet(self._doc, sketch, self._kp_hover, param)
                else:
                    pass

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
        self.draw_edges(event, qp)
        qp.end()

    def draw_edges(self, event, qp):
        edge_hover_pen = QPen(QtGui.QColor(100, 100, 200), 4)
        normal_pen = QPen(QtGui.QColor(0, 0, 0), 2)
        select_pen_high = QPen(QtGui.QColor(255, 0, 0), 6)
        select_pen = QPen(QtGui.QColor(255, 255, 255), 2)
        if self._is_dark_theme:
            axis_pen = QPen(QtGui.QColor(40, 50, 80), 1)
            kp_pen = QPen(QtGui.QColor(0, 200, 200), 1)
            kp_pen_hl = QPen(QtGui.QColor(190, 0, 0), 3)
            kp_pen_hover = QPen(QtGui.QColor(0, 60, 150), 3)
        else:
            axis_pen = QPen(QtGui.QColor(140, 150, 180), 1)
            kp_pen = QPen(QtGui.QColor(0, 100, 200), 1)
            kp_pen_hl = QPen(QtGui.QColor(180, 50, 0), 3)
            kp_pen_hover = QPen(QtGui.QColor(0, 120, 255), 3)
        half_width = self.width() / 2
        half_height = self.height() / 2
        center = Vertex(half_width, half_height)
        scale = self._scale
        if self._sketch is None:
            return

        edges = self._sketch.get_edges()

        cx = self._offset.x * scale + half_width
        cy = -self._offset.y * scale + half_height
        qp.setPen(axis_pen)
        if self.width() > cx > 0:
            qp.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
        if self.height() > cy > 0:
            qp.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

        qp.setPen(normal_pen)
        for edge_tuple in edges:
            edge = edge_tuple[1]
            draw_edge(edge, qp, scale, self._offset, center)

        for edge in self._selected_edges:
            qp.setPen(select_pen_high)
            draw_edge(edge, qp, scale, self._offset, center)

        for edge in self._selected_edges:
            qp.setPen(select_pen)
            draw_edge(edge, qp, scale, self._offset, center)

        if self._edge_hover is not None:
            qp.setPen(edge_hover_pen)
            draw_edge(self._edge_hover, qp, scale, self._offset, center)
        qp.setPen(normal_pen)

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

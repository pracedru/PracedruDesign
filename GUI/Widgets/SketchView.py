from PyQt5 import QtGui
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtGui import QPen

from PyQt5.QtWidgets import QWidget
from math import *

from Data.Sketch import Edge
from Data.Vertex import Vertex
from GUI import is_dark_theme


class SketchViewWidget(QWidget):
    def __init__(self, parent, document):
        QWidget.__init__(self, parent)
        self._doc = document
        self._is_dark_theme = is_dark_theme()
        self._sketch = None
        self._scale = 1.0
        self._offset = Vertex()

    def wheelEvent(self, event):
        if self.mouse_position is not None:
            delta = event.angleDelta().y() / 8
            if self._scale + self._scale * (delta * 0.01) > 0:
                self._scale += self._scale * (delta * 0.01)
                width = self.width() / 2
                height = self.height() / 2
                scale = self._scale
                x = self.mouse_position.x() - width
                y = self.mouse_position.y() - height
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
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        if self._sketch is None:
            return

        edges = self._sketch.get_edges()

        cx = self._offset.x * scale + width
        cy = -self._offset.y * scale + height
        qp.setPen(axis_pen)
        if self.width() > cx > 0:
            qp.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
        if self.height() > cy > 0:
            qp.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

        qp.setPen(normal_pen)
        for edge_tuple in edges:
            edge = edge_tuple[1]
            self.draw_edge(edge, qp, scale, height, width)

        for edge in self._selected_edges:
            qp.setPen(select_pen_high)
            self.draw_edge(edge, qp, scale, height, width)

        for edge in self._selected_edges:
            qp.setPen(select_pen)
            self.draw_edge(edge, qp, scale, height, width)

        if self._edge_hover is not None:
            qp.setPen(edge_hover_pen)
            self.draw_edge(self._edge_hover, qp, scale, height, width)
        qp.setPen(normal_pen)

        key_points = edges_object.get_key_points()
        for kp_tuple in key_points:
            qp.setPen(kp_pen)
            key_point = kp_tuple[1]
            x1 = (key_point.x + self._offset.x) * scale + width
            y1 = -(key_point.y + self._offset.y) * scale + height
            if self._set_similar_x or self._set_similar_y:
                if key_point in self._similar_coords:
                    qp.setPen(kp_pen_hl)
            if self._kp_hover is key_point and self._select_kp:
                qp.setPen(kp_pen_hover)

            if self.show_key_points or self._kp_hover is key_point or self._set_similar_x or self._set_similar_y:
                qp.drawEllipse(QPointF(x1, y1), 4, 4)

        qp.setPen(kp_pen_hl)
        for key_point in self._selected_key_points:
            x1 = (key_point.x + self._offset.x) * scale + width
            y1 = -(key_point.y + self._offset.y) * scale + height
            qp.drawEllipse(QPointF(x1, y1), 4, 4)

    def draw_kp(self, qp, key_point, scale, width, height):
        x1 = (key_point.x + self._offset.x) * scale + width
        y1 = -(key_point.y + self._offset.y) * scale + height
        qp.drawEllipse(QPointF(x1, y1), 4, 4)

    def draw_edge(self, edge, qp, scale, height, width):
        if edge is not None:
            key_points = edge.get_key_points()
            if edge.type == Edge.LineEdge:
                edges_list = key_points[0].get_edges()
                fillet1 = None
                other_edge1 = None
                for edge_item in edges_list:
                    if edge_item.type == Edge.FilletLineEdge:
                        fillet1 = edge_item
                    elif edge_item is not edge:
                        other_edge1 = edge_item
                edges_list = key_points[1].get_edges()
                fillet2 = None
                other_edge2 = None
                for edge_item in edges_list:
                    if edge_item.type == Edge.FilletLineEdge:
                        fillet2 = edge_item
                    elif edge_item is not edge:
                        other_edge2 = edge_item
                fillet_offset_x = 0
                fillet_offset_y = 0

                if fillet1 is not None and other_edge1 is not None:
                    r = fillet1.get_meta_data("r")
                    a1 = edge.angle(key_points[0])
                    kp1 = edge.get_other_kp(key_points[0])
                    kp2 = other_edge1.get_other_kp(key_points[0])
                    abtw = key_points[0].angle_between_positive_minimized(kp1, kp2)
                    dist = -tan(abtw/2+pi/2)*r
                    fillet_offset_x = dist * cos(a1)
                    fillet_offset_y = dist * sin(a1)

                x1 = (key_points[0].x + fillet_offset_x + self._offset.x) * scale + width
                y1 = -(key_points[0].y + fillet_offset_y + self._offset.y) * scale + height

                fillet_offset_x = 0
                fillet_offset_y = 0

                if fillet2 is not None and other_edge2 is not None:
                    r = fillet2.get_meta_data("r")
                    a1 = edge.angle(key_points[1])
                    kp1 = edge.get_other_kp(key_points[1])
                    kp2 = other_edge2.get_other_kp(key_points[1])
                    abtw = key_points[1].angle_between_positive_minimized(kp2, kp1)
                    dist = -tan(abtw / 2+pi/2) * r
                    fillet_offset_x = dist * cos(a1)
                    fillet_offset_y = dist * sin(a1)

                x2 = (key_points[1].x + fillet_offset_x + self._offset.x) * scale + width
                y2 = -(key_points[1].y + fillet_offset_y + self._offset.y) * scale + height
                qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            elif edge.type == Edge.ArcEdge:
                cx = (key_points[0].x + self._offset.x) * scale + width
                cy = -(key_points[0].y + self._offset.y) * scale + height
                radius = edge.get_meta_data("r") * scale
                rect = QRectF(cx - radius, cy - 1 * radius, radius * 2, radius * 2)
                start_angle = edge.get_meta_data("sa") * 180 * 16 / pi
                end_angle = edge.get_meta_data("ea") * 180 * 16 / pi
                span = end_angle - start_angle
                if span < 0:
                    span += 2 * 180 * 16
                qp.drawArc(rect, start_angle, span)
            elif edge.type == Edge.FilletLineEdge:
                kp = key_points[0]
                edges_list = kp.get_edges()
                edges_list.remove(edge)
                if len(edges_list) > 1:
                    edge1 = edges_list[0]
                    edge2 = edges_list[1]
                    kp1 = edge1.get_other_kp(kp)
                    kp2 = edge2.get_other_kp(kp)
                    angle_between = kp.angle_between_untouched(kp1, kp2)
                    radius = edge.get_meta_data("r")
                    dist = radius / sin(angle_between/2)
                    radius *= scale
                    angle_larger = False
                    while angle_between < -2*pi:
                        angle_between += 2*pi
                    while angle_between > 2*pi:
                        angle_between -= 2*pi
                    if abs(angle_between) > pi:
                        angle_larger = True
                        angle = edge1.angle(kp) + angle_between / 2 + pi
                    else:
                        angle = edge1.angle(kp) + angle_between / 2
                    if dist < 0:
                        angle += pi
                    cx = (key_points[0].x + dist * cos(angle) + self._offset.x) * scale + width
                    cy = -(key_points[0].y + dist * sin(angle) + self._offset.y) * scale + height
                    rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

                    if angle_between < 0:
                        if angle_larger:
                            end_angle = (edge1.angle(kp) - pi/2) * 180 * 16 / pi
                            start_angle = (edge2.angle(kp) + pi/2) * 180 * 16 / pi
                        else:
                            end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
                            start_angle = (edge2.angle(kp) + 3*pi / 2) * 180 * 16 / pi
                    else:
                        if angle_larger:
                            start_angle = (edge1.angle(kp) + pi/2) * 180 * 16 / pi
                            end_angle = (edge2.angle(kp) - pi/2) * 180 * 16 / pi
                        else:
                            end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
                            start_angle = (edge2.angle(kp) - pi / 2) * 180 * 16 / pi
                            end_angle += pi * 180 * 16 / pi
                            start_angle += pi * 180 * 16 / pi
                    span = end_angle-start_angle
                    qp.drawArc(rect, start_angle, span)
from math import *

from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QPainter

from Data.Sketch import Edge, Text


def draw_sketch(qp: QPainter, sketch, scale, offset, center):
    edges = sketch.get_edges()
    for edge_tuple in edges:
        edge = edge_tuple[1]
        draw_edge(edge, qp, scale, offset, center)
    for text_tuple in sketch.get_texts():
        text = text_tuple[1]
        draw_text(text, qp, scale, offset, center)


def draw_text(text, qp: QPainter, scale, offset, center):
    key_point = text.key_point
    factor = 10 / text.height
    font = QFont("Helvetica", text.height*factor)
    fm = QFontMetrics(font)
    qp.setFont(font)
    width = fm.width(text.value)/factor
    qp.save()
    x1 = (key_point.x + offset.x)*scale + center.x
    y1 = -(key_point.y + offset.y)*scale + center.y
    if text.horizontal_alignment == Text.Left:
        x1 -= width*scale
    elif text.horizontal_alignment == Text.Center:
        x1 -= width*scale/2
    if text.vertical_alignment == Text.Top:
        y1 -= text.height*scale
    elif text.vertical_alignment == Text.Center:
        y1 -= text.height * 2 * scale/2
    qp.translate(x1, y1)
    qp.scale(scale/factor, scale/factor)
    qp.rotate(text.angle*180/pi)
    qp.drawText(QRectF(0, 0, width*factor, text.height*2*factor), Qt.AlignHCenter | Qt.AlignVCenter, text.value)
    qp.restore()


def draw_edge(edge: Edge, qp: QPainter, scale, offset, center):
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

            x1 = (key_points[0].x + fillet_offset_x + offset.x) * scale + center.x
            y1 = -(key_points[0].y + fillet_offset_y + offset.y) * scale + center.y

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

            x2 = (key_points[1].x + fillet_offset_x + offset.x) * scale + center.x
            y2 = -(key_points[1].y + fillet_offset_y + offset.y) * scale + center.y
            qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        elif edge.type == Edge.ArcEdge:
            cx = (key_points[0].x + offset.x) * scale + center.x
            cy = -(key_points[0].y + offset.y) * scale + center.y
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
                cx = (key_points[0].x + dist * cos(angle) + offset.x) * scale + center.x
                cy = -(key_points[0].y + dist * sin(angle) + offset.y) * scale + center.y
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


def draw_kp(qp, key_point, scale, offset, center):
    x1 = (key_point.x + offset.x) * scale + center.x
    y1 = -(key_point.y + offset.y) * scale + center.y
    qp.drawEllipse(QPointF(x1, y1), 4, 4)

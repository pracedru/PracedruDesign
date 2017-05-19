
from math import *

from PyQt5.QtCore import QPointF, Qt, QRectF
from PyQt5.QtGui import QBrush, QFont, QPen, QPainter, QFontMetrics, QColor, QPainterPath

from Data.Nurbs import Nurbs
from Data.Sketch import Edge, Text, Attribute


def create_pens(document, scale, color_override=None):
    pens = {}
    color = color_override
    if color_override is None:
        color = QColor(0, 0, 0)
    pens['default'] = QPen(QColor(0, 0, 0), 0.0002 * scale)
    for style in document.get_styles().get_edge_styles():
        color = color_override
        if color_override is None:
            c = style[1].color
            color =QColor(c[0], c[1], c[2])
        pens[style[1].uid] = QPen(color, style[1].thickness * scale)
    return pens


def draw_sketch(qp: QPainter, sketch, scale, offset, center, pens, fields):
    edges = sketch.get_edges()
    for edge_tuple in edges:
        edge = edge_tuple[1]
        draw_edge(edge, qp, scale, offset, center, pens)
    for text_tuple in sketch.get_texts():
        text = text_tuple[1]
        if type(text) is Attribute:
            value = None
            if text.name in fields:
                value = fields[text.name].value
            draw_attribute(text, qp, scale, offset, center, True, value)
        else:
            draw_text(text, qp, scale, offset, center)


def draw_attribute(text, qp: QPainter, scale, offset, center, show_value=False, value=None):
    key_point = text.key_point
    factor = 10 / text.height
    font = QFont("Helvetica", text.height*factor)
    fm = QFontMetrics(font)
    qp.setFont(font)
    if show_value:
        if value is None:
            txt = text.value
        else:
            txt = value
    else:
        txt = "<" + text.name + ">"
    width = fm.width(txt)/factor
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
        y1 -= text.height * 2.3 * scale/2
    qp.translate(x1, y1)
    qp.scale(scale/factor, scale/factor)
    qp.rotate(text.angle*180/pi)
    qp.drawText(QRectF(0, 0, width*factor, text.height*2*factor), Qt.AlignHCenter | Qt.AlignVCenter, txt)
    qp.restore()


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
        y1 -= text.height * 2.3 * scale/2
    qp.translate(x1, y1)
    qp.scale(scale/factor, scale/factor)
    qp.rotate(text.angle*180/pi)
    qp.drawText(QRectF(0, 0, width*factor, text.height*2*factor), Qt.AlignHCenter | Qt.AlignVCenter, text.value)
    qp.restore()


def draw_edge(edge: Edge, qp: QPainter, scale, offset, center, pens):
    if edge.style is None:
        qp.setPen(pens['default'])
    else:
        qp.setPen(pens[edge.style.uid])
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
        elif edge.type == Edge.CircleEdge:
            cx = (key_points[0].x + offset.x) * scale + center.x
            cy = -(key_points[0].y + offset.y) * scale + center.y
            radius = edge.get_meta_data("r") * scale
            rect = QRectF(cx - radius, cy - 1 * radius, radius * 2, radius * 2)

            qp.drawEllipse(rect)
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
        elif edge.type == Edge.NurbsEdge:
            kps = edge.get_key_points()
            nurbs = Nurbs()
            controls = []

            for i in range(0, len(kps)):
                controls.append(kps[i].xyz)

            if len(controls)>2:
                nurbs.set_controls(controls)
                p1 = nurbs.C(0)
                divs = len(controls)*15
                for i in range(1, divs):
                    p2 = nurbs.C(i/divs)
                    x1 = (p1[0] + offset.x) * scale + center.x
                    y1 = -(p1[1] + offset.y) * scale + center.y
                    x2 = (p2[0] + offset.x) * scale + center.x
                    y2 = -(p2[1] + offset.y) * scale + center.y
                    qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                    p1 = p2
                p2 = controls[len(controls)-1]
                x1 = (p1[0] + offset.x) * scale + center.x
                y1 = -(p1[1] + offset.y) * scale + center.y
                x2 = (p2[0] + offset.x) * scale + center.x
                y2 = -(p2[1] + offset.y) * scale + center.y
                qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            else:
                for i in range(1, len(kps)):
                    kp1 = kps[i - 1]
                    kp2 = kps[i]
                    x1 = (kp1.x + offset.x) * scale + center.x
                    y1 = -(kp1.y + offset.y) * scale + center.y
                    x2 = (kp2.x + offset.x) * scale + center.x
                    y2 = -(kp2.y + offset.y) * scale + center.y
                    qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def draw_kp(qp, key_point, scale, offset, center):
    x1 = (key_point.x + offset.x) * scale + center.x
    y1 = -(key_point.y + offset.y) * scale + center.y
    qp.drawEllipse(QPointF(x1, y1), 4, 4)


def draw_area(area, qp, scale, offset, height, width, show_names, brush):
    path = QPainterPath()
    first_kp = True
    x_max = 0
    y_max = 0
    x_min = 0
    y_min = 0
    counter = 0
    for kp in area.get_key_points():
        x = (kp.x + offset.x) * scale + width
        y = -(kp.y + offset.y) * scale + height
        if first_kp:
            path.moveTo(QPointF(x, y))
            first_kp = False
            x_max = x
            y_max = y
            x_min = x
            y_min = y
        else:
            edge = area.get_edges()[counter - 1]
            if edge.type == Edge.ArcEdge:
                center_kp = edge.get_key_points()[0]
                cx = (center_kp.x + offset.x) * scale + width
                cy = -(center_kp.y + offset.y) * scale + height
                radius = edge.get_meta_data('r')
                start_angle = edge.get_meta_data('sa')
                end_angle = edge.get_meta_data('ea')
                diff = (x - (cx + cos(end_angle) * radius * scale)) + (y - (cy - sin(end_angle) * radius * scale))
                end_angle *= 180 / pi
                start_angle *= 180 / pi
                sweep_length = end_angle - start_angle
                if abs(diff) > 0.01 * radius * scale:
                    start_angle = end_angle
                    sweep_length = -sweep_length

                path.arcTo(cx - radius * scale, cy - radius * scale, scale * radius * 2, scale * radius * 2, start_angle, sweep_length)
            else:
                path.lineTo(QPointF(x, y))
            if x > x_max:
                x_max = x
            if x < x_min:
                x_min = x
            if y > y_max:
                y_max = y
            if y < y_min:
                y_min = y
        counter += 1

    #  if area in selected_areas:
    #    qp.fillPath(path, QBrush(QColor(150, 150, 250, 180)))
    # elif area == self._area_hover:
    #    qp.fillPath(path, QBrush(QColor(150, 150, 180, 180)))
    # else:
    qp.fillPath(path, brush)

    if show_names:
        if x_max - x_min < (y_max - y_min) * 0.75:
            qp.rotate(-90)
            qp.drawText(QRectF(-y_min, x_min, y_min - y_max, x_max - x_min), Qt.AlignCenter, area.name)
            qp.rotate(90)
        else:
            qp.drawText(QRectF(x_min, y_min, x_max - x_min, y_max - y_min), Qt.AlignCenter, area.name)
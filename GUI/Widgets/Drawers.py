from math import *

from PyQt5.QtCore import QPointF, Qt, QRectF
from PyQt5.QtGui import QBrush, QFont, QPen, QPainter, QFontMetrics, QColor, QPainterPath

from Data.Nurbs import Nurbs
from Data.Sketch import *
from Data.Vertex import Vertex



def create_pens(document, scale, color_override=None):
  """
  Creates pens for all edge styles that are defined in the document
  :param document:
  :param scale: The pen thickness scale to be used
  :param color_override: Overrides the color defined in the style
  :return:
  """
  pens = {}
  color = color_override
  if color_override is None:
    color = QColor(0, 0, 0)
  pens['default'] = QPen(QColor(0, 0, 0), 0.0002 * scale)
  for style in document.get_styles().get_edge_styles():
    color = color_override
    if color_override is None:
      c = style[1].color
      color = QColor(c[0], c[1], c[2])
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
  font = QFont("Helvetica", text.height * factor)
  fm = QFontMetrics(font)
  qp.setFont(font)
  if show_value:
    if value is None:
      txt = text.value
    else:
      txt = value
  else:
    txt = "<" + text.name + ">"
  width = fm.width(txt) / factor
  qp.save()
  x1 = (key_point.x + offset.x) * scale + center.x
  y1 = -(key_point.y + offset.y) * scale + center.y
  if text.horizontal_alignment == Text.Left:
    x1 -= width * scale
  elif text.horizontal_alignment == Text.Center:
    x1 -= width * scale / 2
  if text.vertical_alignment == Text.Top:
    y1 -= text.height * 2 * scale
  elif text.vertical_alignment == Text.Center:
    y1 -= text.height * 2 * scale / 2
  qp.translate(x1, y1)
  qp.scale(scale / factor, scale / factor)
  qp.rotate(text.angle * 180 / pi)
  qp.drawText(QRectF(0, 0, width * factor, text.height * 2 * factor), Qt.AlignHCenter | Qt.AlignVCenter, txt)
  qp.restore()


def draw_text(text, qp: QPainter, scale, offset, center):
  key_point = text.key_point
  factor = 10 / text.height  # Factor takes care of wierd bug in Qt with fonts that are smaller than 1 in height
  font = QFont("Helvetica", text.height * factor)
  fm = QFontMetrics(font)
  qp.setFont(font)
  width = fm.width(text.value) / factor
  qp.save()
  x1 = (key_point.x + offset.x) * scale + center.x
  y1 = -(key_point.y + offset.y) * scale + center.y
  if text.horizontal_alignment == Text.Left:
    x1 -= width * scale
  elif text.horizontal_alignment == Text.Center:
    x1 -= width * scale / 2
  if text.vertical_alignment == Text.Top:
    y1 -= text.height * 2 * scale
  elif text.vertical_alignment == Text.Center:
    y1 -= text.height * 2 * scale / 2
  qp.translate(x1, y1)
  qp.scale(scale / factor, scale / factor)
  qp.rotate(text.angle * 180 / pi)
  qp.drawText(QRectF(0, 0, width * factor, text.height * 2 * factor), Qt.AlignHCenter | Qt.AlignVCenter, text.value)
  # qp.drawRect(QRectF(0, 0, width*factor, text.height*2*factor))
  qp.restore()


def get_fillet_offset_distance(fillet_kp, r, edge1, edge2):
  kp1 = edge1.get_other_kp(fillet_kp)
  kp2 = edge2.get_other_kp(fillet_kp)
  abtw = fillet_kp.angle_between_positive_minimized(kp1, kp2)
  dist = -tan(abtw / 2 + pi / 2) * r
  return dist


def draw_edge(edge: Edge, qp: QPainter, scale, offset, center, pens):
  if edge.style is None:
    qp.setPen(pens['default'])
  else:
    qp.setPen(pens[edge.style.uid])
  if edge is not None:
    key_points = edge.get_key_points()
    if edge.type == EdgeType.LineEdge:
      edges_list = key_points[0].get_edges()
      fillet1 = None
      other_edge1 = None
      for edge_item in edges_list:
        if edge_item.type == EdgeType.FilletLineEdge:
          fillet1 = edge_item
        elif edge_item is not edge:
          other_edge1 = edge_item
      edges_list = key_points[1].get_edges()
      fillet2 = None
      other_edge2 = None
      for edge_item in edges_list:
        if edge_item.type == EdgeType.FilletLineEdge:
          fillet2 = edge_item
        elif edge_item is not edge:
          other_edge2 = edge_item
      fillet_offset_x = 0
      fillet_offset_y = 0

      if fillet1 is not None and other_edge1 is not None:
        r = fillet1.get_meta_data("r")
        a1 = edge.angle(key_points[0])
        dist = get_fillet_offset_distance(key_points[0], r, edge, other_edge1)
        fillet_offset_x = dist * cos(a1)
        fillet_offset_y = dist * sin(a1)

      x1 = (key_points[0].x + fillet_offset_x + offset.x) * scale + center.x
      y1 = -(key_points[0].y + fillet_offset_y + offset.y) * scale + center.y

      fillet_offset_x = 0
      fillet_offset_y = 0

      if fillet2 is not None and other_edge2 is not None:
        r = fillet2.get_meta_data("r")
        a1 = edge.angle(key_points[1])
        dist = get_fillet_offset_distance(key_points[1], r, edge, other_edge2)
        fillet_offset_x = dist * cos(a1)
        fillet_offset_y = dist * sin(a1)

      x2 = (key_points[1].x + fillet_offset_x + offset.x) * scale + center.x
      y2 = -(key_points[1].y + fillet_offset_y + offset.y) * scale + center.y
      qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    elif edge.type == EdgeType.ArcEdge:
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
    elif edge.type == EdgeType.CircleEdge:
      cx = (key_points[0].x + offset.x) * scale + center.x
      cy = -(key_points[0].y + offset.y) * scale + center.y
      radius = edge.get_meta_data("r") * scale
      rect = QRectF(cx - radius, cy - 1 * radius, radius * 2, radius * 2)

      qp.drawEllipse(rect)
    elif edge.type == EdgeType.FilletLineEdge:
      kp = key_points[0]
      edges_list = kp.get_edges()
      if edge in edges_list:
        edges_list.remove(edge)
      if len(edges_list) > 1:
        edge1 = edges_list[0]
        edge2 = edges_list[1]
        kp1 = edge1.get_other_kp(kp)
        kp2 = edge2.get_other_kp(kp)
        angle_between = kp.angle_between_untouched(kp1, kp2)
        radius = edge.get_meta_data("r")
        dist = radius / sin(angle_between / 2)
        radius *= scale
        angle_larger = False
        while angle_between < -2 * pi:
          angle_between += 2 * pi
        while angle_between > 2 * pi:
          angle_between -= 2 * pi
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
            end_angle = (edge1.angle(kp) - pi / 2) * 180 * 16 / pi
            start_angle = (edge2.angle(kp) + pi / 2) * 180 * 16 / pi
          else:
            end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
            start_angle = (edge2.angle(kp) + 3 * pi / 2) * 180 * 16 / pi
        else:
          if angle_larger:
            start_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
            end_angle = (edge2.angle(kp) - pi / 2) * 180 * 16 / pi
          else:
            end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
            start_angle = (edge2.angle(kp) - pi / 2) * 180 * 16 / pi
            end_angle += pi * 180 * 16 / pi
            start_angle += pi * 180 * 16 / pi
        span = end_angle - start_angle
        qp.drawArc(rect, start_angle, span)
    elif edge.type == EdgeType.NurbsEdge:
      draw_data = edge.get_draw_data()
      coords = draw_data['coords']
      x1 = None
      for coord in coords:
        x2 = (coord.x + offset.x) * scale + center.x
        y2 = -(coord.y + offset.y) * scale + center.y
        if x1 is not None:
          qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        x1 = x2
        y1 = y2


def draw_kp(qp, key_point, scale, offset, center):
  x1 = (key_point.x + offset.x) * scale + center.x
  y1 = -(key_point.y + offset.y) * scale + center.y
  qp.drawEllipse(QPointF(x1, y1), 4, 4)


def draw_area(area, qp, scale, offset, half_height, half_width, show_names, brush):

  first_kp = True
  x_max = 0
  y_max = 0
  x_min = 0
  y_min = 0
  counter = 0

  if type(area) == CompositeArea:
    area_path = get_area_path(area.base_area, scale, offset, half_height, half_width)
    path = area_path[0]
    for subarea in area.subtracted_areas:
      sub_area_path = get_area_path(subarea, scale, offset, half_height, half_width)
      subpath = sub_area_path[0]
      path = path.subtracted(subpath)
    qp.fillPath(path, brush)
  else:
    path = get_area_path(area, scale, offset, half_height, half_width)
    qp.fillPath(path[0], brush)


  if show_names:
    qp.setPen(QPen(QColor(0, 0, 0), 2))
    if x_max - x_min < (y_max - y_min) * 0.75:
      qp.rotate(-90)
      qp.drawText(QRectF(-y_min, x_min, y_min - y_max, x_max - x_min), Qt.AlignCenter, area.name)
      qp.rotate(90)
    else:
      qp.drawText(QRectF(x_min, y_min, x_max - x_min, y_max - y_min), Qt.AlignCenter, area.name)


def get_area_path(area, scale, offset, half_height, half_width):
  path = QPainterPath()
  first_kp = True
  x_max = 0
  y_max = 0
  x_min = 0
  y_min = 0
  counter = 0
  if area.get_edges()[0].type == EdgeType.CircleEdge:
    kp = area.get_inside_key_points()[0]
    r = area.get_edges()[0].get_meta_data('r')
    x = (kp.x + offset.x) * scale + half_width
    y = -(kp.y + offset.y) * scale + half_height

    x_max = x + r * scale
    x_min = x - r * scale
    y_max = y + r * scale
    y_min = y - r * scale
    path.addEllipse(QRectF(x-r*scale, y-r*scale, 2*r*scale, 2*r*scale))

  else:
    for kp in area.get_key_points():
      edges = kp.get_edges()
      is_fillet_kp = False
      fillet_dist = 0
      for edge in edges:
        if edge.type == EdgeType.FilletLineEdge:
          r = edge.get_meta_data("r")
          is_fillet_kp = True
          edge1 = None
          edge2 = None
          for e in edges:
            if e is not edge:
              edge1 = e
          for e in edges:
            if e is not edge and e is not edge1:
              edge2 = e
          fillet_dist = get_fillet_offset_distance(kp, r, edge1, edge2)
      if is_fillet_kp:
        if first_kp:
          kp_prev = area.get_key_points()[len(area.get_key_points()) - 2]
        else:
          kp_prev = area.get_key_points()[counter - 1]
        if counter + 1 == len(area.get_key_points()):
          kp_next = area.get_key_points()[1]
        else:
          kp_next = area.get_key_points()[counter + 1]
        angle = kp.angle2d(kp_prev)
        angle_next = kp.angle2d(kp_next)
        fillet_offset_x = fillet_dist * cos(angle_next)
        fillet_offset_y = fillet_dist * sin(angle_next)
        x = (kp.x + fillet_offset_x + offset.x) * scale + half_width
        y = -(kp.y + fillet_offset_y + offset.y) * scale + half_height
      else:
        x = (kp.x + offset.x) * scale + half_width
        y = -(kp.y + offset.y) * scale + half_height
      if first_kp:
        path.moveTo(QPointF(x, y))
        first_kp = False
        x_max = x
        y_max = y
        x_min = x
        y_min = y
      else:
        edge = area.get_edges()[counter - 1]
        if edge.type == EdgeType.ArcEdge:
          center_kp = edge.get_key_points()[0]
          cx = (center_kp.x + offset.x) * scale + half_width
          cy = -(center_kp.y + offset.y) * scale + half_height
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

          path.arcTo(cx - radius * scale, cy - radius * scale, scale * radius * 2, scale * radius * 2, start_angle,
                     sweep_length)
        elif is_fillet_kp:
          center_kp = Vertex(kp.x, kp.y, kp.z)
          fillet_offset_x = fillet_dist * cos(angle)
          fillet_offset_y = fillet_dist * sin(angle)
          center_kp.x += fillet_offset_x
          center_kp.y += fillet_offset_y

          angle1 = kp_next.angle2d(kp)

          angle_between = kp.angle_between(kp_prev, kp_next)
          if angle_between < 0 or angle_between < pi:
            angle_perp = angle + pi / 2
          else:
            angle_perp = angle - pi / 2
          center_kp.x += r * cos(angle_perp)
          center_kp.y += r * sin(angle_perp)

          cx = (center_kp.x + offset.x) * scale + half_width
          cy = -(center_kp.y + offset.y) * scale + half_height

          if angle_between < 0 or angle_between < pi:
            start_angle = (angle * 180 / pi) + 270
          else:
            start_angle = angle * 180 / pi + 90
          sweep_length = -(180 - angle_between * 180 / pi)
          path.arcTo(cx - r * scale, cy - r * scale, scale * r * 2, scale * r * 2, start_angle, sweep_length)

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

  return path, x_max, x_min, y_max, y_min
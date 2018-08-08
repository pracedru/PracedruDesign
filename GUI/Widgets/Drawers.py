from math import *

from PyQt5.QtCore import QPointF, Qt, QRectF
from PyQt5.QtGui import QBrush, QFont, QPen, QPainter, QFontMetrics, QColor, QPainterPath, QTransform

from Data.Nurbs import Nurbs
from Data.Sketch import *
from Data.Style import EdgeLineType
from Data.Vertex import Vertex


def scale_dash_pattern(dash_pattern, fat):
	new_dash_pattern = []
	for dash in dash_pattern:
		if fat != 0:
			dash = dash * (1 / (1 + fat))
		new_dash_pattern.append(dash)
	return new_dash_pattern


def get_pen_from_style(style, scale, color_override, fat):
	color = color_override
	if color_override is None:
		c = style.color
		color = QColor(c[0], c[1], c[2])
	pen = None

	if style.line_type == EdgeLineType.Continous:
		pen = QPen(color, style.thickness * scale + style.thickness * scale * fat, Qt.SolidLine)
	elif style.line_type == EdgeLineType.DashDot:
		pen = QPen(color, style.thickness * scale + style.thickness * scale * fat)
		pen.setDashPattern(scale_dash_pattern([10.0, 4.0, 1.0, 4.0], fat))
	elif style.line_type == EdgeLineType.DashDotDot:
		pen = QPen(color, style.thickness * scale + style.thickness * scale * fat)
		pen.setDashPattern(scale_dash_pattern([10.0, 4.0, 1.0, 4.0, 1.0, 4.0], fat))
	elif style.line_type == EdgeLineType.Dashed:
		pen = QPen(color, style.thickness * scale + style.thickness * scale * fat)
		pen.setDashPattern(scale_dash_pattern([10.0, 4.0], fat))
	elif style.line_type == EdgeLineType.DotDot:
		pen = QPen(color, style.thickness * scale + style.thickness * scale * fat, Qt.DotLine)
		pen.setDashPattern(scale_dash_pattern([2.0, 4.0], fat))
	else:
		pen = QPen(color, style.thickness * scale + style.thickness * scale * fat, Qt.SolidLine)

	return pen


def create_pens(document, scale, color_override=None, fat=0):
	"""
	Creates pens for all edge styles that are defined in the document
	:param document:
	:param scale: The pen thickness scale to be used
	:param color_override: Overrides the color defined in the style
	:return:
	"""
	pens = {}
	pens['default'] = QPen(QColor(0, 0, 0), 0.0002 * scale)
	for style in document.get_styles().get_edge_styles():
		pens[style.uid] = get_pen_from_style(style, scale, color_override, fat)
	return pens


def draw_sketch(qp: QPainter, sketch, scale, brush_scale, offset, center, pens, fields, instance=None):
	edges = sketch.get_edges()
	areas = sketch.get_areas()

	for area in areas:
		if area.brush is not None:
			brush = QBrush(QColor(0, 0, 0), Qt.HorPattern)
			transx = offset.x * scale + center.x
			transy = -offset.y * scale + center.y
			transform = QTransform().translate(transx, transy).scale(brush_scale, brush_scale).rotate(area.brush_rotation)
			brush.setTransform(transform)
			draw_area(area, qp, scale, offset, center.y, center.x, False, brush, instance)
	for edge in edges:
		draw_edge(edge, qp, scale, offset, center, pens, instance)
	for text in sketch.get_texts():
		if type(text) is Attribute:
			value = None
			if text.name in fields:
				value = fields[text.name].value
			draw_attribute(text, qp, scale, offset, center, instance, True, value)
		else:
			draw_text(text, qp, scale, offset, center, instance)

	for sketch_instance in sketch.sketch_instances:
		si = sketch_instance.sketch
		siscale = sketch_instance.scale * scale
		sioffset = (offset + sketch_instance.offset) / sketch_instance.scale
		draw_sketch(qp, si, siscale, brush_scale, sioffset, center, pens, fields, sketch_instance.uid)


def draw_attribute(text, qp: QPainter, scale, offset, center, instance=None, show_value=False, value=None):
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
	x1 = (key_point.get_instance_x(instance) + offset.x) * scale + center.x
	y1 = -(key_point.get_instance_y(instance) + offset.y) * scale + center.y
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


def draw_text(text, qp: QPainter, scale, offset, center, instance=None):
	key_point = text.key_point
	factor = 10 / text.height  # Factor takes care of wierd bug in Qt with fonts that are smaller than 1 in height
	font = QFont("Helvetica", text.height * factor)
	fm = QFontMetrics(font)
	qp.setFont(font)
	width = fm.width(text.value) / factor
	qp.save()
	x1 = (key_point.get_instance_x(instance) + offset.x) * scale + center.x
	y1 = -(key_point.get_instance_y(instance) + offset.y) * scale + center.y
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


def draw_edge(edge: Edge, qp: QPainter, scale, offset, center, pens, instance=None):
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
				r = fillet1.get_meta_data("r", instance)
				a1 = edge.angle(key_points[0])
				dist = get_fillet_offset_distance(key_points[0], r, edge, other_edge1)
				fillet_offset_x = dist * cos(a1)
				fillet_offset_y = dist * sin(a1)

			x1 = (key_points[0].get_instance_x(instance) + fillet_offset_x + offset.x) * scale + center.x
			y1 = -(key_points[0].get_instance_y(instance) + fillet_offset_y + offset.y) * scale + center.y

			fillet_offset_x = 0
			fillet_offset_y = 0

			if fillet2 is not None and other_edge2 is not None:
				r = fillet2.get_meta_data("r", instance)
				a1 = edge.angle(key_points[1])
				dist = get_fillet_offset_distance(key_points[1], r, edge, other_edge2)
				fillet_offset_x = dist * cos(a1)
				fillet_offset_y = dist * sin(a1)

			x2 = (key_points[1].get_instance_x(instance) + fillet_offset_x + offset.x) * scale + center.x
			y2 = -(key_points[1].get_instance_y(instance) + fillet_offset_y + offset.y) * scale + center.y
			qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
		elif edge.type == EdgeType.ArcEdge:
			cx = (key_points[0].get_instance_x(instance) + offset.x) * scale + center.x
			cy = -(key_points[0].get_instance_y(instance) + offset.y) * scale + center.y
			radius = edge.get_meta_data("r", instance) * scale
			rect = QRectF(cx - radius, cy - 1 * radius, radius * 2, radius * 2)
			start_angle = edge.get_meta_data("sa", instance) * 180 * 16 / pi
			end_angle = edge.get_meta_data("ea", instance) * 180 * 16 / pi
			span = end_angle - start_angle
			if span < 0:
				span += 2 * 180 * 16
			qp.drawArc(rect, start_angle, span)
		elif edge.type == EdgeType.CircleEdge:
			cx = (key_points[0].get_instance_x(instance) + offset.x) * scale + center.x
			cy = -(key_points[0].get_instance_y(instance) + offset.y) * scale + center.y
			radius = edge.get_meta_data("r", instance) * scale
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
				radius = edge.get_meta_data("r", instance)
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
				cx = (key_points[0].get_instance_x(instance) + dist * cos(angle) + offset.x) * scale + center.x
				cy = -(key_points[0].get_instance_y(instance) + dist * sin(angle) + offset.y) * scale + center.y
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
			draw_data = edge.get_draw_data(instance)
			coords = draw_data['coords']
			x1 = None
			y1 = None
			for coord in coords:
				x2 = (coord.x + offset.x) * scale + center.x
				y2 = -(coord.y + offset.y) * scale + center.y
				if x1 is not None:
					qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
				x1 = x2
				y1 = y2


def draw_kp(qp, key_point, scale, offset, center, instance = None):
	x1 = (key_point.get_instance_x(instance) + offset.x) * scale + center.x
	y1 = -(key_point.get_instance_y(instance) + offset.y) * scale + center.y
	qp.drawEllipse(QPointF(x1, y1), 4, 4)


class Limits():
	def __init__(self):
		self.x_max = 0
		self.y_max = 0
		self.x_min = 0
		self.y_min = 0

	def check_limits(self, other_limits):
		if other_limits.x_max > self.x_max:
			self.x_max = other_limits.x_max
		if other_limits.x_min < self.x_min:
			self.x_min = other_limits.x_min
		if other_limits.y_max > self.y_max:
			self.y_max = other_limits.y_max
		if other_limits.y_min < self.y_min:
			self.y_min = other_limits.y_min


def draw_area(area, qp, scale, offset, half_height, half_width, show_names, brush, instance = None):
	first_kp = True
	limits = Limits()

	counter = 0

	if type(area) == CompositeArea:
		path = get_area_path(area.base_area, scale, offset, half_height, half_width, limits, instance)
		for subarea in area.subtracted_areas:
			other_limits = Limits()
			sub_area_path = get_area_path(subarea, scale, offset, half_height, half_width, other_limits, instance)
			limits.check_limits(other_limits)
			path = path.subtracted(sub_area_path)
		qp.fillPath(path, brush)
	else:
		path = get_area_path(area, scale, offset, half_height, half_width, limits, instance)
		qp.fillPath(path, brush)

	if show_names:
		qp.setPen(QPen(QColor(0, 0, 0), 2))
		if limits.x_max - limits.x_min < (limits.y_max - limits.y_min) * 0.75:
			qp.rotate(-90)
			qp.drawText(QRectF(-limits.y_min, limits.x_min, limits.y_min - limits.y_max, limits.x_max - limits.x_min), Qt.AlignCenter, area.name)
			qp.rotate(90)
		else:
			qp.drawText(QRectF(limits.x_min, limits.y_min, limits.x_max - limits.x_min, limits.y_max - limits.y_min), Qt.AlignCenter, area.name)


def get_area_path(area, scale, offset, half_height, half_width, limits, instance = None):
	path = QPainterPath()
	first_kp = True
	counter = 0
	if area.get_edges()[0].type == EdgeType.CircleEdge:
		kp = area.get_inside_key_points()[0]
		r = area.get_edges()[0].get_meta_data('r')
		x = (kp.get_instance_x(instance) + offset.x) * scale + half_width
		y = -(kp.get_instance_y(instance) + offset.y) * scale + half_height

		limits.x_max = x + r * scale
		limits.x_min = x - r * scale
		limits.y_max = y + r * scale
		limits.y_min = y - r * scale
		path.addEllipse(QRectF(x - r * scale, y - r * scale, 2 * r * scale, 2 * r * scale))

	else:
		for kp in area.get_key_points():
			edges = kp.get_edges()
			is_fillet_kp = False
			fillet_dist = 0
			for edge in edges:
				if edge.type == EdgeType.FilletLineEdge:
					r = edge.get_meta_data("r", instance)
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
				x = (kp.get_instance_x(instance) + fillet_offset_x + offset.x) * scale + half_width
				y = -(kp.get_instance_y(instance) + fillet_offset_y + offset.y) * scale + half_height
			else:
				x = (kp.get_instance_x(instance) + offset.x) * scale + half_width
				y = -(kp.get_instance_y(instance) + offset.y) * scale + half_height
			if first_kp:
				path.moveTo(QPointF(x, y))
				first_kp = False
				limits.x_max = x
				limits.y_max = y
				limits.x_min = x
				limits.y_min = y
			else:
				edge = area.get_edges()[counter - 1]
				if edge.type == EdgeType.ArcEdge:
					center_kp = edge.get_key_points()[0]
					cx = (center_kp.x + offset.x) * scale + half_width
					cy = -(center_kp.y + offset.y) * scale + half_height
					radius = edge.get_meta_data('r')
					start_angle = edge.get_meta_data('sa', instance)
					end_angle = edge.get_meta_data('ea', instance)
					diff = (x - (cx + cos(end_angle) * radius * scale)) + (y - (cy - sin(end_angle) * radius * scale))
					end_angle *= 180 / pi
					start_angle *= 180 / pi
					sweep_length = end_angle - start_angle
					if sweep_length < 0:
						sweep_length += 360

					path.arcTo(cx - radius * scale, cy - radius * scale, scale * radius * 2, scale * radius * 2, start_angle,
										 sweep_length)
				elif is_fillet_kp:
					center_kp = Vertex(kp.get_instance_x(instance), kp.get_instance_y(instance), kp.get_instance_z(instance))
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
				elif edge.type == EdgeType.NurbsEdge:
					draw_data = edge.get_draw_data(instance)
					coords = draw_data['coords']

					for coord in coords:
						x2 = (coord.x + offset.x) * scale + half_width
						y2 = -(coord.y + offset.y) * scale + half_height
						path.lineTo(QPointF(x2, y2))

				else:
					path.lineTo(QPointF(x, y))
				if x > limits.x_max:
					limits.x_max = x
				if x < limits.x_min:
					limits.x_min = x
				if y > limits.y_max:
					limits.y_max = y
				if y < limits.y_min:
					limits.y_min = y
			counter += 1

	return path

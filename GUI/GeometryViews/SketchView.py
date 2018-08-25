from math import pi, cos, sin

from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPainter, QPainterPath, QBrush, QColor, QTransform

from Data.Areas import CompositeArea
from Data.Edges import EdgeDrawDataType, EdgeType, get_fillet_offset_distance
from Data.Style import BrushType
from Data.Vertex import Vertex
from GUI.Widgets.NewDrawers import Limits

sketch_views = {}


class SketchViewInstance:
	def __init__(self, sketch, instance_uid):
		self._sketch = sketch
		self._instance_uid = instance_uid
		self._edges = {}
		self._areas = {}
		self._invalidated = True
		sketch.add_change_handler(self.on_sketch_changed)

	@property
	def instance(self):
		return self._instance_uid


	def on_sketch_changed(self, event):
		self._invalidated = True

	def draw(self, qp: QPainter, pens, annotation_scale, show_area_names, show_keypoints):
		if self._invalidated:
			self.regenerate_paths()
		qp.setBrush(QBrush())
		for pen_name in self._edges:
			pen = pens[pen_name]
			qp.setPen(pen)
			qp.drawPath(self._edges[pen_name])
		for area_uid in self._areas:
			area = self._sketch.get_area(area_uid)
			if area.brush is not None:
				if area.brush.type == BrushType.Solid:
					brush = QBrush(QColor(0, 0, 0))
				else:
					brush = QBrush(QColor(0, 0, 0), Qt.HorPattern)
				transform = QTransform().scale(annotation_scale, annotation_scale).rotate(area.brush_rotation)
				brush.setTransform(transform)

				qp.fillPath(self._areas[area_uid], brush)
		if show_keypoints:
			qp.drawPath(self._kps)

		for sketch_instance in self._sketch.sketch_instances:
			sketch_view = get_sketch_view(sketch_instance.sketch)
			sioffset = sketch_instance.offset / sketch_instance.scale
			sketch_view.draw_instance(qp, pens, sketch_instance.scale, annotation_scale/sketch_instance.scale, sioffset, Vertex(), sketch_instance.rotation, sketch_instance.uid, show_area_names, show_keypoints)

	def get_edge_path(self, pen_name):
		if pen_name in self._edges:
			return self._edges[pen_name]
		else:
			path = QPainterPath()
			self._edges[pen_name] = path
			return path

	def regenerate_paths(self):
		self._edges = {}
		self._areas = {}
		self._invalidated = False
		for edge in self._sketch.get_edges():
			draw_data = edge.get_draw_data(self._instance_uid)
			path = self.get_edge_path(edge.style.uid)
			coords = None
			if 'coords' in draw_data:
				coords = draw_data['coords']
			if draw_data['type'] == EdgeDrawDataType.Line:
				c1 = coords[0]
				c2 = coords[1]
				path.moveTo(c1.x, -c1.y)
				path.lineTo(c2.x, -c2.y)
			elif draw_data['type'] == EdgeDrawDataType.Lines:
				c1 = coords[0]
				path.moveTo(c1.x, -c1.y)
				for i in range(1, len(coords)):
					c2 = coords[i]
					path.lineTo(c2.x, -c2.y)
			elif draw_data['type'] == EdgeDrawDataType.Arc:
				rect = draw_data["rect"]
				start_angle = draw_data["sa"]
				span = draw_data["span"]
				radius = draw_data["r"]
				c = draw_data["c"]
				rect = QRectF(rect[0], -rect[1], rect[2], rect[3])
				path.moveTo(c.x, -c.y)
				path.arcMoveTo(rect, start_angle*180/pi)
				path.arcTo(rect, start_angle*180/pi, span*180/pi)
			elif draw_data['type'] == EdgeDrawDataType.Circle:
				rect = draw_data["rect"]
				rect = QRectF(rect[0], -rect[1], rect[2], rect[3])
				path.addEllipse(rect)
		for area in self._sketch.get_areas():
			limits = Limits()
			if type(area) == CompositeArea:
				path = get_area_path(area.base_area, limits, self._instance_uid)
				for subarea in area.subtracted_areas:
					other_limits = Limits()
					sub_area_path = get_area_path(subarea, other_limits, self._instance_uid)
					limits.check_limits(other_limits)
					path = path.subtracted(sub_area_path)
			else:
				path = get_area_path(area, limits, self._instance_uid)
			self._areas[area.uid] = path

class SketchView(SketchViewInstance):
	def __init__(self, sketch):
		SketchViewInstance.__init__(self, sketch, None)
		self._instances = {}


	def draw_instance(self, qp: QPainter, pens, scale, annotation_scale, offset, view_center, rotation, instance=None, show_area_names=False, show_keypoints=False):
		qp.save()
		qp.translate(view_center.x, view_center.y)
		qp.scale(scale, scale)
		qp.translate(offset.x, -offset.y)
		qp.rotate(rotation)
		try:
			if instance is None:
				sketch_view_instance = self
			else:
				if instance in self._instances:
					sketch_view_instance = self._instances[instance]
				else:
					sketch_view_instance = SketchViewInstance(self._sketch, instance)
					self._instances[instance] = sketch_view_instance
			sketch_view_instance.draw(qp, pens, annotation_scale/scale, show_area_names, show_keypoints)
		except Exception as e:
			print(str(e))
		qp.restore()



def get_sketch_view(sketch) -> SketchView:
	if sketch.uid in sketch_views:
		return sketch_views[sketch.uid]
	sketch_view = SketchView(sketch)
	sketch_views[sketch.uid] = sketch_view
	return sketch_view


def get_area_path(area, limits, instance):
	path = QPainterPath()
	first_kp = True
	counter = 0
	if area.get_edges()[0].type == EdgeType.CircleEdge:
		kp = area.get_inside_key_points()[0]
		r = area.get_edges()[0].get_meta_data('r')
		x = (kp.get_instance_x(instance))
		y = -(kp.get_instance_y(instance))

		limits.x_max = x + r
		limits.x_min = x - r
		limits.y_max = y + r
		limits.y_min = y - r
		path.addEllipse(QRectF(x - r, y - r, 2 * r, 2 * r))
	else:
		for kp in area.get_keypoints():
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
					kp_prev = area.get_keypoints()[len(area.get_keypoints()) - 2]
				else:
					kp_prev = area.get_keypoints()[counter - 1]
				if counter + 1 == len(area.get_keypoints()):
					kp_next = area.get_keypoints()[1]
				else:
					kp_next = area.get_keypoints()[counter + 1]
				angle = kp.angle2d(kp_prev)
				angle_next = kp.angle2d(kp_next)
				fillet_offset_x = fillet_dist * cos(angle_next)
				fillet_offset_y = fillet_dist * sin(angle_next)
				x = (kp.get_instance_x(instance) + fillet_offset_x)
				y = -(kp.get_instance_y(instance) + fillet_offset_y)
			else:
				x = (kp.get_instance_x(instance))
				y = -(kp.get_instance_y(instance))
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
					center_kp = edge.get_keypoints()[0]
					cx = center_kp.x
					cy = -center_kp.y
					radius = edge.get_meta_data('r')
					start_angle = edge.get_meta_data('sa', instance)
					end_angle = edge.get_meta_data('ea', instance)
					diff = (x - (cx + cos(end_angle) * radius)) + (y - (cy - sin(end_angle) * radius))
					end_angle *= 180 / pi
					start_angle *= 180 / pi
					sweep_length = end_angle - start_angle
					if sweep_length < 0:
						sweep_length += 360

					path.arcTo(cx - radius, cy - radius, radius * 2,radius * 2, start_angle, sweep_length)
				elif is_fillet_kp:
					center_kp = Vertex(kp.get_instance_x(instance), kp.get_instance_y(instance), kp.get_instance_z(instance))
					fillet_offset_x = fillet_dist * cos(angle)
					fillet_offset_y = fillet_dist * sin(angle)
					center_kp.x += fillet_offset_x
					center_kp.y += fillet_offset_y

					angle_between = kp.angle_between(kp_prev, kp_next)
					if angle_between < 0 or angle_between < pi:
						angle_perp = angle + pi / 2
					else:
						angle_perp = angle - pi / 2
					center_kp.x += r * cos(angle_perp)
					center_kp.y += r * sin(angle_perp)

					cx = center_kp.x
					cy = -center_kp.y

					if angle_between < 0 or angle_between < pi:
						start_angle = (angle * 180 / pi) + 270
					else:
						start_angle = angle * 180 / pi + 90
					sweep_length = -(180 - angle_between * 180 / pi)
					path.arcTo(cx - r, cy - r, r * 2, r * 2, start_angle, sweep_length)
				elif edge.type == EdgeType.NurbsEdge:
					draw_data = edge.get_draw_data(instance)
					coords = draw_data['coords']

					# Make sure the direction is correct.
					f_kp = coords[0]
					l_kp = coords[len(coords)-1]
					n_kp = Vertex(x, -y)
					first_dist = f_kp.distance(n_kp)
					last_dist = l_kp.distance(n_kp)
					if first_dist < last_dist:
						coords = reversed(coords)

					for coord in coords:
						x2 = coord.x
						y2 = -coord.y
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

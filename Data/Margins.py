from math import cos, pi, sin

from Data.Sketch import Edge
from Data.Events import ChangeEvent
from Data.Objects import ObservableObject
from Data.Vertex import Vertex


class OffsetVertex(Vertex):
	def __init__(self, margins_object):
		self.margins_object = margins_object
		self.kp = None
		self.size = 0.0


class Margin(ObservableObject):
	def __init__(self):
		ObservableObject.__init__(self)
		self._edges_list = []
		self._name = "New margin"
		self._switch_parameter = None
		self._size_parameter = None

	@property
	def name(self):
		return self._name

	@property
	def length(self):
		return len(self._edges_list)

	def set_name(self, value):
		self._name = value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

	def add_edge(self, edge):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, edge))
		self._edges_list.append(edge)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, edge))
		edge.add_change_handler(self.on_edge_changed)

	def remove_edges(self, edges):
		for edge in edges:
			if edge in self._edges_list:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, edge))
				self._edges_list.remove(edge)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, edge))

	def on_edge_changed(self, event):
		self.changed(event)

	def get_edges(self):
		return self._edges_list

	def set_switch_parameter(self, switch_parameter):
		if self._switch_parameter is not None:
			self._switch_parameter.remove_change_handler(self.on_parameter_changed)
		self._switch_parameter = switch_parameter
		self._switch_parameter.add_change_handler(self.on_parameter_changed)

	def set_size_parameter(self, size_parameter):
		if self._size_parameter is not None:
			self._size_parameter.remove_change_handler(self.on_parameter_changed)
		self._size_parameter = size_parameter
		self._size_parameter.add_change_handler(self.on_parameter_changed)

	def on_parameter_changed(self, event):
		self.changed(event)

	@property
	def size_parameter(self):
		return self._size_parameter

	@property
	def switch_parameter(self):
		return self._switch_parameter

	def get_edges_uids(self):
		uids = []
		for edge in self._edges_list:
			uids.append(edge.uid)
		return uids

	def serialize_json(self):
		return {
			'name': self._name,
			'switch': self._switch_parameter.uid,
			'size': self.size_parameter.uid,
			'edges_list': self.get_edges_uids(),
		}

	@staticmethod
	def deserialize(data, document):
		margin = Margin()
		if data is not None:
			margin.deserialize_data(data, document)
		return margin

	def deserialize_data(self, data, doc):
		self._name = data['name']
		size_uid = data['size']
		self._size_parameter = doc.get_parameters().get_parameter_by_uid(size_uid)
		self._size_parameter.add_change_handler(self.on_parameter_changed)
		switch_uid = data['switch']
		self._switch_parameter = doc.get_parameters().get_parameter_by_uid(switch_uid)
		self._switch_parameter.add_change_handler(self.on_parameter_changed)
		for edge_uid in data.get('edges_list', []):
			edge = doc.get_edges().get_edge(edge_uid)
			if edge is not None:
				edge.add_change_handler(self.on_edge_changed)
				self._edges_list.append(edge)


class Margins(ObservableObject):
	def __init__(self, doc):
		ObservableObject.__init__(self)
		self._doc = doc
		self._margin_list = []

	def create_margin(self, name, switch_param, size_param):
		margin = Margin()
		margin.set_name(name)
		margin.set_switch_parameter(switch_param)
		margin.set_size_parameter(size_param)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, margin))
		self._margin_list.append(margin)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, margin))
		margin.add_change_handler(self.on_margin_changed)

	def remove_margins(self, margins):
		for margin in margins:
			if margin in self._margin_list:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, margin))
				self._margin_list.remove(margin)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, margin))
				margin.remove_change_handler(self.on_margin_changed)

	def get_margins(self):
		return self._margin_list

	def on_margin_changed(self, event):
		self.changed(event)

	def get_offset_edges_and_kps(self):
		"""
		This functions finds the offset keypoints from the defined margins.
		The function determines which direction the offset is based on the defined areas.
		:return: returns the edges and keypoints with their total margin applied.
		"""
		areas_object = self._doc.get_areas()
		kps = {}
		edges = {}
		# Summing the margins on each edge
		for margin in self.get_margins():
			for edge in margin.get_edges():
				if edge.uid not in edges:
					edge_param_name = margin.switch_parameter.name
					edges[edge.uid] = {'total_margin': margin.size_parameter.value, 'edge': edge, 'switch_parameter': edge_param_name}
				else:
					edges[edge.uid]['total_margin'] += margin.size_parameter.value
					edges[edge.uid]['switch_parameter'] = margin.switch_parameter.name
		# Finding the largest margin on each kp
		# matching the edges to the kps
		for edge_tuple in edges.items():
			edge = edge_tuple[1]['edge']
			for kp in edge_tuple[1]['edge'].get_end_key_points():
				if kp.uid in kps:
					kps[kp.uid]['margin'] = max(edge_tuple[1]['total_margin'], kps[kp.uid]['margin'])
					kps[kp.uid]['edges'].add(edge)
				else:
					edges_set = set()
					edges_set.add(edge)
					kps[kp.uid] = {'kp': kp, 'margin': edge_tuple[1]['total_margin'], 'edges': edges_set}
		# Calculating a offset Vertex from the kp and the edges
		for kp_tuple in kps.items():
			kp = kp_tuple[1]['kp']
			edges_set = kp_tuple[1]['edges']
			margin = kp_tuple[1]['margin']
			if len(edges_set) >= 2:
				edges_list = list(edges_set)
				edge1 = edges_list[0]
				edge2 = edges_list[1]
				if edge1.type == Edge.LineEdge and edge2.type == Edge.LineEdge:
					kps[kp.uid]['okp'] = self.calc_offset_from_two_line_edges(edge1, edge2, kp, margin)
				else:
					if edge1.type == Edge.ArcEdge:
						kps[kp.uid]['okp'] = self.calc_offset_from_an_edge(edge1, kp, margin, edges)
					else:
						kps[kp.uid]['okp'] = self.calc_offset_from_an_edge(edge2, kp, margin, edges)
			else:
				edges_list = list(edges_set)
				edge = edges_list[0]
				kps[kp.uid]['okp'] = self.calc_offset_from_an_edge(edge, kp, margin, edges)
		return edges, kps

	def calc_offset_from_an_edge(self, edge, kp, margin, edges):
		areas_object = self._doc.get_areas()
		if edge.type == Edge.LineEdge:
			for ekp in edge.get_end_key_points():
				if ekp != kp:
					kp1 = ekp

			median = (kp.xyz + kp1.xyz) / 2
			angle1 = kp.angle2d(kp1) + pi / 2
			test_vertex = Vertex(median[0] + cos(angle1) * margin, median[1] + sin(angle1) * margin)
			inside = False
			for area in areas_object.get_areas():
				if edge in area[1].get_edges():
					if area[1].inside(test_vertex):
						inside = True
						break
			if not inside:
				angle1 += pi
			okp = Vertex(kp.x + cos(angle1) * margin, kp.y + sin(angle1) * margin)
			return okp
		elif edge.type == Edge.ArcEdge:
			ckp = edge.get_keypoints()[0]
			angle1 = edge.angle(kp) + pi / 2
			sa = edge.get_meta_data('sa')
			ea = edge.get_meta_data('ea')
			diff = ea - sa
			if diff < 0:
				diff += 2 * pi
			mid_angle = sa + diff / 2
			radius = margin + edge.get_meta_data('r')
			test_vertex = Vertex(ckp.x + cos(mid_angle) * radius, ckp.y + sin(mid_angle) * radius)
			inside = False
			for area in areas_object.get_areas():
				if edge in area[1].get_edges():
					if area[1].inside(test_vertex):
						inside = True
						break
			if not inside:
				angle1 += pi
				edges[edge.uid]['convex'] = False
			else:
				edges[edge.uid]['convex'] = True

			okp = Vertex(kp.x + cos(angle1) * margin, kp.y + sin(angle1) * margin)
			return okp

	def calc_offset_from_two_line_edges(self, edge1, edge2, kp, margin):
		areas_object = self._doc.get_areas()
		for ekp in edge1.get_end_key_points():
			if ekp != kp:
				kp1 = ekp
		for ekp in edge2.get_end_key_points():
			if ekp != kp:
				kp2 = ekp
		median = (kp.xyz + kp1.xyz) / 2
		angle1 = kp.angle2d(kp1) + pi / 2
		angle2 = kp.angle2d(kp2) + pi / 2
		test_vertex = Vertex(median[0] + cos(angle1) * margin, median[1] + sin(angle1) * margin)
		inside = False
		for area in areas_object.get_areas():
			if edge1 in area[1].get_edges():
				if area[1].inside(test_vertex):
					inside = True
					break
		if not inside:
			angle1 += pi
			angle2 += pi
		angle_diff = (angle2 - angle1) / 2
		offset_angle = angle1 + angle_diff - pi / 2
		offset_distance = margin / sin(angle_diff)
		okp = Vertex(kp.x + cos(offset_angle) * offset_distance, kp.y + sin(offset_angle) * offset_distance)
		return okp

	def serialize_json(self):
		return {
			'margin_list': self._margin_list
		}

	@staticmethod
	def deserialize(data, document):
		margins = Margins(document)
		if data is not None:
			margins.deserialize_data(data, document)
		return margins

	def deserialize_data(self, data, document):
		for margin_data in data.get('margin_list', []):
			margin = Margin.deserialize(margin_data, document)
			margin.add_change_handler(self.on_margin_changed)
			self._margin_list.append(margin)

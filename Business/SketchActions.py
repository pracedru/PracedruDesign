import collections
from math import pi

from Business.Undo import DoObject
from Data.Document import Document
from Data.Proformer import ProformerType
from Data.Sketch import *


class CreateSketchDoObject(DoObject):
	def __init__(self, sketch, parent):
		DoObject.__init__(self)
		self._sketch = sketch
		self._name = sketch.name
		self._parent = parent

	def undo(self):
		self._sketch.delete()

	def redo(self):
		self._parent.add_sketch(self._sketch)


class CreateKeypointDoObject(DoObject):
	def __init__(self, sketch, kp, edge_to_split, new_edge):
		DoObject.__init__(self)
		self._sketch = sketch
		self._kp = kp

	def undo(self):
		self._kp.delete()

	def redo(self):
		self._sketch.add_keypoint(self._kp)


class CreateEdgeDoObjet(DoObject):
	def __init__(self, sketch, edge):
		DoObject.__init__(self)
		self._sketch = sketch
		self._edge = edge

	def undo(self):
		self._edge.delete()

	def redo(self):
		self._sketch.add_edge(self._edge)


def create_add_sketch_to_parent(parent):
	sketch = Sketch(parent)
	parent.add_sketch(sketch)
	parent.document.undo_stack.append(CreateSketchDoObject(sketch, parent))
	return sketch


def get_create_keypoint(sketch, x, y, coincident_threshold):
	kp = sketch.get_keypoint_by_location(x, y, 0.0, coincident_threshold)
	if kp is None:
		kp = sketch.create_keypoint(x, y, 0.0)
		edge_to_split = None
		new_edge = None
		for edge in sketch.get_edges():
			if edge.coincident(kp, coincident_threshold):
				edge_to_split = edge
		if edge_to_split is not None:
			new_edge = edge_to_split.split(kp)
			for area in sketch.get_areas():
				if edge_to_split in area.get_edges():
					area.insert_edge(new_edge, edge_to_split)
		sketch.document.undo_stack.append(CreateKeypointDoObject(sketch, kp, edge_to_split, new_edge))
	return kp


def create_line(sketch, start_kp, end_kp):
	line_edge = sketch.create_line_edge(start_kp, end_kp)
	sketch.document.undo_stack.append(CreateEdgeDoObjet(sketch, line_edge))
	return line_edge


def create_circle(doc, sketch, kp, radius_param):
	circle_edge = sketch.create_circle_edge(kp, radius_param)
	return circle_edge


def create_nurbs_edge(doc, sketch, kp):
	return sketch.create_nurbs_edge(kp)


def create_fillet(doc, sketch, fillet_kp, radius_param):
	fillet_edge = sketch.create_fillet_edge(fillet_kp, radius_param)
	return fillet_edge


def create_text(doc, sketch, kp, value, height):
	sketch.create_text(kp, value, height)


def create_attribute(doc, sketch, kp, name, default_value, height):
	sketch.create_attribute(kp, name, default_value, height)


def add_arc(document, sketch: Sketch, kp, radius_param, start_angle_param, end_angle_param):
	arc_edge = sketch.create_arc_edge(kp, start_angle_param.value, end_angle_param.value, radius_param.value)
	arc_edge.set_meta_data_parameter('r', radius_param)
	arc_edge.set_meta_data_parameter('sa', start_angle_param)
	arc_edge.set_meta_data_parameter('ea', end_angle_param)


def add_sketch_instance_to_sketch(sketch, sketch_to_insert, kp):
	sketch_instance = sketch.create_sketch_instance(sketch_to_insert, kp)
	return sketch_instance


def set_similar_x(document: Document, sketch: Sketch, key_points: [], name):
	for e in key_points:
		value = e.x
		break
	param = sketch.get_parameter_by_name(name)
	if param is None:
		param = sketch.create_parameter(name, value)
	for kp in key_points:
		kp.set_x_parameter(param.uid)


def set_similar_y(document: Document, sketch: Sketch, key_points: [], name):
	for e in key_points:
		value = e.y
		break
	param = sketch.get_parameter_by_name(name)
	if param is None:
		param = sketch.create_parameter(name, value)
	for kp in key_points:
		kp.set_y_parameter(param.uid)


def find_all_similar(doc, sketch, digits):
	key_points = sketch.get_keypoints()
	sim_x_dict = {}
	sim_y_dict = {}
	arcs = []
	doc.do_update = False
	for kp in key_points:
		x_name = round(kp.x, digits)
		y_name = round(kp.y, digits)
		if x_name not in sim_x_dict:
			sim_x_dict[x_name] = []
		if y_name not in sim_y_dict:
			sim_y_dict[y_name] = []
		sim_x_dict[x_name].append(kp)
		sim_y_dict[y_name].append(kp)
	counter = 0

	sim_x_dict = collections.OrderedDict(sorted(sim_x_dict.items()))
	sim_y_dict = collections.OrderedDict(sorted(sim_y_dict.items()))
	for sim_x_list_tuple in sim_x_dict.items():
		sim_x_list = sim_x_list_tuple[1]
		param = None
		for kp in sim_x_list:
			if kp.get_x_parameter() is not None:
				param = kp.get_x_parameter()
				break
		if param is None:
			exists = True
			while exists:
				name = 'X%03d' % counter
				if sketch.get_parameter_by_name(name) is None:
					exists = False
				counter += 1
			param = sketch.create_parameter(name, float(sim_x_list_tuple[0]))
			param.hidden = True
		for kp in sim_x_list:
			kp.set_x_parameter(param.uid)
	counter = 0
	for sim_y_list_tuple in sim_y_dict.items():
		sim_y_list = sim_y_list_tuple[1]
		param = None
		for kp in sim_y_list:
			if kp.get_y_parameter() is not None:
				param = kp.get_y_parameter()
				break
		if param is None:
			exists = True
			while exists:
				name = 'Y%03d' % counter
				if sketch.get_parameter_by_name(name) is None:
					exists = False
				counter += 1
			param = sketch.create_parameter(name, float(sim_y_list_tuple[0]))
			param.hidden = True
		for kp in sim_y_list:
			kp.set_y_parameter(param.uid)
	for edge in sketch.get_edges():
		if edge.type == EdgeType.ArcEdge:
			r = edge.get_meta_data("r")
			ea = edge.get_meta_data("ea")
			sa = edge.get_meta_data("sa")
			if edge.get_meta_data_parameter('r') is None:
				param_r = doc.get_parameters().create_parameter('PARR_' + edge.name, r)
				edge.set_meta_data_parameter('r', param_r)
			if edge.get_meta_data_parameter('sa') is None:
				param_sa = doc.get_parameters().create_parameter('PARSA_' + edge.name, sa)
				edge.set_meta_data_parameter('sa', param_sa)
			if edge.get_meta_data_parameter('ea') is None:
				param_ea = doc.get_parameters().create_parameter('PAREA_' + edge.name, ea)
				edge.set_meta_data_parameter('ea', param_ea)
	doc.do_update = True


def remove_key_points(sketch, kps):
	for kp in kps:
		kp.delete()
	#sketch.remove_key_points(kps)

def remove_areas(sketch, areas):
	sketch.remove_areas(areas)


def remove_edge(sketch, edge):
	remove_edges(sketch, [edge])


def remove_edges(sketch, edges):
	for edge in edges:
		edge.delete()
	#sketch.remove_edges(edges)

def remove_texts(sketch, texts):
	for text in texts:
		text.delete()

def create_area(sketch, branch):
	area = sketch.create_area()
	for edge in branch['edges']:
		area.add_edge(edge)
	find_fillets(sketch, area)


def create_all_areas(docs: Document, sketch: Sketch):
	edges = []
	for edge in sketch.get_edges():
		edges.append(edge)
	branches = find_all_areas(edges)
	sketch.clear_areas()
	unique_branches = []
	for branch in branches:
		is_unique = True
		for unique_branch in unique_branches:
			if len(branch['edges']) == len(unique_branch['edges']):
				same_all = True
				for edge in branch['edges']:
					if edge not in unique_branch['edges']:
						same_all = False
				if same_all:
					is_unique = False
		if is_unique:
			unique_branches.append(branch)

	for branch in unique_branches:
		if branch['enclosed']:
			area = sketch.create_area()
			for edge in branch['edges']:
				area.add_edge(edge)
			find_fillets(sketch, area)


def find_fillets(sketch, area):
	fillet_edges = []
	for edge in sketch.get_edges():
		if edge.type == EdgeType.FilletLineEdge:
			fillet_edges.append(edge)
	kps = area.get_inside_key_points()
	for kp in kps:
		for fillet_edge in fillet_edges:
			if kp in fillet_edge.get_end_key_points():
				if fillet_edge not in area.get_edges():
					area.add_edge(fillet_edge)


def find_all_areas(edges):
	# edges_object = doc.get_edges()
	connections = {}
	for edge in edges:
		# edge = edge_tuple[1]
		if edge.type != EdgeType.FilletLineEdge:
			kps = edge.get_end_key_points()
			for kp in kps:
				if kp.uid not in connections:
					connection = {'kp': kp, 'edges': [], 'uid': kp.uid}
					connections[kp.uid] = connection
					# connection = connections[kp.uid]
				else:
					connection = connections[kp.uid]
				connection['edges'].append(edge)

	branches = []
	for connection_tuple in connections.items():
		conn1 = None
		if len(connection_tuple[1]['edges']) > 1:
			conn1 = connection_tuple[1]
		elif connection_tuple[1]['edges'][0].type == EdgeType.CircleEdge:
			conn1 = connection_tuple[1]

		if conn1 is not None:
			for edge in conn1['edges']:
				branch = {'edges': [edge], 'start_conn': conn1}
				branches.append(branch)

	for branch in branches:
		follow_branch(branch, branches, connections)
	return branches


def follow_branch(branch, branches, connections):
	branch_ended = False
	next_connection = None
	previous_edge = branch['edges'][0]
	if previous_edge.type == EdgeType.CircleEdge:
		branch_ended = True
		branch['enclosed'] = True
	for kp in previous_edge.get_end_key_points():
		if kp.uid != branch['start_conn']['uid']:
			next_connection = connections[kp.uid]
	last_connection = branch['start_conn']
	while not branch_ended:
		this_connection = next_connection
		next_edge = None
		if len(this_connection['edges']) > 2:
			this_kp = this_connection['kp']
			prev_kp = last_connection['kp']
			smallest_angle = None
			for edge in this_connection['edges']:
				if edge is not previous_edge and edge.type != EdgeType.FilletLineEdge and edge.type != EdgeType.CircleEdge:
					kps = edge.get_keypoints()
					if kps[0] == this_kp:
						next_kp = kps[1]
					else:
						next_kp = kps[0]
					angle = angle_between_edges(this_kp, prev_kp, next_kp)
					if smallest_angle is None:
						smallest_angle = angle
						next_edge = edge
					else:
						if angle < smallest_angle:
							smallest_angle = angle
							next_edge = edge
			for edge in this_connection['edges']:
				if edge is not next_edge and edge is not previous_edge and edge.type != EdgeType.FilletLineEdge and edge.type != EdgeType.CircleEdge:
					exists = False
					for existing_branch in branches:
						if existing_branch['edges'][0] == edge and this_connection == existing_branch['start_conn']:
							exists = True
					if not exists:
						pass

			if next_edge in branch['edges']:
				branch_ended = True
				branch['enclosed'] = False
				next_edge = None
			else:
				branch['edges'].append(next_edge)
		elif len(this_connection['edges']) == 2:
			this_kp = this_connection['kp']
			if this_connection['edges'][0] == previous_edge:
				next_edge = this_connection['edges'][1]
			else:
				next_edge = this_connection['edges'][0]
			if next_edge in branch['edges']:
				branch_ended = True
				next_edge = None
				branch['enclosed'] = False
			else:
				branch['edges'].append(next_edge)
		else:
			branch_ended = True
			branch['enclosed'] = False

		if next_edge is not None:
			last_connection = this_connection
			next_connection = None
			for kp in next_edge.get_end_key_points():
				if kp.uid == branch['start_conn']['uid']:
					branch_ended = True
					branch['enclosed'] = True
				elif kp.uid == last_connection['uid']:
					pass
				else:
					next_connection = connections[kp.uid]

		if next_connection is None and not branch_ended:
			raise Exception('Wierd ending detected!!')
		previous_edge = next_edge

		# areas.append(branch)


def create_composite_area(sketch, base_area, subtract_areas):
	print("create_composite_area")
	comp_area = sketch.create_composite_area()
	comp_area.base_area = base_area
	for area in subtract_areas:
		comp_area.add_subtract_area(area)
	return comp_area


def angle_between_edges(common_kp, kp1, kp2):
	alpha1 = common_kp.angle2d(kp1)
	alpha2 = common_kp.angle2d(kp2)
	alpha = alpha2 - alpha1
	while alpha < 0:
		alpha += 2 * pi
	while alpha > 2 * pi:
		alpha -= 2 * pi
	return alpha

def create_mirror(sketch, type, kps, edges, areas):
	proformer = sketch.create_proformer(type, "New Mirror")
	proformer.base_keypoints = kps
	proformer.base_edges = edges
	proformer.base_areas = areas
	proformer.resolve()
	return proformer


def create_pattern(sketch, pattern_type, kps, edges, areas, count, dimensions, circular_kp=None):
	proformer = sketch.create_proformer(pattern_type, "New Pattern")
	proformer.base_keypoints = kps
	proformer.base_edges = edges
	proformer.base_areas = areas
	if pattern_type == ProformerType.Circular:
		proformer.name = "Circular Pattern"
		count_param = sketch.get_parameter_by_name(count['param_1_name'])
		count_value = count['param_1_value']

		dim_param = sketch.get_parameter_by_name(dimensions['param_1_name'])
		dim_value = dimensions['param_1_value']

		if count_param is None:
			count_param = sketch.create_parameter(count['param_1_name'], count_value)

		if dim_param is None:
			dim_param = sketch.create_parameter(dimensions['param_1_name'], dim_value)

		count_param.value = count_param.formula
		dim_param.value = dim_param.formula
		proformer.set_meta_data("count", count_value)
		proformer.set_meta_data_parameter("count", count_param)
		proformer.set_meta_data("dim", dim_value)
		proformer.set_meta_data_parameter("dim", dim_param)
		proformer.add_control_kp(circular_kp)


	proformer.resolve()
	return proformer
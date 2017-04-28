import collections
from math import pi

from Data.Document import Document
from Data.Sketch import Edge, Sketch


def create_key_point(doc, sketch, x, y, param, coincident_threshold):

    kp = sketch.create_key_point(x, y, 0.0, coincident_threshold)
    edge_to_split = None
    for edge_tuple in sketch.get_edges():
        edge = edge_tuple[1]
        if edge.coincident(kp, coincident_threshold):
            edge_to_split = edge
    if edge_to_split is not None:
        new_edge = edge_to_split.split(kp)
    return kp


def create_circle(doc, sketch, kp, radius_param):
    circle_edge = sketch.create_circle_edge(kp)
    circle_edge.set_meta_data('r', radius_param.value)
    circle_edge.set_meta_data_parameter('r', radius_param)


def create_fillet(doc, sketch, fillet_kp, radius_param):
    fillet_edge = sketch.create_fillet_edge(fillet_kp)
    fillet_edge.set_meta_data('r', radius_param.value)
    fillet_edge.set_meta_data_parameter('r', radius_param)


def create_text(doc, sketch, kp, value, height):
    sketch.create_text(kp, value, height)


def create_attribute(doc, sketch, kp, name, default_value, height):
    sketch.create_attribute(kp, name, default_value, height)


def add_arc(document, sketch: Sketch, kp, radius_param, start_angle_param, end_angle_param):
    arc_edge = sketch.create_arc_edge(kp, start_angle_param.value, end_angle_param.value, radius_param.value)
    arc_edge.set_meta_data_parameter('r', radius_param)
    arc_edge.set_meta_data_parameter('sa', start_angle_param)
    arc_edge.set_meta_data_parameter('ea', end_angle_param)


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
    key_points = sketch.get_key_points()
    sim_x_dict = {}
    sim_y_dict = {}
    arcs = []
    doc.do_update = False
    for kp_tuple in key_points:
        kp = kp_tuple[1]
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
    for edge_tuple in sketch.get_edges():
        edge = edge_tuple[1]
        if edge.type == Edge.ArcEdge:
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


def remove_key_points(doc, sketch, kps):
    sketch.remove_key_points(kps)


def remove_edge(doc, sketch, edge):
    remove_edges(doc. sketch, [edge])


def remove_edges(doc, sketch, edges):
    sketch.remove_edges(edges)


def create_area(sketch, branch):
    area = sketch.create_area()
    for edge in branch['edges']:
        area.add_edge(edge)
    find_fillets(sketch, area)


def create_all_areas(docs: Document, sketch: Sketch):
    edges = []
    for edge_tuple in sketch.get_edges():
        edges.append(edge_tuple[1])
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
    for edge_tuple in sketch.get_edges():
        edge = edge_tuple[1]
        if edge.type == Edge.FilletLineEdge:
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
        if edge.type != Edge.FilletLineEdge:
            kps = edge.get_end_key_points()
            for kp in kps:
                if kp.uid not in connections:
                    connections[kp.uid] = {'kp': kp, 'edges': [], 'uid': kp.uid}
                    connection = connections[kp.uid]
                else:
                    connection = connections[kp.uid]
                connection['edges'].append(edge)

    branches = []
    for connection_tuple in connections.items():
        conn1 = None
        if len(connection_tuple[1]['edges']) > 1:
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
                if edge is not previous_edge and edge.type != Edge.FilletLineEdge:
                    kps = edge.get_key_points()
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
                if edge is not next_edge and edge is not previous_edge and edge.type != Edge.FilletLineEdge:
                    exists = False
                    for existing_branch in branches:
                        if existing_branch['edges'][0] == edge and this_connection == existing_branch['start_conn']:
                            exists = True
                    if not exists:
                        pass
                        # new_branch = {'edges': [edge], 'start_conn': this_connection}
                        # branches.append(new_branch)

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


def angle_between_edges(common_kp, kp1, kp2):
    alpha1 = common_kp.angle2d(kp1)
    alpha2 = common_kp.angle2d(kp2)
    alpha = alpha2 - alpha1
    while alpha < 0:
        alpha += 2 * pi
    while alpha > 2 * pi:
        alpha -= 2 * pi
    return alpha

import collections

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
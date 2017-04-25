import collections

from Data.Sketch import Edge


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


def create_fillet(doc, sketch, fillet_kp, radius_param):
    fillet_edge = sketch.create_fillet_edge(fillet_kp)
    fillet_edge.set_meta_data('r', radius_param.value)
    fillet_edge.set_meta_data_parameter('r', radius_param)
    areas = doc.get_areas()
    for area_tuple in areas.get_areas():
        area = area_tuple[1]
        kps = area.get_inside_key_points()
        for kp in kps:
            if kp is fillet_kp:
                area.add_edge(fillet_edge)


def create_text(doc, sketch, kp, value, height):
    sketch.create_text(kp, value, height=height)


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
            param = sketch.create_parameter('PARX' + str(counter), float(sim_x_list_tuple[0]))
            counter += 1
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
            param = sketch.create_parameter('PARY' + str(counter), float(sim_y_list_tuple[0]))
            counter += 1
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

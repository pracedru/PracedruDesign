
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
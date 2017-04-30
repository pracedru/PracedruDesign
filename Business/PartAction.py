from Data.Part import SketchFeature, Part
from Data.Sketch import Sketch


def insert_sketch_in_part(document, part, sketch, plane_feature):
    return part.create_sketch_feature(sketch, plane_feature)


def add_revolve_in_part(document, part, sketch_feature, area):
    return part.create_revolve_feature()


def add_extrude_in_part(document, part: Part, sketch_feature, area, length):
    return part.create_extrude_feature("Extrude", sketch_feature, area, length)


def create_add_sketch_to_part(document, part, plane):
    sketch = Sketch(document.get_parameters(), document)
    document.get_geometries().add_geometry(sketch)
    insert_sketch_in_part(document, part, sketch, plane)
    return sketch

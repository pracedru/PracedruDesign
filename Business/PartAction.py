from Data.Part import SketchFeature


def insert_sketch_in_part(document, part, sketch, plane_feature):
    return part.create_sketch_feature(sketch, plane_feature)

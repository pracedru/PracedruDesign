from Business.Undo import DoObject
from Data.Part import Part
from Data.Sketch import Sketch


class PartInsertSketchDoObject(DoObject):
	def __init__(self, sketch, part):
		DoObject.__init__(self)
		self._sketch = sketch
		self._part = part

	def undo(self):
		pass

	def redo(self):
		pass


class PartCreateSketchDoObject(DoObject):
	def __init__(self, sketch, part):
		DoObject.__init__(self)
		self._sketch = sketch
		self._part = part

	def undo(self):
		pass

	def redo(self):
		pass


def insert_sketch_in_part(part, sketch, plane_feature):
	sketch_feature = part.create_sketch_feature(sketch, plane_feature)
	part.document.undo_stack.append(PartInsertSketchDoObject(sketch, part))
	return sketch_feature


def add_revolve_in_part(document, part, sketch_feature, area, length, revolve_axis):
	document.get_axes()[revolve_axis.uid] = revolve_axis
	return part.create_revolve_feature("Revolve", sketch_feature, area, length, revolve_axis)


def add_extrude_in_part(document, part: Part, sketch_feature, area, length):
	return part.create_extrude_feature("Extrude", sketch_feature, area, length)


def create_add_sketch_to_part(part, plane_feature):
	sketch = Sketch(part)
	part.add_sketch(sketch)
	sketch_feature = part.create_sketch_feature(sketch, plane_feature)

	part.document.undo_stack.append(PartCreateSketchDoObject(sketch, part))
	return sketch_feature


def add_nurbs_surface_in_part(document, part, sketch_feature, nurbs_edges):
	return part.create_nurbs_surface(sketch_feature, nurbs_edges)

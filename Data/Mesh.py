from Data.Events import ChangeEvent
from Data.Objects import ObservableObject

__author__ = 'mamj'


class MeshDefinition(ObservableObject):
	EdgeElementDivisionDefinition = 1
	EdgeElementSizeDefinition = 2
	AreaElementSizeDefinition = 3
	GlobalElementSizeDefinition = 4

	def __init__(self):
		ObservableObject.__init__(self)
		self._mesh_element_list = []
		self._type = MeshDefinition.EdgeElementDivisionDefinition
		self._name = "New mesh definition"
		self._size = 10

	@property
	def name(self):

		return self._name

	@name.setter
	def name(self, value):
		self._name = value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value):
		if value != self._type:
			self._mesh_element_list = []
			self.changed(ChangeEvent(self, ChangeEvent.Cleared, self))
		self._type = value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

	@property
	def size(self):
		return self._size

	@size.setter
	def size(self, value):
		self._size = value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

	def add_element(self, element):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, element))
		self._mesh_element_list.append(element)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, element))
		element.add_change_handler(self.on_element_changed)

	def remove_elements(self, elements):
		for element in elements:
			if element in self._mesh_element_list:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, element))
				self._mesh_element_list.remove(element)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, element))
				element.remove_change_handler(self.on_element_changed)

	def on_element_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			if event.object in self._mesh_element_list:
				self._mesh_element_list.remove(event.object)
				event.object.remove_change_handler(self.on_element_changed)
		self.changed(event)

	@property
	def length(self):
		return len(self._mesh_element_list)

	def get_elements(self):
		return self._mesh_element_list

	def get_element_uids(self):
		elements_uids = []
		for element in self._mesh_element_list:
			elements_uids.append(element.uid)
		return elements_uids

	def serialize_json(self):
		return {
			'type': self._type,
			'name': self._name,
			'size': self._size,
			'elements': self.get_element_uids()
		}

	@staticmethod
	def deserialize(data, document):
		mesh_definition = MeshDefinition()
		if data is not None:
			mesh_definition.deserialize_data(data, document)
		return mesh_definition

	def deserialize_data(self, data, doc):
		self._type = data['type']
		self._name = data.get('name', self._name)
		self._size = data.get('size', self._size)
		areas_object = doc.get_areas()
		edges_object = doc.get_edges()
		for element_uid in data.get('elements', []):
			if MeshDefinition.EdgeElementDivisionDefinition <= self._type <= MeshDefinition.EdgeElementSizeDefinition:
				element = edges_object.get_edge(element_uid)
			elif self._type == MeshDefinition.AreaElementSizeDefinition:
				element = areas_object.get_area_item(element_uid)
			else:
				pass
			self._mesh_element_list.append(element)
			element.add_change_handler(self.on_element_changed)


class Mesh(ObservableObject):
	def __init__(self, document):
		ObservableObject.__init__(self)
		self._mesh_def_list = []
		self._doc = document

	def create_mesh_definition(self, type, size):
		mesh_def = MeshDefinition()
		mesh_def.type = type
		mesh_def.size = size
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, mesh_def))
		self._mesh_def_list.append(mesh_def)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, mesh_def))
		mesh_def.add_change_handler(self.on_mesh_def_changed)
		return mesh_def

	def remove_mesh_definitions(self, mesh_definitions):
		for mesh_def in mesh_definitions:
			if mesh_def in self._mesh_def_list:
				self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, mesh_def))
				self._mesh_def_list.remove(mesh_def)
				self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, mesh_def))
				mesh_def.remove_change_handler(self.on_mesh_def_changed)

	def get_mesh_definitions(self):
		return self._mesh_def_list

	def on_mesh_def_changed(self, event):
		self.changed(event)

	def serialize_json(self):
		return {
			'mesh_definitions': self._mesh_def_list
		}

	@staticmethod
	def deserialize(data, document):
		mesh = Mesh(document)
		if data is not None:
			mesh.deserialize_data(data)
		return mesh

	def deserialize_data(self, data):
		for component_data in data.get('mesh_definitions', []):
			mesh_definition = MeshDefinition.deserialize(component_data, self._doc)
			self._mesh_def_list.append(mesh_definition)
			mesh_definition.add_change_handler(self.on_mesh_def_changed)

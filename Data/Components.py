# from Data import Document
from Data.Events import ChangeEvent
from Data.Objects import ObservableObject

__author__ = 'mamj'


class Component(ObservableObject):
	LineComponent = 1
	AreaComponent = 2

	def __init__(self, document):
		ObservableObject.__init__(self)
		self._doc = document
		self._type = Component.LineComponent
		self._elements = []
		self.name = "new Component"

	def get_element_uids(self):
		elements_uids = []
		for element in self._elements:
			elements_uids.append(element.uid)
		return elements_uids

	def add_element(self, element):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, element))
		self._elements.append(element)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, element))
		element.add_change_handler(self.on_element_changed)

	def remove_element(self, element):
		if element in self._elements:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, element))
			self._elements.remove(element)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, element))
			element.remove_change_handler(self.on_element_changed)

	@property
	def type(self):
		return self._type

	@type.setter
	def type(self, value):
		if value != self._type:
			self._elements.clear()
			self.changed(ChangeEvent(self, ChangeEvent.Cleared, self))
		self._type = value

	@property
	def length(self):
		return len(self._elements)

	def on_element_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			if event.object in self._elements:
				self._elements.remove(event.object)
				event.object.remove_change_handler(self.on_element_changed)

	def get_elements(self):
		return self._elements

	def serialize_json(self):
		return {
			'type': self._type,
			'name': self.name,
			'elements': self.get_element_uids()
		}

	@staticmethod
	def deserialize(data, document):
		component = Component(document)
		if data is not None:
			component.deserialize_data(data)
		return component

	def deserialize_data(self, data):
		self._type = data['type']
		self.name = data.get('name', self.name)
		areas_object = self._doc.get_areas()
		edges_object = self._doc.get_edges()
		for element_uid in data.get('elements', []):
			if self._type == Component.LineComponent:
				element = edges_object.get_edge(element_uid)
			else:
				element = areas_object.get_area_item(element_uid)
			self._elements.append(element)
			element.add_change_handler(self.on_element_changed)


class Components(ObservableObject):
	def __init__(self, document):
		ObservableObject.__init__(self)
		self._doc = document
		self._components = []

	def on_component_changed(self, event):
		self.changed(event)

	def create_component(self, name, type):
		component = Component(self._doc)
		component.name = name
		component._type = type
		component.add_change_handler(self.on_component_changed)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, component))
		self._components.append(component)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, component))
		return component

	def remove_components(self, components):
		for component in components:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, component))
			self._components.remove(component)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, component))

	def get_component_by_name(self, name):
		for component in self._components:
			if component.name == name:
				return component
		return None

	def get_components(self):
		return self._components

	def serialize_json(self):
		return {
			'components': self._components
		}

	@staticmethod
	def deserialize(data, document):
		components = Components(document)
		if data is not None:
			components.deserialize_data(data)
		return components

	def deserialize_data(self, data):
		for component_data in data.get('components', []):
			component = Component.deserialize(component_data, self._doc)
			self._components.append(component)
			component.add_change_handler(self.on_component_changed)

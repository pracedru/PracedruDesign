from Data import Parameters
from Data.Events import ChangeEvent
from Data.Vertex import Vertex
from Data.Objects import IdObject, ObservableObject, NamedObservableObject

__author__ = 'mamj'

components = "xyz"

class Point3d(Vertex, IdObject):
	def __init__(self, x=0.0, y=0.0, z=0.0):
		Vertex.__init__(self, x, y, z)
		IdObject.__init__(self)

	def serialize_json(self):
		return \
			{
				'v': Vertex.serialize_json(self),
				'uid': IdObject.serialize_json(self)
			}

	@staticmethod
	def deserialize(data):
		point = Point3d()
		point.deserialize_data(data)
		return point

	def deserialize_data(self, data):
		try:
			IdObject.deserialize_data(self, data['uid'])
		except TypeError as e:
			print("error: " + str(e))
		Vertex.deserialize_data(self, data['v'])


class KeyPoint(Point3d, NamedObservableObject):
	def __init__(self, parameters: Parameters, x=0.0, y=0.0, z=0.0, name="Keypoint"):
		Point3d.__init__(self, x, y, z)
		NamedObservableObject.__init__(self, name)
		self._component_parameters = [None, None, None]
		self._instances = {}
		self._parameters = parameters
		self._edges = []
		self.editable = True
		self._component_change_handlers = []
		self._component_change_handlers.append(self.on_x_param_changed)
		self._component_change_handlers.append(self.on_y_param_changed)
		self._component_change_handlers.append(self.on_z_param_changed)

	@property
	def instances(self):
		return self._instances.items()

	@property
	def parameters(self):
		return self._parameters

	def delete(self):
		self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

	def get_edges(self):
		return list(self._edges)

	def add_edge(self, edge):
		if edge not in self._edges:
			self._edges.append(edge)
			edge.add_change_handler(self.edge_changed_handler)

	def edge_changed_handler(self, event):
		if event.type == ChangeEvent.Deleted:
			self.remove_edge(event.object)

	def remove_edge(self, edge):
		if edge in self._edges:
			edge.remove_change_handler(self.edge_changed_handler)
			self._edges.remove(edge)

	def get_x_parameter(self):
		return self._component_parameters[0]

	def get_y_parameter(self):
		return self._component_parameters[1]

	def get_z_parameter(self):
		return self._component_parameters[2]

	def create_value_change_object(self, new_value, old_value, component, instance_uid):
		change_object = {
			'new value': new_value,
			'old value': old_value,
			'name': components[component],
			'component': component,
			'instance': instance_uid
		}
		return change_object

	def set_instance_generic(self, instance_uid, value, component):
		changed = False
		old_value = self.get_instance_generic(instance_uid, component)
		if instance_uid is None:
			self.xyz[component] = value
			changed = True
		else:
			if instance_uid in self._instances:
				instance_vertice = self._instances[instance_uid]
				instance_vertice.xyz[component] = value
				if self.equals(instance_vertice):
					self._instances.pop(instance_uid)
				changed = True
			else:
				if value != self.xyz[component]:
					instance_vertice = Vertex(self.x, self.y, self.z)
					instance_vertice.xyz[component] = value
					self._instances[instance_uid] = instance_vertice
					changed = True
		if changed:
			name = components[component]
			change_object = self.create_value_change_object(value, old_value, component, instance_uid)
			self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, change_object))

	def set_instance_x(self, instance_uid, value):
		self.set_instance_generic(instance_uid, value, 0)

	def set_instance_y(self, instance_uid, value):
		self.set_instance_generic(instance_uid, value, 1)

	def set_instance_z(self, instance_uid, value):
		self.set_instance_generic(instance_uid, value, 2)

	def get_instance_generic(self, instance_uid, component):
		if self._component_parameters[component] is None:
			if instance_uid in self._instances:
				return self._instances[instance_uid].xyz[component]
			return self.xyz[component]
		else:
			return self._component_parameters[component].get_instance_value(instance_uid)

	def get_instance_x(self, instance_uid):
		return self.get_instance_generic(instance_uid, 0)

	def get_instance_y(self, instance_uid):
		return self.get_instance_generic(instance_uid, 1)

	def get_instance_z(self, instance_uid):
		return self.get_instance_generic(instance_uid, 2)

	def get_instance_xyz(self, instance_uid):
		if instance_uid in self._instances:
			return self._instances[instance_uid].xyz
		return self.xyz

	def get_instance(self, instance_uid):
		if instance_uid in self._instances:
			return self._instances[instance_uid]
		return self

	@property
	def x(self):
		return self.xyz[0]

	@property
	def y(self):
		return self.xyz[1]

	@property
	def z(self):
		return self.xyz[2]

	@x.setter
	def x(self, value):
		self.set_instance_generic(None, value, 0)

	@y.setter
	def y(self, value):
		self.set_instance_generic(None, value, 1)

	@z.setter
	def z(self, value):
		self.set_instance_generic(None, value, 2)

	def set_parameter_generic(self, param_uid, component):
		old_value = self.get_instance_generic(None, component)
		if self._component_parameters[component] is not None:
			self._component_parameters[component].remove_change_handler(self._component_change_handlers[component])
			self._component_parameters[component] = None
		if param_uid is not None:
			param =  self._parameters.get_parameter_by_uid(param_uid)
			self._component_parameters[component] = param
			if param is not None:
				new_value = self.get_instance_generic(None, component)
				param.add_change_handler(self._component_change_handlers[component])
				change_object = self.create_value_change_object(new_value, old_value, component, None)
				self._component_change_handlers[component](ChangeEvent(self, ChangeEvent.ValueChanged, change_object))

	def set_x_parameter(self, param_uid):
		self.set_parameter_generic(param_uid, 0)

	def set_y_parameter(self, param_uid):
		self.set_parameter_generic(param_uid, 1)

	def set_z_parameter(self, param_uid):
		self.set_parameter_generic(param_uid, 2)

	def on_param_changed_generic(self, event, component):
		instance = None
		if 'instance' in event.object:
			instance = event.object['instance']
		old_value = self.get_instance_generic(instance, component)
		new_value = float(self._component_parameters[component].evaluate(instance))
		self.set_instance_generic(instance, new_value, component)
		if event.type == ChangeEvent.Deleted:
			event.object.remove_change_handler(self._component_change_handlers[component])
			self._component_parameters[component] = None
		change_object = self.create_value_change_object(new_value, old_value, component, instance)
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, change_object))

	def on_x_param_changed(self, event):
		self.on_param_changed_generic(event, 0)

	def on_y_param_changed(self, event):
		self.on_param_changed_generic(event, 1)

	def on_z_param_changed(self, event):
		self.on_param_changed_generic(event, 2)

	def get_param_uid(self, param):
		if param is None:
			return None
		else:
			return param.uid

	def serialize_json(self):
		return \
			{
				'p3d': Point3d.serialize_json(self),
				'no': NamedObservableObject.serialize_json(self),
				'instances': self._instances,
				'x_param_uid': self.get_param_uid(self._component_parameters[0]),
				'y_param_uid': self.get_param_uid(self._component_parameters[1]),
				'z_param_uid': self.get_param_uid(self._component_parameters[2])
			}

	@staticmethod
	def deserialize(data, parameters):
		key_point = KeyPoint(parameters)
		key_point.deserialize_data(data)
		return key_point

	def deserialize_data(self, data):
		Point3d.deserialize_data(self, data.get('p3d'))
		if 'no' in data:
			NamedObservableObject.deserialize_data(self, data['no'])
		else:
			self.name = "Keypoint"
		for instance_tuple in data.get('instances', {}).items():
			instance_uid = instance_tuple[0]
			vertex = Vertex.deserialize(instance_tuple[1])
			self._instances[instance_uid] = vertex
		self.set_parameter_generic(data['x_param_uid'], 0)
		self.set_parameter_generic(data['y_param_uid'], 1)
		self.set_parameter_generic(data['z_param_uid'], 2)

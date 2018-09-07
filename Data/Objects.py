import uuid

from Data.Events import ValueChangeEvent, ChangeEvent

__author__ = 'mamj'


class IdObject(object):
	def __init__(self):
		uid = uuid.uuid1().urn[9:]
		self._uid = uid

	@property
	def uid(self):
		return self._uid

	def serialize_json(self):
		return {'uid': self._uid}

	def deserialize_data(self, data):
		self._uid = data['uid']


class ObservableObject(object):
	def __init__(self):
		self._change_handlers = set()
		self._is_modified = False

	def changed(self, event):
		self._is_modified = True
		for handler in list(self._change_handlers):
			# print(str(handler))
			handler(event)

	@property
	def is_modified(self):
		return self._is_modified

	@is_modified.setter
	def is_modified(self, value):
		self._is_modified = value

	def add_change_handler(self, change_handler):
		self._change_handlers.add(change_handler)

	def remove_change_handler(self, change_handler):
		try:
			self._change_handlers.remove(change_handler)
		except KeyError:
			pass

	@property
	def change_handlers(self):
		return list(self._change_handlers)


class NamedObservableObject(ObservableObject):
	def __init__(self, name="No name"):
		ObservableObject.__init__(self)
		self._name = name

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		old_value = self._name
		self._name = value
		self.changed(ValueChangeEvent(self, 'name', old_value, value))

	def serialize_json(self):
		return {'name': self._name}

	def deserialize_data(self, data):
		self._name = data['name']


class MetaDataObject(ObservableObject):
	def __init__(self, parameters):
		ObservableObject.__init__(self)
		self._parameters = parameters
		self._meta_data = {}
		self._meta_data_parameters = {}

	def clear(self):
		for uid in self._meta_data_parameters:
			param = self._parameters.get_parameter_by_uid(uid)
			param.remove_change_handler(self.on_parameter_change)
		self._meta_data_parameters = {}
		self._meta_data = {}

	def set_meta_data(self, name, value):
		for param_tuple in self._meta_data_parameters.items():
			if param_tuple[1] == name:
				param = self._parameters.get_parameter_by_uid(param_tuple[0])
				param.value = value
				return
		self._meta_data[name] = value

	def get_meta_data(self, name, instance=None):
		if instance is None:
			return self._meta_data[name]
		else:
			param = self.get_meta_data_parameter(name)
			if param is None:
				return self._meta_data[name]
			else:
				return param.get_instance_value(instance)

	def get_meta_data_parameter(self, name):
		for param_tuple in self._meta_data_parameters.items():
			if param_tuple[1] == name:
				return self._parameters.get_parameter_by_uid(param_tuple[0])
		return None

	def set_meta_data_parameter(self, name, parameter):
		self._meta_data_parameters[parameter.uid] = name
		param = self._parameters.get_parameter_by_uid(parameter.uid)
		self._meta_data[name] = param.value
		param.add_change_handler(self.on_parameter_change)

	def on_parameter_change(self, event):
		param = event.sender
		uid = param.uid
		meta_name = self._meta_data_parameters[uid]
		self._meta_data[meta_name] = param.value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'name': meta_name, 'parameter': param, 'param_change_event': event}))

	def serialize_json(self):
		return {
			'meta_data': self._meta_data,
			'meta_data_parameters': self._meta_data_parameters
		}

	def deserialize_data(self, data):
		if data is None:
			return
		self._meta_data = data.get('meta_data')
		self._meta_data_parameters = data.get('meta_data_parameters')
		for parameter_uid in self._meta_data_parameters:
			param = self._parameters.get_parameter_by_uid(parameter_uid)
			if param is not None:
				param.add_change_handler(self.on_parameter_change)
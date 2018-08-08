from Business.Undo import DoObject
from Data.Events import ChangeEvent
from Data.Parameters import Parameters, Parameter


class AddParameterDoObject(DoObject):
	def __init__(self, parameter):
		DoObject.__init__(self)
		self._parameter = parameter
		self._parameters = parameter.parent
		self._name = parameter.name
		self._value = parameter.value

	def undo(self):
		self._name = self._parameter.name
		self._value = self._parameter.value
		self._parameters.delete_parameter(self._parameter.uid)

	def redo(self):
		self._parameter = self._parameters.create_parameter(self._name, self._value)


class ChangeParameterDoObject(DoObject):
	def __init__(self, parameter, new_value, old_value, old_formula, instance):
		DoObject.__init__(self)
		self._parameter = parameter
		self._new_value = new_value
		self._old_value = old_value
		self._old_formula = old_formula
		self._instance = instance

	def undo(self):
		old_value = None
		value = self._old_value
		if self._instance is None:
			self._parameter._instance_values[self._instance] = self._old_value
			self._parameter._instance_formula[self._instance] = self._old_formula
		else:
			self._parameter._value = self._old_value
			self._parameter._formula = self._old_formula
		change_object = {
			'new value': self._old_value,
			'old value': self._new_value,
			'instance': self._instance
		}
		self._parameter.changed(ChangeEvent(self._parameter, ChangeEvent.ValueChanged, change_object))

	def redo(self):
		self._parameter = self._parameter.parent.get_parameter_by_name(self._parameter.name)
		self._parameter.set_instance_value(self._instance, self._new_value)


class ChangeParameterNameDoObject(DoObject):
	def __init__(self, parameter, old_name, new_name):
		DoObject.__init__(self)
		self._old_name = old_name
		self._new_name = new_name
		self._parameter = parameter
		self._parameters = parameter.parent

	def undo(self):
		self._parameter.name = self._old_name

	def redo(self):
		self._parameter = self._parameters.get_parameter_by_name(self._old_name)
		self._parameter.name = self._new_name


class DeleteParametersDoObject(DoObject):
	def __init__(self, parent, parameters, dependents):
		DoObject.__init__(self)
		self._parameters = parameters
		self._parent = parent
		self._dependents = dependents

	def undo(self):
		for param in self._parameters:
			self._parent._add_parameter_object(param)

		for param in self._parameters:
			try:
				value = float(param.formula)
				param.value = value
			except ValueError:
				param.value = param.formula

		for param in self._dependents:
			try:
				value = float(param.formula)
				param.value = value
			except ValueError:
				param.value = param.formula

	def redo(self):
		new_param_list = []
		for param in self._parameters:
			new_param_list.append(self._parent.get_parameter_by_name(param.name))
		self._parameters = new_param_list
		self._parent.delete_parameters(self._parameters)


def add_parameter(parameters_object: Parameters):
	parameter = parameters_object.create_parameter()
	parameters_object.document.undo_stack.append(AddParameterDoObject(parameter))
	return parameter


def set_parameter(parameter, value, instance):
	old_value = parameter._value
	old_formula = parameter._formula
	#parameter.value = value
	parameter.set_instance_value(instance, value)
	parameter.parent.document.undo_stack.append(ChangeParameterDoObject(parameter, value, old_value, old_formula, instance))


def set_parameter_name(parameter, name):
	old_name = parameter.name
	parameter.name = name
	parameter.parent.document.undo_stack.append(ChangeParameterNameDoObject(parameter, old_name, name))


def delete_parameters(parent, parameters):
	dependents = []
	for param in parameters:
		for change_handler in param.change_handlers:
			obj = change_handler.__self__
			if type(obj) is Parameter or issubclass(type(obj), Parameter):
				dependents.append(obj)
	parent.delete_parameters(parameters)
	parent.document.undo_stack.append(DeleteParametersDoObject(parent, parameters, dependents))

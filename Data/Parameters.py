from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Objects import IdObject, ObservableObject, NamedObservableObject
import ast
import operator as op
import re
import math

__author__ = 'mamj'

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
						 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
						 ast.USub: op.neg}

operator_keys = ['+', '-', '*', '/', '^', '(', ')', ',']
true_strings = ['true', 'yes', '1', 't', 'y']


def pi_func():
	return math.pi


funcs = {
	'sin': math.sin,
	'cos': math.cos,
	'tan': math.tan,
	'abs': abs,
	'asin': math.asin,
	'acos': math.acos,
	'atan': math.atan,
	'atan2': math.atan2,
	'sqrt': math.sqrt,
	'pi': pi_func,
	'log': math.log,
	'log10': math.log10
}


def boolean(value):
	return str(value).lower() in true_strings


def eval_expr(expr):
	return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
	if isinstance(node, ast.Num):  # <number>
		return node.n
	elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
		return operators[type(node.op)](eval_(node.left), eval_(node.right))
	elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
		return operators[type(node.op)](eval_(node.operand))
	elif isinstance(node, ast.Call):
		if node.func.id in funcs:
			if len(node.args) == 1:
				return funcs[node.func.id](eval_(node.args[0]))
			elif len(node.args) == 2:
				return funcs[node.func.id](eval_(node.args[0]), eval_(node.args[1]))
			else:
				return funcs[node.func.id]()
	else:
		raise TypeError(node)


def insert_spaces(formula):
	for key in operator_keys:
		formula = formula.replace(key, " " + key + " ")
	return formula


class Parameter(IdObject, ObservableObject):
	def __init__(self, parent, name='new parameter', value=0.0):
		IdObject.__init__(self)
		ObservableObject.__init__(self)
		self._parent = parent
		self._name = name
		self._value = value
		self._instance_values = {}
		self._instance_formula = {}
		self._formula = str(value)
		self._change_senders = []
		self._instance_change_senders = {}
		self._hidden = False
		self._arguments = []
		self._base_unit = False
		self._units = {}
		self._locked = False

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		old_name = self._name
		if '(' in value:
			args = re.findall("\((.*?)\)", value)
			self._arguments = str.split(args[0], ',')
			self._name = value.replace("(" + args[0] + ")", "")
		else:
			self._name = value
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'old_name': old_name, 'new_name': self._name}))

	@property
	def full_name(self):
		args = ""
		if len(self._arguments) > 0:
			args = "("
			first = True
			for arg in self._arguments:
				if first:
					first = False
				else:
					args += ","
				args += arg
			args += ")"
		return self._name + args

	@property
	def parent(self):
		return self._parent

	@property
	def locked(self):
		return self._locked

	@locked.setter
	def locked(self, value):
		if type(value) is not bool:
			value = boolean(value)
		self._locked = value

	@property
	def hidden(self):
		return self._hidden

	@hidden.setter
	def hidden(self, value):
		old_val = self._hidden
		if type(value) is not bool:
			value = boolean(value)
		self._hidden = value
		if value != old_val:
			self.changed(ChangeEvent(self, ChangeEvent.HiddenChanged, {'new value': value, 'old value': old_val}))

	@property
	def value_view(self):
		return self._value

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, value):
		self.set_instance_value(None, value)

	def get_instance_value(self, instance_uid):
		if instance_uid in self._instance_values:
			return self._instance_values[instance_uid]
		return self._value

	def create_value_change_object(self, new_value, old_value, old_formula, instance_uid):
		change_object = {
			'new value': new_value,
			'old value': old_value,
			'new formula': self.get_instance_internal_formula(instance_uid),
			'old formula': old_formula,
			'instance': instance_uid
		}
		return change_object

	def set_instance_value(self, instance_uid, value):
		if self._base_unit:
			raise ValueError("Base unit can only have value = 1")
		elif self._locked:
			raise ValueError("This parameter " + self.name + " has been locked")
		old_value = self.get_instance_value(instance_uid)
		old_formula = self.get_instance_internal_formula(instance_uid)
		if value is None and instance_uid is not None:
			if instance_uid in self._instance_values:
				self._instance_values.pop(instance_uid)
			if instance_uid in self._instance_formula:
				self._instance_formula.pop(instance_uid)
		else:
			self.clear_change_handler(instance_uid)
			if isinstance(value, str):
				formula = " " + insert_spaces(value) + " "
				params = self._parent.get_all_parameters()
				for param in params:
					if " " + param.name + " " in formula:
						if param is self:
							raise Exception("Formula may not reference it self.")
						formula = formula.replace(" " + param.name + " ", '{' + param.uid + '}')
						param.add_change_handler(self.on_parameter_changed)
						self._change_senders.append(param)
				if instance_uid is None:
					self._formula = formula.replace(' ', '')
					new_value = self.evaluate(instance_uid)
					if type(new_value) is str:
						new_value = value
						self._formula = value
					self._value = new_value
				else:
					self.set_instance_internal_formula(instance_uid, formula.replace(' ', ''))
					new_value = self.evaluate(instance_uid)
					if type(new_value) is str:
						new_value = value
						self.set_instance_internal_formula(instance_uid, value)
					self.set_instance_internal_value(instance_uid, new_value)
			else:
				if instance_uid is None:
					self._formula = str(value)
					new_value = value
					self._value = value
				else:
					self.set_instance_internal_formula(instance_uid, str(value))
					new_value = value
					self.set_instance_internal_value(instance_uid, value)
		change_object = self.create_value_change_object(new_value, old_value, old_formula, instance_uid)
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, change_object))

	@property
	def formula(self):
		return self.get_instance_formula(None)

	def get_instance_formula(self, instance_uid):
		formula = ""
		if instance_uid is None:
			formula = self._formula
		else:
			if instance_uid in self._instance_formula:
				formula = self._instance_formula[instance_uid]
			else:
				formula = self._formula
		uids = re.findall("{(.*?)}", formula)
		expr = formula
		if formula != "":
			for uid in uids:
				param = self._parent.get_parameter_by_uid(uid)
				expr = expr.replace('{' + uid + '}', param.name)
		return expr

	@property
	def internal_formula(self):
		return self._formula

	@internal_formula.setter
	def internal_formula(self, value):
		self._formula = value

	@property
	def internal_value(self):
		return self._value

	@internal_value.setter
	def internal_value(self, value):
		self._value = value

	def get_instance_internal_formula(self, instance_uid):
		if instance_uid in self._instance_formula:
			return self._instance_formula[instance_uid]
		return self._formula

	def set_instance_internal_formula(self, instance_uid, value):
		if instance_uid in self._instance_formula:
			if value == self._formula:
				self._instance_formula.pop(instance_uid)
			else:
				self._instance_formula[instance_uid] = value
		else:
			if value != self._formula:
				self._instance_formula[instance_uid] = value

	def get_instance_internal_value(self, instance_uid):
		if instance_uid in self._instance_values:
			return self._instance_values[instance_uid]
		return self._value

	def set_instance_internal_value(self, instance_uid, value):
		if instance_uid in self._instance_values:
			if value == self._value:
				self._instance_values.pop(instance_uid)
			else:
				self._instance_values[instance_uid] = value
		else:
			if value != self._formula:
				self._instance_values[instance_uid] = value

	@property
	def base_unit(self):
		return self._base_unit

	@base_unit.setter
	def base_unit(self, value):
		if type(value) is not bool:
			value = boolean(value)
		if value:
			if len(self._units) == 0:
				self._base_unit = value
				self._value = 1
				self._formula = "1"
				self._units[self.uid] = [1, self]
			else:
				raise Exception("Base unit can not be based on other units.")
		else:
			self._units.clear()
			self._base_unit = value

	@property
	def units(self):
		return self._units.values()

	def formula_factored(self, factor):
		sets = []
		expr = ""
		for set1 in self._formula.split("{"):
			for set2 in set1.split("}"):
				sets.append(set2)

		for i in range(len(sets)):
			if i % 2 == 0:
				try:
					expr += re.sub(r'([0-9]*\.[0-9]+|[0-9]+)', lambda m: str(float(m.groups()[0]) * factor), sets[i])
				except ValueError:
					pass
			else:
				expr += "{" + sets[i] + "}"
		uids = re.findall("{(.*?)}", self._formula)
		for uid in uids:
			param = self._parent.get_parameter_by_uid(uid)
			expr = expr.replace('{' + uid + '}', param.name)
		return expr

	def get_depend_params(self):
		depends = []
		uids = re.findall("{(.*?)}", self._formula)
		for uid in uids:
			param = self._parent.get_parameter_by_uid(uid)
			sub_params = param.get_depend_params()
			for sub_param in sub_params:
				depends.append(sub_param)
			depends.append(param)
		return depends

	def evaluate(self, instance_uid=None):
		if instance_uid is None:
			formula = self._formula
		else:
			if instance_uid in self._instance_formula:
				formula = self._instance_formula[instance_uid]
			else:
				formula = self._formula
		uids = re.findall("{(.*?)}", formula)
		expr = formula
		for uid in uids:
			param = self._parent.get_parameter_by_uid(uid)
			expr = expr.replace('{' + uid + '}', str(param.get_instance_value(instance_uid)))
		try:
			return eval_expr(expr)
		except (TypeError):
			return expr

	def clear_change_handler(self, instance_uid):
		if instance_uid is None:
			for param in self._change_senders:
				param.remove_change_handler(self.on_parameter_changed)
			self._change_senders = []
		else:
			if instance_uid in self._instance_change_senders:
				for param in self._instance_change_senders[instance_uid]:
					param.remove_change_handler(self.on_parameter_changed)
				self._instance_change_senders[instance_uid] = []

	def on_parameter_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			self._formula = self._formula.replace('{' + event.object.uid + '}', event.object.name)
		if 'instance' in event.object:
			instance_uid = event.object['instance']
		else:
			instance_uid = None

		if instance_uid is None:
			old_value = self._value
			self._value = self.evaluate(instance_uid)
			new_value = self._value
			for formula_tuple in self._instance_formula.items():
				uid = formula_tuple[0]
				if event.sender.uid in formula_tuple[1]:
					self.set_instance_internal_value(uid, self.evaluate(uid))
		else:
			old_value = self.get_instance_value(instance_uid)
			new_value = self.evaluate(instance_uid)
			if new_value != self._value:
				self._instance_values[instance_uid] = new_value
			else:
				if instance_uid in self._instance_values:
					self._instance_values.pop(instance_uid)

		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'new value': new_value, 'old value': old_value, 'instance': instance_uid}))

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'name': self.name,
			'value': self._value,
			'inval': self._instance_values,
			'formula': self._formula,
			'inform': self._instance_formula,
			'hidden': self._hidden
		}

	@staticmethod
	def deserialize(data, parameters):
		param = Parameter(parameters)
		param.deserialize_data(data)
		return param

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		self._value = data.get('value', 0.0)
		self._formula = data.get('formula', "")
		self.name = data.get('name', 'name missing')
		self._hidden = data.get('hidden', False)
		self._instance_values = data.get('inval', {})
		self._instance_formula = data.get('inform', {})


class ParametersBase(NamedObservableObject):
	def __init__(self, name):
		NamedObservableObject.__init__(self, name)


class Parameters(ParametersBase):
	def __init__(self, name, parent=None):
		ParametersBase.__init__(self, name)
		self._parameter_list = []
		self._params = {}
		self._parent = parent
		self._custom_name_getter = None
		self._standards = {}
		self._current_standard_name = "Normal"
		self._current_type_name = "Default"
		self._current_type = self.make_type(self._current_standard_name, self._current_type_name)

	@property
	def document(self):
		if self._parent is None:
			return self
		else:
			return self._parent.document

	@property
	def parent(self):
		return self._parent

	def param_in_current_type(self, param):
		if self._current_type is None:
			return False
		return param.uid in self._current_type

	def make_standard(self, name):
		standard = {}
		self._standards[name] = standard
		return standard

	@property
	def standards(self):
		return list(self._standards.keys())

	@property
	def standard(self):
		return self._current_standard_name

	@standard.setter
	def standard(self, value):
		if value in self._standards:
			self._current_standard_name = value
			self._current_type_name = ""
			self._current_type = None

	@property
	def types(self):
		return self._standards[self._current_standard_name].keys()

	def get_types_from_standard(self, standard):
		if standard in self._standards:
			return list(self._standards[standard].keys())
		return []

	def make_type(self, standard_name, type_name):
		if standard_name not in self._standards:
			standard = {}
			self._standards[standard_name] = standard
		else:
			standard = self._standards[standard_name]
		type = {}
		standard[type_name] = type
		return type

	@property
	def type(self):
		return self._current_type_name

	@type.setter
	def type(self, type_name):
		if type_name in self._standards[self._current_standard_name]:
			self._current_type = self._standards[self._current_standard_name][type_name]
			self._current_type_name = type_name
			if self._current_type is None:
				return
			for param_definition_tuple in self._current_type.items():
				uid = param_definition_tuple[0]
				val = param_definition_tuple[1]
				if uid in self._params:
					param = self._params[uid]
					old_value = param.value
					param.internal_formula = val['if']
					param.internal_value = param.evaluate(None)
					change_object = {
						'new value': param.value,
						'old value': old_value,
						'instance': None
					}
					param.changed(ChangeEvent(param, ChangeEvent.ValueChanged, change_object))
			self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self))

	def _add_parameter_object(self, param):
		param.add_change_handler(self.on_parameter_changed)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, param))
		self._params[param.uid] = param
		self._parameter_list.append(param.uid)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, param))

	def _remove_parameter_object(self, uid):
		if uid in self._params:
			self._params.pop(uid)

	def get_parameter_by_uid(self, uid) -> Parameter:
		if uid in self._params:
			return self._params[uid]
		elif self._parent is not None:
			return self._parent.get_parameter_by_uid(uid)
		else:
			return None

	def get_parameter_by_name(self, name) -> Parameter:
		param = None
		for prm in self._params.values():
			if prm.name == name:
				param = prm
		if param is None and self._custom_name_getter is not None:
			param = self._custom_name_getter(name)
		if param is None and self._parent is not None:
			param = self._parent.get_parameter_by_name(name)

		return param

	def get_all_local_parameters(self):
		params = list(self._params.items())
		return params

	def get_all_parameters(self):
		params = list(self._params.values())
		if self._parent is not None:
			params.extend(self._parent.get_all_parameters())
		return params

	def create_parameter(self, name=None, value=0.0):
		if name is None:
			if self._parent is None:
				name = "Global" + str(len(self._parameter_list))
			else:
				name = self.name + str(len(self._parameter_list))
		param = Parameter(self, name, value)
		self._add_parameter_object(param)
		return param

	def delete_parameter(self, uid):
		param = self.get_parameter_by_uid(uid)
		if param is not None:
			param.remove_change_handler(self.on_parameter_changed)
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, param))
			self._parameter_list.remove(uid)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, param))
			self._remove_parameter_object(uid)
			param.changed(ChangeEvent(param, ChangeEvent.Deleted, param))

	def delete_parameters(self, params):
		for param in params:
			if param.uid in self._parameter_list:
				self.delete_parameter(param.uid)

	def on_parameter_changed(self, event):
		param = event.sender
		self.changed(ChangeEvent(self, event.type, event.sender))
		if self._current_type is not None and param.uid in self._params:
			if 'instance' in event.object and 'new formula' in event.object:
				if event.object['instance'] is None and event.object['new formula'] != event.object['old formula']:

					if param.uid in self._current_type:
						predef = self._current_type[param.uid]
					else:
						predef = {}
						self._current_type[param.uid] = predef
					predef['if'] = param.internal_formula
					predef['iv'] = param.internal_value

	def get_index_of(self, parameter):
		if parameter.uid in self._parameter_list:
			return self._parameter_list.index(parameter.uid)
		else:
			return -1

	@property
	def length(self):
		return len(self._parameter_list)

	@property
	def length_all(self):
		if self._parent is not None:
			return self._parent.length_all + self.length
		else:
			return self.length

	def get_parameter_item(self, index):
		if index >= self.length:
			return self._parent.get_parameter_item(index - self.length)
		else:
			uid = self._parameter_list[index]
		param = self.get_parameter_by_uid(uid)
		return param

	def serialize_json(self):
		return {
			'name': self._name,
			'params': self._params,
			'parameter_list': self._parameter_list,
			'pps': self._standards,
			'csn': self._current_standard_name,
			'ctn': self._current_type_name
		}

	@staticmethod
	def deserialize(data, parent):
		param = Parameters(parent)
		param.deserialize_data(data)
		return param

	def deserialize_data(self, data):
		self._parameter_list = data.get('parameter_list', [])
		self._name = data.get('name', 'name missing')
		self._standards = data.get('pps', self._standards)
		self._current_standard_name = data.get("csn", self._current_standard_name)
		self._current_type_name = data.get("ctn", self._current_type_name)
		self._current_type = self._standards[self._current_standard_name][self._current_type_name]
		for param_data in data.get('params', {}).items():
			param = Parameter.deserialize(param_data[1], self)
			self._params[param.uid] = param
			param.add_change_handler(self.on_parameter_changed)

		for param_tuple in self._params.items():
			if param_tuple[1].formula != '':
				try:
					param_tuple[1].value = param_tuple[1].formula
				except Exception as e:
					pass


class ParametersInstance(IdObject, ParametersBase):
	def __init__(self, name):
		ParametersBase.__init__(self, name)
		IdObject.__init__(self)
		self._parameters = None
		self._current_standard_name = ""
		self._current_type_name = ""

	@property
	def document(self):
		if self._parameters is None:
			return None
		return self._parameters.document

	@property
	def length(self):
		if self._parameters is None:
			return 0
		return self._parameters.length

	@property
	def length_all(self):
		if self._parameters is None:
			return 0
		return self._parameters.length_all

	def get_parameter_item(self, index):
		if self._parameters is None:
			return None
		return self._parameters.get_parameter_item(index)

	@property
	def standards(self):
		if self._parameters is None:
			return []
		return self._parameters.standards

	def get_types_from_standard(self, standard):
		if self._parameters is None:
			return []
		return self._parameters.get_types_from_standard(standard)

	@property
	def standard(self):
		return self._current_standard_name

	@standard.setter
	def standard(self, value):
		self._current_standard_name = value

	@property
	def type(self):
	    return self._current_type_name

	@type.setter
	def type(self, type_name):
		if self._parameters is None:
			return
		current_type = self._parameters._standards[self._current_standard_name][type_name]
		self._current_type_name = type_name

		for param_definition_tuple in current_type.items():
			uid = param_definition_tuple[0]
			val = param_definition_tuple[1]

			param = self._parameters.get_parameter_by_uid(uid)
			if param is not None:
				old_value = param.value
				param.set_instance_internal_formula(self.uid, val['if'])
				param.set_instance_internal_value(self.uid, param.evaluate(self.uid))
				change_object = {
					'new value': param.value,
					'old value': old_value,
					'instance': self.uid
				}
				param.changed(ChangeEvent(param, ChangeEvent.ValueChanged, change_object))
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self))

	def param_in_current_type(self, index):
		return False

	def delete_parameters(self, params):
		raise Exception("Parameters can not be deleted on instance")

	def delete_parameter(self, uid):
		raise Exception("Parameters can not be deleted on instance")

	def get_parameter_by_uid(self, uid) -> Parameter:
		if self._parameters is None:
			return None
		return self._parameters.get_parameter_by_uid(uid)

	def get_parameter_by_name(self, name) -> Parameter:
		if self._parameters is None:
			return None
		return self._parameters.get_parameter_by_name()

	def get_all_local_parameters(self):
		if self._parameters is None:
			return []
		return self._parameters.get_all_local_parameters()

	def get_all_parameters(self):
		if self._parameters is None:
			return []
		return self._parameters.get_all_parameters()

	def create_parameter(self, name=None, value=0.0):
		raise Exception("Parameters can not be created on instance")
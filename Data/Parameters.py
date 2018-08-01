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
    self._formula = str(value)
    self._change_senders = []
    self._hidden = False
    self._arguments = []
    self._base_unit = False
    self._units = {}

  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, value):
    if '(' in value:
      args = re.findall("\((.*?)\)", value)
      self._arguments = str.split(args[0], ',')
      self._name = value.replace("(" + args[0] + ")", "")
    else:
      self._name = value
    self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

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

  def serialize_json(self):
    return {
      'uid': IdObject.serialize_json(self),
      'name': self.name,
      'value': self._value,
      'formula': self._formula,
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

  @property
  def hidden(self):
    return self._hidden

  @hidden.setter
  def hidden(self, hide):
    old_val = self._hidden
    self._hidden = hide
    if hide != old_val:
      self.changed(ChangeEvent(self, ChangeEvent.HiddenChanged, {'new value': hide, 'old value': old_val}))

  @property
  def value(self):
    return self._value

  @property
  def formula(self):
    uids = re.findall("{(.*?)}", self._formula)
    expr = self._formula
    for uid in uids:
      param = self._parent.get_parameter_by_uid(uid)
      expr = expr.replace('{' + uid + '}', param.name)
    return expr

  @property
  def base_unit(self):
    return self._base_unit

  @base_unit.setter
  def base_unit(self, value):
    if len(self._units) == 0:
      self._base_unit = value
      if value:
        self._units[self.uid] = [1, self]
      else:
        self._units.clear()
    else:
      raise Exception("Base unit can not be based on other units.")

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

  def evaluate(self):
    uids = re.findall("{(.*?)}", self._formula)
    expr = self._formula
    for uid in uids:
      param = self._parent.get_parameter_by_uid(uid)
      expr = expr.replace('{' + uid + '}', str(param.value))
    try:
      return eval_expr(expr)
    except (TypeError):
      return expr

  def clear_change_handler(self):
    for param in self._change_senders:
      param.remove_change_handler(self.on_parameter_changed)
    self._change_senders = []

  def on_parameter_changed(self, event):
    if event.type == ChangeEvent.Deleted:
      self._formula = self._formula.replace('{' + event.object.uid + '}', event.object.name)
    old_value = self._value
    self._value = self.evaluate()
    new_value = self._value
    self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'new value': new_value, 'old value': old_value}))

  @value.setter
  def value(self, value):
    old_value = self._value
    self.clear_change_handler()
    if isinstance(value, str):
      formula = " " + insert_spaces(value) + " "
      params = self._parent.get_all_parameters()
      for param_tuple in params:
        param = param_tuple[1]
        if " " + param.name + " " in formula:
          if param is self:
            raise Exception("Formula may not reference it self.")
          formula = formula.replace(" " + param.name + " ", '{' + param.uid + '}')
          param.add_change_handler(self.on_parameter_changed)
          self._change_senders.append(param)
      self._formula = formula.replace(' ', '')
      self._value = self.evaluate()
    else:
      self._value = value
      self._formula = str(value)
    self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'new value': value, 'old value': old_value}))


class Parameters(NamedObservableObject):
  def __init__(self, name, parent=None):
    NamedObservableObject.__init__(self, name)
    self._parameter_list = []
    self._params = {}
    self._parent = parent
    self._custom_name_getter = None

  @property
  def document(self):
    if self._parent is None:
      return self
    else:
      return self._parent.document

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
    params = list(self._params.items())
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
    self.changed(event)

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
      'parameter_list': self._parameter_list
    }

  @staticmethod
  def deserialize(data, parent):
    param = Parameters(parent)
    param.deserialize_data(data)
    return param

  def deserialize_data(self, data):
    self._parameter_list = data.get('parameter_list', [])
    self._name = data.get('name', 'name missing')
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


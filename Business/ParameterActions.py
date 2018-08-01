from Business.Undo import DoObject
from Data.Events import ChangeEvent
from Data.Parameters import Parameters


class AddParameterDoObject(DoObject):
  def __init__(self, parameter):
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
  def __init__(self, parameter, new_value, old_value, old_formula):
    self._parameter = parameter
    self._new_value = new_value
    self._old_value = old_value
    self._old_formula = old_formula

  def undo(self):
    self._parameter._value = self._old_value
    self._parameter._formula = self._old_formula
    self._parameter.changed(ChangeEvent(self._parameter, ChangeEvent.ValueChanged, self._parameter))

  def redo(self):
    self._parameter.value = self._new_value

def add_parameter(parameters_object: Parameters):
  parameter = parameters_object.create_parameter()
  parameters_object.document.undo_stack.append(AddParameterDoObject(parameter))
  return parameter

def set_parameter(parameter, value):
  old_value = parameter._value
  old_formula = parameter._formula
  parameter.value = value
  parameter.parent.document.undo_stack.append(ChangeParameterDoObject(parameter, value, old_value, old_formula))
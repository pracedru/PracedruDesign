

class DoObject():
  def __init__(self):
    pass

  def undo(self):
    raise Exception("This DoObject has not been fully implemented")

  def redo(self):
    raise Exception("This DoObject has not been fully implemented")

class ChangeNameDoObject(DoObject):
  def __init__(self, named_object, old_name, new_name):
    self._named_object = named_object
    self._old_name = old_name
    self._new_name = new_name

  def undo(self):
    self._named_object.name = self._old_name

  def redo(self):
    self._named_object.name = self._new_name


class ChangePropertyDoObject(DoObject):
  def __init__(self, obj, property_name, old_value, new_value):
    self._obj = obj
    self._property_name = property_name
    self._old_value = old_value
    self._new_value = new_value

  def undo(self):
    setattr(self._obj, self._property_name, self._old_value)

  def redo(self):
    setattr(self._obj, self._property_name, self._new_value)


def on_undo(document):
  if len(document.undo_stack) > 0:
    do_object = document.undo_stack.pop()
    do_object.undo()


def on_redo(document):
  if len(document.redo_stack) > 0:
    do_object = document.redo_stack.pop()
    do_object.redo()

def change_name(doc, named_object, new_name):
  old_name = named_object.name
  named_object.name = new_name
  doc.undo_stack.append(ChangeNameDoObject(named_object, old_name, new_name))

def change_property(doc, obj, prop_name, new_value):
  old_value = getattr(obj, prop_name)
  setattr(obj, prop_name, new_value)
  doc.undo_stack.append(ChangePropertyDoObject(obj, prop_name, old_value, new_value))


class DoObject():
  def __init__(self):
    pass

  def undo(self):
    raise Exception("This DoObject has not been fully implemented")

  def redo(self):
    raise Exception("This DoObject has not been fully implemented")


def on_undo(document):
  if len(document.undo_stack) > 0:
    do_object = document.undo_stack.pop()
    do_object.undo()


def on_redo(document):
  if len(document.redo_stack) > 0:
    do_object = document.redo_stack.pop()
    do_object.redo()

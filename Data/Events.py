__author__ = 'mamj'


class Event(object):
  def __init__(self, sender):
    self.sender = sender


class ChangeEvent(Event):
  ObjectAdded = 1
  ObjectRemoved = 2
  ValueChanged = 3
  BeforeObjectAdded = 4
  BeforeObjectRemoved = 5
  Cleared = 6
  Deleted = 7
  HiddenChanged = 8
  ObjectChanged = 9
  BeforeCleared = 10

  def __init__(self, sender, type, object):
    Event.__init__(self, sender)
    self.type = type
    self.object = object


class ValueChangeEvent(ChangeEvent):
  def __init__(self, sender, name, old_value, new_value):
    ChangeEvent.__init__(self, sender, ChangeEvent.ValueChanged, name)
    self.old_value = old_value
    self.new_value = new_value

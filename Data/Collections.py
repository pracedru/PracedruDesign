from Data.Events import ChangeEvent
from Data.Objects import ObservableObject


class ObservableList(list, ObservableObject):
  def __init__(self):
    list.__init__(self)
    ObservableObject.__init__(self)

  def append(self, obj):
    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, obj))
    list.append(self, obj)
    self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, obj))

  def remove(self, obj):
    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, obj))
    list.remove(self, obj)
    self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, obj))

  def pop(self, index: int = -1):
    if index == -1:
      obj =  self[len(self)-1]
    else:
      obj = self[index]
    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, obj))
    list.pop(self, index)
    self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, obj))
    return obj

  def insert(self, index: int, obj):
    self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, obj))
    list.insert(self, index, obj)
    self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, obj))

  def clear(self):
    self.changed(ChangeEvent(self, ChangeEvent.BeforeCleared, None))
    list.clear(self)
    self.changed(ChangeEvent(self, ChangeEvent.Cleared, None))

  def sneak_append(self, obj):
    list.append(self, obj)
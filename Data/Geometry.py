from Data.Objects import IdObject, ObservableObject

__author__ = 'mamj'




class Geometry(ObservableObject, IdObject):
    def __init__(self, parent):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._parent = parent

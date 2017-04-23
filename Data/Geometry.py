from Data.Objects import IdObject, ObservableObject
from Data.Parameters import Parameters

__author__ = 'mamj'


class Geometry(Parameters, IdObject):
    Sketch = 0
    Part = 1
    Assembly = 2

    def __init__(self, parent, name, geometry_type):
        IdObject.__init__(self)
        Parameters.__init__(self, name, parent)
        self._parent = parent
        self._geometry_type = geometry_type

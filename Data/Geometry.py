from Data.Objects import IdObject

__author__ = 'mamj'


class Geometry(object):
    LineEdge = 0
    ArcEdge = 1
    EllipseEdge = 2

    def __init__(self):
        object.__init__(self)
        self._edges = []

    def get_edges(self):
        return self._edges

    def serialize_json(self):
        return {'edges': self._edges}

    @staticmethod
    def deserialize(data):
        geom = Geometry()
        if data is not None:
            geom.deserialize_data(data)
        return geom

    def deserialize_data(self, data):
        self._edges = data.get('edges', [])


class CoordinateSystem(IdObject):
    def __init__(self):
        IdObject.__init__()
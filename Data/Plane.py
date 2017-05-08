import numpy as np
from math import *
from Data.Objects import NamedObservableObject, IdObject
from Data.Vertex import Vertex


class Plane(NamedObservableObject, IdObject):
    def __init__(self, x_axis=Vertex(1, 0, 0), y_axis=Vertex(0, 1, 0), position=Vertex(0, 0, 0), name="New plane"):
        NamedObservableObject.__init__(self, name)
        IdObject.__init__(self)
        self._position = position
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._pm = None

    @property
    def normal(self):
        cp = np.cross(self._x_axis.xyz, self._y_axis.xyz)
        n = cp / np.linalg.norm(cp)
        return Vertex(n[0], n[1], n[2])

    def get_local_projection_matrix(self):
        if self._pm is None:
            v1 = self._x_axis.xyz / np.linalg.norm(self._x_axis.xyz)
            v2 = self._y_axis.xyz / np.linalg.norm(self._y_axis.xyz)
            v3 = self.normal.xyz
            pm = np.array([v1, v2, v3])
            self._pm = pm
        else:
            pm = self._pm
        return pm

    def get_global_projection_matrix(self):
        return self.get_local_projection_matrix().transpose()

    def get_global_vertex(self, vertex: Vertex):
        pm = self.get_global_projection_matrix()
        c = self._position.xyz + pm.dot(vertex.xyz)
        return Vertex(c[0], c[1], c[2])

    def get_global_xyz_array(self, xyz):
        pm = self.get_global_projection_matrix()
        c = self._position.xyz + pm.dot(np.array(xyz))
        return c

    def get_global_xyz(self, x, y, z):
        pm = self.get_global_projection_matrix()
        c = self._position.xyz + pm.dot(np.array([x, y, z]))
        return c

    def get_z_rotated_plane(self, rz):
        new_x = self.get_global_xyz(cos(rz), sin(rz), 0)
        new_x = new_x/np.linalg.norm(new_x)
        cp = np.cross(new_x, -self.normal.xyz)
        new_y = cp / np.linalg.norm(cp)
        new_plane = Plane(Vertex.from_xyz(new_x), Vertex.from_xyz(new_y), self._position)
        return new_plane

    def get_local_vertex(self, global_vertex):
        pm = self.get_local_projection_matrix()
        c = pm.dot(global_vertex.xyz-self._position.xyz)
        return Vertex(c[0], c[1], c[2])

    def get_local_xyz(self, x, y, z):
        pm = self.get_local_projection_matrix()
        c = pm.dot(np.array([x, y, z])-self._position.xyz)
        return c

    def get_local_xyz_array(self, xyz):
        pm = self.get_local_projection_matrix()
        c = pm.dot(xyz-self._position.xyz)
        return c

    def distance_vertex(self, global_vertex):
        return abs(self.get_local_vertex(global_vertex).z)

    def distance_xyz(self, x, y, z):
        return abs(self.get_local_xyz(x, y, z)[2])

    def distance_xyz_array(self, xyz):
        return abs(self.get_local_xyz(xyz)[2])

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'no': NamedObservableObject.serialize_json(self),
            'x_axis': self._x_axis,
            'y_axis': self._y_axis,
            'position': self._position
        }

    @staticmethod
    def deserialize(data):
        plane = Plane()
        if data is not None:
            plane.deserialize_data(data)
        return plane

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        NamedObservableObject.deserialize_data(self, data.get('no', None))
        self._x_axis = Vertex.deserialize(data['x_axis'])
        self._y_axis = Vertex.deserialize(data['y_axis'])
        self._position = Vertex.deserialize(data['position'])

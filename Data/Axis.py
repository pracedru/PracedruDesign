from math import atan2, pi, sin, cos, sqrt

import numpy as np

from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Objects import IdObject, NamedObservableObject
from Data.Vertex import Vertex


class Axis(NamedObservableObject, IdObject):
    def __init__(self, document, name="New Axis"):
        NamedObservableObject.__init__(self, name)
        IdObject.__init__(self)
        self._doc = document
        self._sketch = None
        self._edge = None

        self._origo = Vertex()
        self._direction = Vertex(1, 1, 1)

    @property
    def direction(self):
        return self._direction

    @property
    def origo(self):
        return self._origo

    def on_edge_changed(self, event):
        old_value = self._origo
        kps = self._edge.get_end_key_points()
        self._origo.x = kps[0].x
        self._origo.y = kps[0].y
        self._origo.z = kps[0].z
        self._direction.xyz = kps[1].xyz - kps[0].xyz
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        self.changed(ValueChangeEvent(self, 'origo', old_value, self._origo))
        if event.type == ChangeEvent.Deleted:
            event.sender.remove_change_handler(self.on_edge_changed)
            self._sketch = None

    def set_edge_governor(self, edge, sketch):
        if self._edge is not None:
            self._edge.remove_change_handler(self.on_edge_changed)
        self._edge = edge
        self._sketch = sketch
        kps = self._edge.get_end_key_points()
        self._origo.x = kps[0].x
        self._origo.y = kps[0].y
        self._origo.z = kps[0].z
        self._direction.xyz = kps[1].xyz - kps[0].xyz
        self._edge.add_change_handler(self.on_edge_changed)

    def get_projection_matrix(self):
        if self._direction.z == 0:
            angle = atan2(self._direction.y, self._direction.x) + pi / 2
        elif self._direction.x == 0:
            angle = atan2(self._direction.y, self._direction.z) + pi / 2
        else:
            angle = atan2(self._direction.x, self._direction.z) + pi / 2
        d2 = np.array([cos(angle), sin(angle), self._direction.z])
        cp = np.cross(self._direction.xyz, d2)
        d2 = cp / np.linalg.norm(cp)
        cp = np.cross(self._direction.xyz, d2)
        d3 = cp / np.linalg.norm(cp)
        d1 = self._direction.xyz / np.linalg.norm(self._direction.xyz)
        pm = np.array([d1, d2, d3])
        return pm

    def distance(self, point):
        p1 = self._origo.xyz
        pm = self.get_projection_matrix()
        newp = pm.dot(point.xyz-p1)
        newp[0] = 0.0
        distance = np.linalg.norm(newp)
        return distance

    def distance_xyz(self, point):
        p1 = self._origo.xyz
        pm = self.get_projection_matrix()
        newp = pm.dot(point-p1)
        newp[0] = 0.0
        distance = np.linalg.norm(newp)
        return distance

    def project_point(self, point):
        pm = self.get_projection_matrix()
        newp = pm.dot(point.xyz - self._origo.xyz)
        return newp[0]*pm[0]+self._origo.xyz

    def project_point_xyz(self, point):
        pm = self.get_projection_matrix()
        newp = pm.dot(point - self._origo.xyz)
        return newp[0]*pm[0]+self._origo.xyz

    @property
    def _sketch_uid(self):
        if self._sketch is None:
            return None
        else:
            return self._sketch.uid

    @property
    def _edge_uid(self):
        if self._edge is None:
            return None
        else:
            return self._edge.uid

    def serialize_json(self):
        return {
            'no': NamedObservableObject.serialize_json(self),
            'uid': IdObject.serialize_json(self),
            'sketch_uid': self._sketch_uid,
            'edge_uid': self._edge_uid,
            'origo': self._origo,
            'direction': self._direction
        }

    @staticmethod
    def deserialize(data, document):
        axis = Axis(document)
        if data is not None:
            axis.deserialize_data(data)
        return axis

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data.get('uid', {'uid': self.uid}))
        NamedObservableObject.deserialize_data(self, data['no'])
        sketch_uid = data['sketch_uid']
        if sketch_uid is not None:
            self._sketch = self._doc.get_geometries().get_geometry(sketch_uid)
        edge_uid = data['edge_uid']
        if self._sketch is not None and edge_uid is not None:
            self._edge = self._sketch.get_edge(edge_uid)
            self._edge.add_change_handler(self.on_edge_changed)
        self._origo = Vertex.deserialize(data['origo'])
        self._direction = Vertex.deserialize(data['direction'])
        if self._edge is not None:
            self.on_edge_changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self._edge))
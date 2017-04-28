from math import sqrt, atan2, pi
import numpy as np

__author__ = 'mamj'


class Vertex(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.xyz = np.array([float(x), float(y), float(z)])

    def distance(self, other):
        return np.linalg.norm(self.xyz - other.xyz)

    def angle2d(self, other):
        diff = other.xyz - self.xyz
        return atan2(diff[1], diff[0])

    def angle3d(self, other):
        diff = other.xyz - self.xyz
        return atan2(diff[0], diff[1]), atan2(diff[0], diff[2])

    @property
    def x(self):
        return self.xyz[0]

    @property
    def y(self):
        return self.xyz[1]

    @property
    def z(self):
        return self.xyz[2]

    @x.setter
    def x(self, x):
        self.xyz[0] = x

    @y.setter
    def y(self, y):
        self.xyz[1] = y

    @z.setter
    def z(self, z):
        self.xyz[2] = z

    def serialize_json(self):
        return {'xyz': self.xyz.tolist()}

    @staticmethod
    def deserialize(data):
        vertex = Vertex()
        if data is not None:
            vertex.deserialize_data(data)
        return vertex

    def deserialize_data(self, data):
        self.xyz = np.array(data['xyz'])

    def angle_between_untouched(self, kp1, kp2):
        alpha1 = self.angle2d(kp1)
        alpha2 = self.angle2d(kp2)
        alpha = alpha2 - alpha1
        return alpha

    def angle_between(self, kp1, kp2):
        alpha1 = self.angle2d(kp1)
        alpha2 = self.angle2d(kp2)
        alpha = alpha2 - alpha1
        while alpha < 0:
            alpha += 2*pi
        while alpha > 2*pi:
            alpha -= 2*pi
        return alpha

    def angle_between_positive_minimized(self, kp1, kp2):
        angle = abs(self.angle_between(kp1, kp2))
        if angle > pi:
            angle = 2*pi-angle
        return angle

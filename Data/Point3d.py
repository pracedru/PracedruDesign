from Data import Parameters
from Data.Events import ChangeEvent
from Data.Vertex import Vertex
from Data.Objects import IdObject, ObservableObject

__author__ = 'mamj'


class Point3d(Vertex, IdObject):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        Vertex.__init__(self, x, y, z)
        IdObject.__init__(self)

    def serialize_json(self):
        return \
            {
                'v': Vertex.serialize_json(self),
                'uid': IdObject.serialize_json(self)
            }

    @staticmethod
    def deserialize(data):
        point = Point3d()
        point.deserialize_data(data)
        return point

    def deserialize_data(self, data):
        try:
            IdObject.deserialize_data(self, data['uid'])
        except TypeError as e:
            print("error: " + str(e))
        Vertex.deserialize_data(self, data['v'])


class KeyPoint(Point3d, ObservableObject):
    def __init__(self, parameters: Parameters, x=0.0, y=0.0, z=0.0):
        Point3d.__init__(self, x, y, z)
        ObservableObject.__init__(self)
        self._x_param_uid = None
        self._y_param_uid = None
        self._z_param_uid = None
        self._x_param = None
        self._y_param = None
        self._z_param = None
        self._parameters = parameters
        self._edges = []

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def get_edges(self):
        return list(self._edges)

    def add_edge(self, edge):
        if edge not in self._edges:
            self._edges.append(edge)
            edge.add_change_handler(self.edge_changed_handler)

    def edge_changed_handler(self, event):
        if event.type == ChangeEvent.Deleted:
            self.remove_edge(event.object)

    def remove_edge(self, edge):
        if edge in self._edges:
            edge.remove_change_handler(self.edge_changed_handler)
            self._edges.remove(edge)

    def get_x_parameter(self):
        return self._x_param

    def get_y_parameter(self):
        return self._y_param

    def get_z_parameter(self):
        return self._z_param

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
        if x != self.xyz[0]:
            new_value = x
            old_value = self.xyz[0]
            self.xyz[0] = x
            self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'new value': new_value, 'old value': old_value, 'name': 'x'}))

    @y.setter
    def y(self, y):
        if y != self.xyz[1]:
            new_value = y
            old_value = self.xyz[1]
            self.xyz[1] = y
            self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'new value': new_value, 'old value': old_value, 'name': 'y'}))

    @z.setter
    def z(self, z):
        if z != self.xyz[2]:
            new_value = z
            old_value = self.xyz[2]
            self.xyz[2] = z
            self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, {'new value': new_value, 'old value': old_value, 'name': 'z'}))

    def set_x_parameter(self, x_param_uid):
        if self._x_param is not None:
            self._x_param.remove_change_handler(self.on_x_param_changed)
            self._x_param = None
            self._x_param_uid = None
        self._x_param_uid = x_param_uid
        if self._x_param_uid is not None:
            self._x_param = self._parameters.get_parameter_by_uid(x_param_uid)
            if self._x_param is not None:
                self._x_param.add_change_handler(self.on_x_param_changed)
                self.on_x_param_changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))
            else:
                self._x_param_uid = None

    def on_x_param_changed(self, event):
        old_value = self.x
        self.x = float(self._x_param.evaluate())
        new_value = self.x
        if event.type == ChangeEvent.Deleted:
            event.object.remove_change_handler(self.on_x_param_changed)
            self._x_param_uid = None
            self._x_param = None
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))


    def set_y_parameter(self, y_param_uid):
        if self._y_param is not None:
            self._y_param.remove_change_handler(self.on_y_param_changed)
            self._y_param = None
            self._y_param_uid = None
        self._y_param_uid = y_param_uid
        if self._y_param_uid is not None:
            self._y_param = self._parameters.get_parameter_by_uid(y_param_uid)
            if self._y_param is not None:
                self._y_param.add_change_handler(self.on_y_param_changed)
                self.on_y_param_changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))
            else:
                self._y_param_uid = None

    def on_y_param_changed(self, event):
        old_value = self.y
        self.y = float(self._y_param.evaluate())
        new_value = self.y
        if event.type == ChangeEvent.Deleted:
            event.object.remove_change_handler(self.on_y_param_changed)
            self._y_param_uid = None
            self._y_param = None
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    def set_z_parameter(self, z_param_uid):
        if self._z_param is not None:
            self._z_param.remove_change_handler(self.on_z_param_changed)
            self._z_param = None
            self._z_param_uid = None
        self._z_param_uid = z_param_uid
        if self._z_param_uid is not None:
            self._z_param = self._parameters.get_parameter_by_uid(z_param_uid)
            if self._z_param is not None:
                self._z_param.add_change_handler(self.on_z_param_changed)
                self.on_z_param_changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))
            else:
                self._z_param_uid = None


    def on_z_param_changed(self, event):
        old_value = self.z
        self.z = float(self._z_param.evaluate())
        new_value = self.z
        if event.type == ChangeEvent.Deleted:
            event.object.remove_change_handler(self.on_z_param_changed)
            self._z_param_uid = None
            self._z_param = None
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    def serialize_json(self):
        return \
            {
                'p3d': Point3d.serialize_json(self),
                'x_param_uid': self._x_param_uid,
                'y_param_uid': self._y_param_uid,
                'z_param_uid': self._z_param_uid
            }

    @staticmethod
    def deserialize(data, parameters):
        key_point = KeyPoint(parameters)
        key_point.deserialize_data(data)
        return key_point

    def deserialize_data(self, data):
        Point3d.deserialize_data(self, data.get('p3d'))
        self.set_x_parameter(data['x_param_uid'])
        self.set_y_parameter(data['y_param_uid'])
        self.set_z_parameter(data['z_param_uid'])




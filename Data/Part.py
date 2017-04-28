from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Objects import IdObject, NamedObservableObject
from Data.Parameters import Parameters
from Data.Vertex import Vertex


class Part(Geometry):
    def __init__(self, parameters_parent, document, name="New part"):
        Geometry.__init__(self, parameters_parent, name, Geometry.Part)
        self._doc = document
        self._plane_features = {}
        self._sketch_features = {}
        self._extrude_features = {}

    def create_plane_feature(self, name, position, x_direction, y_direction):
        plane = Feature(self._doc, PlaneFeature, name)
        plane.add_vertex('p', position)
        plane.add_vertex('xd', x_direction)
        plane.add_vertex('yd', y_direction)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, plane))
        self._plane_features[plane.uid] = plane
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, plane))
        return plane

    def create_sketch_feature(self, name, sketch, plane_feature):
        sketch_feature = Feature(self._doc, SketchFeature, sketch.name)
        sketch_feature.add_feature(plane_feature)


    def create_extrude_feature(self, name, sketch_feature, area):
        pass

    def get_feature(self, uid):
        if uid in self._plane_features:
            return self._plane_features[uid]
        if uid in self._sketch_features:
            return self._sketch_features[uid]
        if uid in self._extrude_features:
            return self._extrude_features[uid]
        return None

    def get_planes(self):
        planes = []
        for feature in self._plane_features.items():
            planes.append(feature[1])
        return planes

    @property
    def get_features(self):
        features = []
        for feature_tuple in self._plane_features.items():
            features.append(feature_tuple[1])
        return features

    def on_plane_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._plane_features.pop(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_plane_feature_changed)

    def on_sketch_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._sketch_features.pop(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_sketch_feature_changed)

    def on_extrude_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._extrude_features.pop(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_extrude_feature_changed)

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'parameters': Parameters.serialize_json(self),
            'plane_features': self._plane_features,
            'sketch_features': self._sketch_features,
            'extrude_features': self._extrude_features,
            'type': self._geometry_type
        }

    @staticmethod
    def deserialize(data, param_parent, document):
        part = Part(param_parent, document)
        if data is not None:
            part.deserialize_data(data)
        return part

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        Parameters.deserialize_data(self, data['parameters'])
        for feature_data_tuple in data.get('plane_features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._plane_features[feature.uid] = feature
            feature.add_change_handler(self.on_plane_feature_changed)
        for feature_data_tuple in data.get('sketch_features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._sketch_features[feature.uid] = feature
            feature.add_change_handler(self.on_sketch_feature_changed)
        for feature_data_tuple in data.get('extrude_features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._extrude_features[feature.uid] = feature
            feature.add_change_handler(self.on_extrude_feature_changed)


ExtrudeFeature = 0
RevolveFeature = 1
FilletFeature = 2
PlaneFeature = 3
SketchFeature = 4


class Feature(NamedObservableObject, IdObject):
    def __init__(self, document, feature_type=ExtrudeFeature, name="new feature"):
        IdObject.__init__(self)
        NamedObservableObject.__init__(self, name)
        self._doc = document
        self._feature_type = feature_type
        self._vertexes = {}
        self._edges = []
        self._features = []

    def add_vertex(self, key, vertex):
        self._vertexes[key] = vertex

    def get_vertex(self, key):
        if key in self._vertexes:
            return self._vertexes[key]
        return None

    @property
    def feature_type(self):
        return self._feature_type

    def on_edge_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def on_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, event))

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'name': NamedObservableObject.serialize_json(self),
            'edges': self._edges,
            'vertexes': self._vertexes,
            'type': self._feature_type,
            'features': self._features
        }

    @staticmethod
    def deserialize(data, feature_parent, document):
        feature = Feature(document)
        if data is not None:
            feature.deserialize_data(data, feature_parent)
        return feature

    def deserialize_data(self, data, feature_parent):
        IdObject.deserialize_data(self, data['uid'])
        NamedObservableObject.deserialize_data(self, data['name'])
        self._feature_type = data['type']
        for vertex_data_tuple in data.get('vertexes', {}).items():
            vertex_data = vertex_data_tuple[1]
            vertex = Vertex.deserialize(vertex_data)
            self._vertexes[vertex_data_tuple[0]] = vertex

        for edges_uid in data.get('edges', []):
            edge = self._doc.get_geometries.get_edge(edges_uid)
            self._edges.append(edge)
            edge.add_change_handler(self.on_edge_changed)

        for feature_uid in data.get('features', []):
            feature = feature_parent.get_feature(feature_uid)
            self._features.append(feature)
            feature.add_change_handler(self.on_feature_changed)

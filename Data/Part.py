from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Objects import IdObject, NamedObservableObject
from Data.Parameters import Parameters


class Part(Geometry):
    def __init__(self, parameters_parent, document, name="New part"):
        Geometry.__init__(self, parameters_parent, name, Geometry.Part)
        self._doc = document
        self._features = []

    @property
    def get_features(self):
        return self._features

    def on_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._features.remove(event.sender)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_feature_changed)

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'parameters': Parameters.serialize_json(self),
            'features': self._features,
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
        for feature_data in data.get('features', []):
            feature = Feature.deserialize(feature_data, self)
            self._features.append(feature)
            feature.add_change_handler(self.on_feature_changed)

ExtrudeFeature = 0
RevolveFeature = 1
FilletFeature = 2


class Feature(NamedObservableObject):
    def __init__(self, document, feature_type=ExtrudeFeature, name="new feature"):
        NamedObservableObject.__init__(self, name)
        self._doc = document
        self._feature_type = feature_type
        self._edges = []

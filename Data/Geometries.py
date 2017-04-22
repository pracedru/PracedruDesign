from Data.Objects import ObservableObject


class Geometries(ObservableObject):
    def __init__(self, document):
        ObservableObject.__init__(self)
        self._doc = document
        self._geometries = {}

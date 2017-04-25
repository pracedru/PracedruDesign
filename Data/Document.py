from Data.Components import Components
from Data.Drawings import Drawings
from Data.Geometries import Geometries
from Data.Events import ChangeEvent
from Data.Margins import Margins
from Data.Materials import Materials
from Data.Mesh import Mesh
from Data.Objects import ObservableObject, IdObject
from Data.Parameters import Parameters
from Data.Style import Styles

from Data.Sweeps import Sweeps

__author__ = 'mamj'


class Document(IdObject, ObservableObject):
    def __init__(self):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._parameters = Parameters("Global Parameters")
        self._styles = Styles()
        self._geometries = Geometries(self)
        self._margins = Margins(self)
        self._materials = Materials(self)
        self._components = Components(self)
        self._mesh = Mesh(self)
        self._sweeps = Sweeps(self)
        self._drawings = Drawings(self)
        self.path = ""
        self.name = "New document.jadoc"
        self.do_update = True
        self.status_handler = None
        self.init_change_handlers()

    def init_change_handlers(self):
        self._parameters.add_change_handler(self.on_parameters_changed)
        self._styles.add_change_handler(self.on_object_changed)
        self._geometries.add_change_handler(self.on_geometries_changed)
        self._materials.add_change_handler(self.on_materials_changed)
        self._components.add_change_handler(self.on_components_changed)
        self._margins.add_change_handler(self.on_margins_changed)
        self._mesh.add_change_handler(self.on_object_changed)
        self._sweeps.add_change_handler(self.on_object_changed)
        self._drawings.add_change_handler(self.on_object_changed)

    def get_styles(self):
        return self._styles

    def get_materials_object(self):
        return self._materials

    def get_geometries(self):
        return self._geometries

    def get_materials(self):
        return self._materials

    def get_parameters(self):
        return self._parameters

    def get_components(self):
        return self._components

    def get_margins(self):
        return self._margins

    def get_mesh(self):
        return self._mesh

    def get_sweeps(self):
        return self._sweeps

    def get_drawings(self):
        return self._drawings

    def on_parameters_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def on_geometries_changed(self, event: ChangeEvent):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def on_areas_changed(self, event):
        self.changed(event)

    def on_materials_changed(self, event):
        self.changed(event)

    def on_components_changed(self, event):
        self.changed(event)

    def on_margins_changed(self, event):
        self.changed(event)

    def on_object_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def set_status(self, message, progess=100):
        if self.status_handler is not None:
            self.status_handler(message, progess)

    def add_status_handler(self, status_handler):
        self.status_handler = status_handler

    def serialize_json(self):
        return \
            {
                'uid': IdObject.serialize_json(self),
                'styles': self._styles,
                'params': self._parameters,
                'geoms': self._geometries,
                'name': self.name,
                'materials': self._materials,
                'components': self._components,
                'margins': self._margins,
                'mesh': self._mesh,
                'sweeps': self._sweeps,
                'drawings': self._drawings,
                'path': self.path
            }

    @staticmethod
    def deserialize(data):
        doc = Document()
        doc.deserialize_data(data)
        return doc

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        self._parameters = Parameters.deserialize(data.get('params', None), None)
        self._styles = Styles.deserialize(data.get('styles', None))
        self._geometries = Geometries.deserialize(data.get('geoms', None), self)
        self._materials = Materials.deserialize(data.get('materials'), self)
        self._components = Components.deserialize(data.get('components'), self)
        self._margins = Margins.deserialize(data.get('margins'), self)
        self._mesh = Mesh.deserialize(data.get('mesh'), self)
        self._sweeps = Sweeps.deserialize(data.get('sweeps'), self)
        self._drawings = Drawings.deserialize(data.get('drawings', None), self)
        self.name = data.get('name', "missing")
        self.path = data.get('path', "missing")
        self.init_change_handlers()


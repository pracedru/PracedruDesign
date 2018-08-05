from Data.Analyses import Analyses
from Data.Axis import Axis
from Data.Collections import ObservableList
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


class Document(IdObject, Parameters):
	def __init__(self):
		IdObject.__init__(self)
		Parameters.__init__(self, "Global Parameters")
		# self._parameters = Parameters("Global Parameters")
		self._styles = Styles()
		self._geometries = Geometries(self)
		self._axes = {}
		self._margins = Margins(self)
		self._materials = Materials(self)
		self._components = Components(self)
		self._mesh = Mesh(self)
		self._sweeps = Sweeps(self)
		self._drawings = Drawings(self)
		self._analyses = Analyses(self)
		self._undo_stack = ObservableList()
		self._redo_stack = ObservableList()
		self.path = ""
		self.name = "New document.jadoc"
		self.do_update = True
		self.status_handler = None
		self.init_change_handlers()
		self._persistent_status_message = ""
		self._persistent_status_progress = 100

	def init_change_handlers(self):
		# self.add_change_handler(self.on_parameters_changed)
		self._styles.add_change_handler(self.on_object_changed)
		self._geometries.add_change_handler(self.on_geometries_changed)
		self._materials.add_change_handler(self.on_materials_changed)
		self._components.add_change_handler(self.on_components_changed)
		self._margins.add_change_handler(self.on_margins_changed)
		self._mesh.add_change_handler(self.on_object_changed)
		self._sweeps.add_change_handler(self.on_object_changed)
		self._drawings.add_change_handler(self.on_object_changed)
		self._undo_stack.add_change_handler(self._on_undo_stack_changed)
		self._redo_stack.add_change_handler(self._on_redo_stack_changed)

	@property
	def undo_stack(self):
		return self._undo_stack

	@property
	def redo_stack(self):
		return self._redo_stack

	def get_axes(self):
		return self._axes

	def get_styles(self):
		return self._styles

	def get_materials_object(self):
		return self._materials

	def get_geometries(self):
		return self._geometries

	def get_analyses(self):
		return self._analyses

	def get_materials(self):
		return self._materials

	def get_parameters(self):
		return self

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

	def get_sketches(self):
		return self._geometries.get_sketches()

	def get_sketch_by_name(self, name):
		return self._geometries.get_sketch_by_name(name)

	def get_sketch(self, uid):
		return self._geometries.get_geometry(uid)

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

	def set_status(self, message, progress=100, persistent=False):
		if persistent:
			self._persistent_status_message = message
			self._persistent_status_progress = progress
		if message == "":
			message = self._persistent_status_message
			progress = self._persistent_status_progress
		if self.status_handler is not None:
			self.status_handler(message, progress)

	def add_status_handler(self, status_handler):
		self.status_handler = status_handler

	def _on_undo_stack_changed(self, event):
		if event.type == ChangeEvent.ObjectAdded:
			self._redo_stack.clear()
		if event.type == ChangeEvent.ObjectRemoved:
			self._redo_stack.append(event.object)

	def _on_redo_stack_changed(self, event):
		if event.type == ChangeEvent.ObjectRemoved:
			self._undo_stack.sneak_append(event.object)
			self._undo_stack.changed(ChangeEvent(self, ChangeEvent.ValueChanged, None))

	def add_sketch(self, sketch):
		self._geometries.add_geometry(sketch)

	def serialize_json(self):
		return \
			{
				'uid': IdObject.serialize_json(self),
				'styles': self._styles,
				'params': Parameters.serialize_json(self),
				'geoms': self._geometries,
				'axes': self._axes,
				'name': self.name,
				'materials': self._materials,
				'components': self._components,
				'margins': self._margins,
				'mesh': self._mesh,
				'sweeps': self._sweeps,
				'drawings': self._drawings,
				'analysees': self._analyses,
				'path': self.path
			}

	@staticmethod
	def deserialize(data):
		doc = Document()
		doc.deserialize_data(data)
		return doc

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		Parameters.deserialize_data(self, data.get('params', None))

		self._styles = Styles.deserialize(data.get('styles', None))
		self._geometries = Geometries.deserialize(data.get('geoms', None), self)
		for axis_tuple in data.get('axes', {}).items():
			axis = Axis.deserialize(axis_tuple[1], self)
			self._axes[axis.uid] = axis
		self._materials = Materials.deserialize(data.get('materials'), self)
		self._components = Components.deserialize(data.get('components'), self)
		self._margins = Margins.deserialize(data.get('margins'), self)
		self._mesh = Mesh.deserialize(data.get('mesh'), self)
		self._sweeps = Sweeps.deserialize(data.get('sweeps'), self)
		self._drawings = Drawings.deserialize(data.get('drawings', None), self)
		self._analyses = Analyses.deserialize(data.get('analysees', None), self)
		self.name = data.get('name', "missing")
		self.path = data.get('path', "missing")
		self.init_change_handlers()

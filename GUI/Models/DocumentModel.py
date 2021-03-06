from PyQt5.QtCore import QAbstractItemModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt

from Business.Undo import change_name
from Data.Analysis import Analysis
from Data.Areas import Area
from Data.CalcSheetAnalysis import CalcSheetAnalysis
from Data.CalcTableAnalysis import CalcTableAnalysis
from Data.Document import Document
from Data.Drawings import Drawing, Drawings, Field, SketchView, PartView
from Data.Events import ChangeEvent
from Data.Feature import *
from Data.Geometry import Geometry
from Data.Parameters import Parameters, Parameter
from Data.Part import Part, Feature
from Data.Point3d import KeyPoint
from Data.Proformer import Proformer, ProformerType
from Data.Sketch import Sketch, Edge, Text, Attribute, SketchInstance
from Data.Style import EdgeStyle, Brush
from GUI.init import tr
from GUI.Icons import get_icon


class DocumentItemModel(QAbstractItemModel):
	def __init__(self, document: Document):
		QAbstractItemModel.__init__(self)
		self._new_item_added_listeners = []
		self._doc = document
		self._root_item = DocumentModelItem(document, self)
		self.populate()
		if document is not None:
			document.add_change_handler(self.on_document_changed)

	def add_new_item_added_listener(self, listener):
		self._new_item_added_listeners.append(listener)

	def on_new_item_added(self, item):
		row = item.parent().children().index(item)
		index = self.createIndex(row, 0, item)
		for listener in self._new_item_added_listeners:
			listener(index)

	def populate(self):
		glocal_params_item = DocumentModelItem(self._doc.get_parameters(), self, self._root_item, "Parameters")
		styles_item = DocumentModelItem(self._doc.styles, self, self._root_item, "Styles")
		pens_item = DocumentModelItem(None, self, styles_item, "Pens")
		brushes_item = DocumentModelItem(None, self, styles_item, "Brushes")
		for style in self._doc.styles.get_edge_styles():
			DocumentModelItem(style, self, pens_item)
		for style in self._doc.styles.get_brushes():
			DocumentModelItem(style, self, brushes_item)
		for param in self._doc.get_parameters().get_all_parameters():
			DocumentModelItem(param, self, glocal_params_item)
		geoms_item = DocumentModelItem(self._doc.get_geometries(), self, self._root_item)
		for geom in self._doc.get_geometries().items():
			if type(geom) is Sketch:
				self.populate_sketch(geom, geoms_item)
			if type(geom) is Part:
				self.populate_part(geom, geoms_item)
			# DocumentModelItem(geom, self, geoms_item)
		analyses_item = DocumentModelItem(self._doc.get_analyses(), self, self._root_item)
		for analysis_tuple in self._doc.get_analyses().items():
			self.populate_analysis(analysis_tuple[1], analyses_item)
		self.populate_drawings()
		DocumentModelItem(None, self, self._root_item, "Reports")

	def populate_sketch(self, sketch, parent_item):
		geom_item = self.create_model_item(parent_item, sketch)
		for param_tuple in sketch.get_all_local_parameters():
			param_item = DocumentModelItem(param_tuple[1], self, geom_item.children()[0])
		for kp in sketch.get_keypoints():
			kp_item = DocumentModelItem(kp, self, geom_item.children()[1], "Key point")
		for edge in sketch.get_edges():
			edge_item = DocumentModelItem(edge, self, geom_item.children()[2])
		for text in sketch.get_texts():
			text_item = DocumentModelItem(text, self, geom_item.children()[3])
		for area in sketch.get_areas():
			area_item = DocumentModelItem(area, self, geom_item.children()[4])
		for sketch_instance in sketch.sketch_instances:
			parent_item = geom_item.get_child_by_name("Sketch instances")
			sketch_instance_item = DocumentModelItem(sketch_instance, self, parent_item)
		for proformer in sketch.proformers:
			parent_item = geom_item.get_child_by_name("Proformers")
			proformer_item = DocumentModelItem(proformer, self, parent_item)
		return geom_item

	def populate_drawing(self, drawing, parent_item):
		drawing_item = self.create_model_item(parent_item, drawing)
		for field_tuple in drawing.get_fields().items():
			field_item = DocumentModelItem(field_tuple[1], self, drawing_item.children()[0])
		for view in drawing.get_views():
			view_item = DocumentModelItem(view, self, drawing_item)
		return drawing_item

	def populate_part(self, part, parent_item):
		geom_item = self.create_model_item(parent_item, part)
		for feature_key in part.get_feature_progression():
			feature = part.get_feature(feature_key)
			self.create_model_item(geom_item, feature)
		return geom_item

	def populate_drawings(self):
		drawings = self._doc.get_drawings()
		# drawings_item = self.create_model_item(self._root_item, drawings)
		drawings_item = DocumentModelItem(drawings, self, self._root_item)
		DocumentModelItem(None, self, drawings_item, "Headers")
		for header in drawings.get_headers():
			self.populate_sketch(header, drawings_item)
		for dwg in self._doc.get_drawings().items:
			self.populate_drawing(dwg, drawings_item)

	def populate_analysis(self, analysis, analyses_item):
		analysis_item = self.create_model_item(analyses_item, analysis)
		return analysis_item

	def parent(self, index: QModelIndex = None):
		if not index.isValid():
			return QModelIndex()
		model_item = index.internalPointer()
		try:
			if model_item is None:
				return QModelIndex()
			elif model_item == self._root_item:
				return QModelIndex()
			else:
				parent_item = model_item.parent()
				if parent_item is not None:
					elder_item = parent_item.parent()
					if elder_item is not None:
						row = elder_item.children().index(parent_item)
					else:
						row = 0
					return self.createIndex(row, 0, parent_item)
		except Exception as e:
			col = index.column()
			row = index.row()
			print("DocumentModel::parent")
			print(str(e))
			print("Col: " + str(col) + " Row: " + str(row))
		return QModelIndex()

	def index(self, row, col, parent: QModelIndex = None, *args, **kwargs):
		if parent is None:
			return self.createIndex(row, col, self._root_item)
		if parent.internalPointer() is None:
			return self.createIndex(row, col, self._root_item)
		else:
			parent_model_item = parent.internalPointer()
			model_item = parent_model_item.children()[row]
			data = model_item.parent()
			return self.createIndex(row, 0, model_item)

	def columnCount(self, parent=None, *args, **kwargs):
		return 1

	def rowCount(self, parent=None, *args, **kwargs):
		if parent is None:
			return 1
		if parent.internalPointer() is None:
			print("HESJA")
			return 0
		else:
			return len(parent.internalPointer().children())

	def data(self, index: QModelIndex, role=None):
		col = index.column()
		row = index.row()
		data = None
		model_item = index.internalPointer()
		if role == Qt.DisplayRole or role == Qt.EditRole:
			return model_item.name
		elif role == Qt.DecorationRole:
			return model_item.icon
		return None

	def setData(self, index: QModelIndex, value, role=None):
		model_item = index.internalPointer()
		if role == Qt.EditRole:
			change_name(self._doc, model_item.data, str(value))
			# model_item.data.name = str(value)
			return True
		return False

	def headerData(self, p_int, qt_orientation, role=None):
		if role == Qt.DisplayRole:
			if qt_orientation == Qt.Vertical:
				return p_int
			else:
				return "Name"

	def flags(self, index: QModelIndex):
		col = index.column()
		row = index.row()
		model_item = index.internalPointer()
		default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
		try:
			if isinstance(model_item.data, Geometry):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, Parameter):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, Drawing):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, Feature):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, Analysis):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, Area):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, Edge):
				default_flags = default_flags | Qt.ItemIsEditable
			if isinstance(model_item.data, KeyPoint):
				default_flags = default_flags | Qt.ItemIsEditable
		except RuntimeError as e:
			print("DocumentModel::flags")
			print(str(e))
			print("Col: " + str(col) + " Row: " + str(row))
		return default_flags

	def on_object_deleted(self, item):
		self.remove_item(item)

	def remove_item(self, item):
		parent = item.parent()
		if parent:
			if parent.parent():
				parent_row = parent.parent().children().index(parent)
			else:
				parent_row = 0
			index = parent.children().index(item)
			if index != -1:
				parent_model_index = self.createIndex(parent_row, 0, parent)
				self.beginRemoveRows(parent_model_index, index, index)
				item.setParent(None)
				self.endRemoveRows()

	def on_object_changed(self, item):
		self.layoutAboutToBeChanged.emit()
		self.layoutChanged.emit()

	def on_document_changed(self, event):
		self.layoutAboutToBeChanged.emit()
		self.layoutChanged.emit()

	def on_before_object_removed(self, parent_item, event):
		pass

	def on_object_removed(self, parent_item, item):
		self.remove_item(item)

	def on_before_object_added(self, parent_item, object):
		self.layoutAboutToBeChanged.emit()

	def on_object_added(self, parent_item, object):
		item = self.create_model_item(parent_item, object)
		if item is not None:
			self.on_new_item_added(item)
		self.layoutChanged.emit()

	def create_model_item(self, parent_item, object):
		new_item = None
		if parent_item == self._root_item:
			# print("root item is parent")
			return
		if type(parent_item.data) is Sketch:
			if type(object) is Parameter:
				parameters_item = parent_item.children()[0]
				new_item = DocumentModelItem(object, self, parameters_item)
			elif type(object) is KeyPoint:
				kps_item = parent_item.children()[1]
				new_item = DocumentModelItem(object, self, kps_item)
			elif type(object) is Edge:
				edges_item = parent_item.children()[2]
				new_item = DocumentModelItem(object, self, edges_item)
			elif isinstance(object, Text):
				annos_item = parent_item.children()[3]
				new_item = DocumentModelItem(object, self, annos_item)
			elif issubclass(type(object), Area):
				areas_item = parent_item.get_child_by_name("Areas")
				new_item = DocumentModelItem(object, self, areas_item)
			elif type(object) is Proformer:
				proformers_item = parent_item.get_child_by_name("Proformers")
				proformer_item = DocumentModelItem(object, self, proformers_item)
			elif type(object) is SketchInstance:
				instances_item = parent_item.get_child_by_name("Sketch instances")
				sketch_instance_item = DocumentModelItem(object, self, instances_item)
			else:
				new_item = DocumentModelItem(object, self, parent_item)
		elif type(parent_item.data) is Drawings and type(object) is Sketch:
			headers_item = parent_item.children()[0]
			new_item = self.create_model_item(headers_item, object)
		elif type(parent_item.data) is Drawing and type(object) is Field:
			fields_item = parent_item.children()[0]
			new_item = DocumentModelItem(object, self, fields_item)
		elif type(parent_item.data) is Part and type(object) is Feature:
			if type(object) is Feature:
				if object.feature_type == FeatureType.PlaneFeature:
					planes_item = parent_item.children()[0]
					new_item = DocumentModelItem(object, self, planes_item)
				elif object.feature_type == FeatureType.SketchFeature:
					sketch = object.get_sketches()[0]
					new_item = self.populate_sketch(sketch, parent_item)
				else:
					new_item = DocumentModelItem(object, self, parent_item)
		elif type(object) is EdgeStyle:
			pens_item = parent_item.get_child_by_name('Pens')
			new_item = DocumentModelItem(object, self, pens_item)
		elif type(object) is Brush:
			pens_item = parent_item.get_child_by_name('Brushes')
			new_item = DocumentModelItem(object, self, pens_item)
		else:
			new_item = DocumentModelItem(object, self, parent_item)
			if type(object) is Sketch:
				DocumentModelItem(None, self, new_item, "Parameters", icon=get_icon("params"))
				DocumentModelItem(None, self, new_item, "Key Points")
				DocumentModelItem(None, self, new_item, "Edges")
				DocumentModelItem(None, self, new_item, "Annotation")
				DocumentModelItem(None, self, new_item, "Areas")
				DocumentModelItem(None, self, new_item, "Proformers")
				DocumentModelItem(None, self, new_item, "Transformers")
				DocumentModelItem(None, self, new_item, "Sketch instances")

			if type(object) is Drawing:
				DocumentModelItem(None, self, new_item, "Fields")
				self.populate_sketch(object.header_sketch, new_item)
			if type(object) is Part:
				DocumentModelItem(None, self, new_item, "Planes")

		return new_item



class DocumentModelItem(QObject):
	def __init__(self, data, model, parent=None, name=None, icon=None):
		QObject.__init__(self, parent)
		self._data = data
		self._name = name
		if icon is None:
			self._icon = self.get_icon_based_on_type(data)
		else:
			self._icon = icon
		if name is not None:
			self._name = tr(name, 'model')
		self._model = model
		if data is not None:
			data.add_change_handler(self.data_changed)

	def __del__(self):
		# print("modelitem deleted")
		try:
			if self._data is not None:
				self._data.remove_change_handler(self.data_changed)
		except Exception as e:
			print(str(e))

	def get_child_by_name(self, name):
		name = tr(name, 'model')
		for child in self.children():
			if child.name == name:
				return child
		return None

	@property
	def name(self):
		if self._name is not None:
			return self._name
		if self._data is not None:
			if hasattr(self._data, "name"):
				return self._data.name
		return self._name

	@property
	def data(self):
		return self._data

	@property
	def icon(self):
		return self._icon

	def data_changed(self, event: ChangeEvent):
		if event.type == ChangeEvent.BeforeObjectAdded:
			self._model.on_before_object_added(self, event.object)
		elif event.type == ChangeEvent.ObjectAdded:
			self._model.on_object_added(self, event.object)
		elif event.type == ChangeEvent.BeforeObjectRemoved:
			self._model.on_before_object_removed(self, event)
		elif event.type == ChangeEvent.ObjectRemoved:
			event.object.remove_change_handler(self.data_changed)
			for child in self.children():
				if child.data == event.object:
					self._model.on_object_removed(self, child)
					return
				for child_child in child.children():
					if child_child.data == event.object:
						self._model.on_object_removed(self, child_child)
						return
		elif event.type == ChangeEvent.Deleted:
			self._data.remove_change_handler(self.data_changed)
			self._data = None
			self._model.on_object_deleted(self)
		elif event.type == ChangeEvent.ValueChanged:
			self._model.on_object_changed(self)

	@staticmethod
	def get_icon_based_on_type(obj):
		if type(obj) is Parameter:
			return get_icon("param")
		elif type(obj) is Sketch:
			return get_icon("sketch")
		elif type(obj) is SketchInstance:
			return get_icon("sketch")
		elif type(obj) is KeyPoint:
			return get_icon("kp")
		elif type(obj) is Edge:
			return get_icon("edge")
		elif type(obj) is Drawing:
			return get_icon("drawing")
		elif type(obj) is Text:
			return get_icon("text")
		elif type(obj) is EdgeStyle:
			return get_icon("edgestyle")
		elif type(obj) is Attribute:
			return get_icon("attribute")
		elif type(obj) is Field:
			return get_icon("field")
		elif type(obj) is SketchView:
			return get_icon("sketchview")
		elif type(obj) is PartView:
			return get_icon("partview")
		elif issubclass(type(obj), Area):
			return get_icon("area")
		elif type(obj) is Part:
			return get_icon("part")
		elif type(obj) is CalcTableAnalysis:
			return get_icon("calctable")
		elif type(obj) is CalcSheetAnalysis:
			return get_icon("calcsheet")
		elif type(obj) is Feature:
			if obj.feature_type == FeatureType.SketchFeature:
				return get_icon("sketch")
			if obj.feature_type == FeatureType.RevolveFeature:
				return get_icon("revolve")
			if obj.feature_type == FeatureType.ExtrudeFeature:
				return get_icon("extrude")
		elif issubclass(type(obj), Parameters):
			return get_icon("params")
		elif type(obj) is Brush:
			return get_icon("brush")
		elif type(obj) is Proformer:
			if ProformerType.Mirror.value <= obj.type.value <= ProformerType.MirrorXY.value:
				return get_icon("mirror")
		return get_icon("default")
from PyQt5.QtCore import *
from Business import *
from Business.SketchActions import remove_key_points
from Data.Parameters import *
from Data.Point3d import KeyPoint
from GUI.init import gui_scale

__author__ = 'mamj'

col_header = ["X coord", "Y coord"]


class KeyPointsModel(QAbstractTableModel):
	def __init__(self, doc):
		QAbstractItemModel.__init__(self)
		self._gui_scale = gui_scale()
		self._doc = doc
		self._sketch = None  # doc.get_edges()
		self._rows = []

	def set_sketch(self, sketch):
		self.layoutAboutToBeChanged.emit()
		if self._sketch is not None:
			self._sketch.remove_change_handler(self.on_sketch_changed)
			self._rows.clear()
		self._sketch = sketch
		for kp in self._sketch.get_keypoints():
			self._rows.append(kp.uid)
		self._sketch.add_change_handler(self.on_sketch_changed)
		self.layoutChanged.emit()

	def rowCount(self, model_index=None, *args, **kwargs):
		return len(self._rows)

	def columnCount(self, model_index=None, *args, **kwargs):
		return len(col_header)

	def data(self, model_index: QModelIndex, int_role=None):
		col = model_index.column()
		row = model_index.row()
		data = None
		if int_role == Qt.DisplayRole:
			kp_item = self._sketch.get_keypoint(self._rows[row])
			if col == 0:
				param = kp_item.get_x_parameter()
				if param is not None:
					data = param.name
				else:
					data = QLocale().toString(kp_item.x)
			if col == 1:
				param = kp_item.get_y_parameter()
				if param is not None:
					data = param.name
				else:
					data = QLocale().toString(kp_item.y)
		elif int_role == Qt.EditRole:
			kp_item = self._sketch.get_keypoint(self._rows[row])
			if col == 0:
				param = kp_item.get_x_parameter()
				if param is not None:
					data = param.name
				else:
					data = QLocale().toString(kp_item.x)
			if col == 1:
				param = kp_item.get_y_parameter()
				if param is not None:
					data = param.name
				else:
					data = QLocale().toString(kp_item.y)
				# data = str(kp_item.y)
		return data

	def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
		col = model_index.column()
		row = model_index.row()
		kp_item = self._sketch.get_keypoint(self._rows[row])
		parsed = QLocale().toDouble(value)
		parameter = None
		if parsed[1]:
			value = parsed[0]
		else:
			parameter = self._sketch.get_parameter_by_name(value)
		if not parsed[1] and parameter is None:
			if col == 0:
				parameter = self._sketch.create_parameter(value, kp_item.x)
			elif col == 1:
				parameter = self._sketch.create_parameter(value, kp_item.y)
		if col == 0:
			if parameter is not None:
				kp_item.set_x_parameter(parameter.uid)
			else:
				kp_item.set_x_parameter(None)
				kp_item.x = value

		if col == 1:
			if parameter is not None:
				kp_item.set_y_parameter(parameter.uid)
			else:
				kp_item.set_y_parameter(None)
				kp_item.y = value
		return False

	def removeRow(self, row, QModelIndex_parent=None, *args, **kwargs):
		kp = self._sketch.get_keypoint(self._rows[row])
		remove_key_points(self._doc, self._sketch, [kp])

	def remove_rows(self, rows):
		kps = []
		for row in rows:
			kps.append(self._sketch.get_keypoint(self._rows[row]))
		remove_key_points(self._sketch, kps)

	def on_sketch_changed(self, event: ChangeEvent):
		if type(event.object) is KeyPoint:
			if event.type == event.BeforeObjectAdded:
				self.beginInsertRows(QModelIndex(), len(self._rows) - 1, len(self._rows) - 1)
			if event.type == event.ObjectAdded:
				self._rows.append(event.object.uid)
				self.endInsertRows()
			if event.type == event.BeforeObjectRemoved:
				if event.object.uid in self._rows:
					row = self._rows.index(event.object.uid)
					self.beginRemoveRows(QModelIndex(), row, row)
			if event.type == event.ObjectRemoved:
				if event.object.uid in self._rows:
					self._rows.remove(event.object.uid)
					self.endRemoveRows()

			if event.type == event.Deleted:
				self._rows.remove(event.object.uid)
				self.layoutChanged.emit()
		if type(event.sender) is KeyPoint:
			if event.type == event.ValueChanged:
				if event.sender.uid in self._rows:
					row = self._rows.index(event.sender.uid)
					index1 = QModelIndex().child(row, 0)
					index2 = QModelIndex().child(row, 1)
					self.dataChanged.emit(index1, index2, [])
		if event.type == event.Cleared:
			self.beginRemoveRows(QModelIndex(), 0, len(self._rows) - 1)
			self._rows = []
			self.endRemoveRows()

	def flags(self, model_index: QModelIndex):
		default_flags = Qt.ItemIsSelectable
		row = model_index.row()
		kp_item = self._sketch.get_keypoint(self._rows[row])
		if kp_item:
			if kp_item.editable:
				default_flags |= Qt.ItemIsEditable | Qt.ItemIsEnabled
		return default_flags

	def headerData(self, p_int, orientation, int_role=None):
		if int_role == Qt.DisplayRole:
			if orientation == Qt.Vertical:
				return p_int
			else:
				return col_header[p_int]
		elif int_role == Qt.SizeHintRole:
			if orientation == Qt.Horizontal:
				return QSize(110 * self._gui_scale, 22 * self._gui_scale);
		else:
			return None

	def get_key_points_object(self):
		return self._sketch

	def get_key_point(self, row):
		return self._sketch.get_keypoint(self._rows[row])

	def get_index_from_key_point(self, kp):
		if kp.uid in self._rows:
			row = self._rows.index(kp.uid)
			return self.index(row, 0)
		return None

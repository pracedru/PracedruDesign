from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QRect
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAbstractItemDelegate, QApplication, QStyle, QWidget, QComboBox, QStyledItemDelegate, \
	QStyleOptionViewItem

__author__ = 'mamj'


class ComboboxDelegate(QStyledItemDelegate):
	def __init__(self, parent):
		QStyledItemDelegate.__init__(self, parent)

	def paint(self, painter: QPainter, item: QStyleOptionViewItem, index: QModelIndex):
		QStyledItemDelegate.paint(self, painter, item, index)

	def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
		options = index.model().data(index, Qt.EditRole)
		if not isinstance(options, list):
			return QStyledItemDelegate.createEditor(self, parent, option, index)
		editor = QComboBox(parent)
		editor.currentIndexChanged.connect(editor.close)
		# value = index.model().data(index, Qt.DisplayRole)
		model = index.model()
		# options = model.get_options(index)
		editor.addItems(options)
		return editor

	def setEditorData(self, editor, index: QModelIndex):
		if type(editor) is QComboBox:
			value = index.model().data(index, Qt.DisplayRole)
			model = index.model()
			options = model.data(index, Qt.EditRole)
			editor.setCurrentIndex(options.index(value))
		else:
			QStyledItemDelegate.setEditorData(self, editor, index)

	def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex):
		if type(editor) is QComboBox:
			value = editor.currentIndex()
			model.setData(index, value, Qt.EditRole)
		else:
			QStyledItemDelegate.setModelData(self, editor, model, index)

	def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, QModelIndex):
		editor.setGeometry(option.rect)

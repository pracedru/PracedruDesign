from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QRect
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAbstractItemDelegate, QApplication, QStyle, QWidget, QComboBox, QStyledItemDelegate, QStyleOptionViewItem

__author__ = 'mamj'


class ComboboxDelegate(QAbstractItemDelegate):
    def __init__(self, parent):
        QAbstractItemDelegate.__init__(self, parent)

    def paint(self, painter: QPainter, item: QStyleOptionViewItem, index: QModelIndex):
        QStyledItemDelegate().paint(painter, item, index)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        editor = QComboBox(parent)
        editor.currentIndexChanged.connect(editor.close)
        # value = index.model().data(index, Qt.DisplayRole)
        options = index.model().data(index, Qt.EditRole)
        model = index.model()
        # options = model.get_options(index)
        editor.addItems(options)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        value = index.model().data(index, Qt.DisplayRole)
        model = index.model()
        options = model.data(index, Qt.EditRole)
        editor.setCurrentIndex(options.index(value))

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel, index: QModelIndex):
        value = editor.currentIndex()
        model.setData(index, value)

    def updateEditorGeometry(self,editor: QWidget,option: QStyleOptionViewItem, QModelIndex):
        editor.setGeometry(option.rect)

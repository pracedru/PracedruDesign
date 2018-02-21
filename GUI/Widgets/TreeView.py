from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTreeView

from Business import delete_items
from Data.CalcTableAnalysis import CalcTableAnalysis
from Data.Document import Document
from Data.Drawings import Drawing
from Data.Geometry import Geometry
from Data.Part import Part
from Data.Sketch import Sketch
from GUI import tr
from GUI.Models.DocumentModel import DocumentItemModel


class TreeViewDock(QDockWidget):
    def __init__(self, main_window, document: Document):
        QDockWidget.__init__(self, main_window)
        self._main_window = main_window
        self.setWindowTitle(tr("Project view"))
        self.setObjectName("TreeViewDock")
        self._doc = document
        self._treeView = QTreeView(self)
        self.setWidget(self._treeView)
        self._model = DocumentItemModel(document)
        self._treeView.setModel(self._model)
        self._treeView.setRootIndex(self._model.index(0, 0))
        self._treeView.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)
        self._model.add_new_item_added_listener(self.on_new_item_added)
        self.installEventFilter(self)

    def on_delete(self):
        txt = tr("Are you sure you want to delete this item?", "messages")
        ret = QMessageBox.warning(self, tr("Delete item?"), txt, QMessageBox.Yes | QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            selection_model = self._treeView.selectionModel()
            indexes = selection_model.selectedIndexes()
            selected_items = set()
            for index in indexes:
                selected_items.add(index.internalPointer())
            delete_items(self._doc, selected_items)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self.on_delete()
                return True
        return False

    def on_tree_selection_changed(self, selection):
        selection_model = self._treeView.selectionModel()
        indexes = selection_model.selectedIndexes()
        selected_items = []
        for index in indexes:
            selected_items.append(index.internalPointer().data)
        self._main_window.on_tree_selection_changed(selected_items)

    def on_new_item_added(self, index):
        select = False
        if type(index.internalPointer().data) is Sketch:
            select = True
        if type(index.internalPointer().data) is Drawing:
            select = True
        if type(index.internalPointer().data) is Part:
            select = True
        if type(index.internalPointer().data) is CalcTableAnalysis:
            select = True
        if type(index.internalPointer().data) is Geometry:
            select = True
        if select:
            sel_type = QItemSelectionModel.ClearAndSelect
            parent_index = self._model.parent(index)
            while parent_index.isValid():
                self._treeView.setExpanded(parent_index, True)
                parent_index = self._model.parent(parent_index)
            self._treeView.scrollTo(index)
            self._treeView.selectionModel().select(index, sel_type)
            parent_index = self._model.parent(index)
            while parent_index.isValid():
                self._treeView.setExpanded(parent_index, True)
                parent_index = self._model.parent(parent_index)
        self._main_window.on_new_item_added_in_tree(index.internalPointer().data)

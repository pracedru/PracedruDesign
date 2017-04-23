from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QTreeView

from Data.Document import Document
from GUI.Models.DocumentModel import DocumentItemModel


class TreeViewDock(QDockWidget):
    def __init__(self, main_window, document: Document):
        QDockWidget.__init__(self, main_window)
        self._main_window = main_window
        self.setWindowTitle("Project view")
        self.setObjectName("TreeViewDock")
        self._doc = document
        self._treeView = QTreeView(self)
        self.setWidget(self._treeView)
        self._model = DocumentItemModel(document)
        self._treeView.setModel(self._model)
        self._treeView.setRootIndex(self._model.index(0, 0))

        self._treeView.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)

    def on_tree_selection_changed(self, selection):
        selection_model = self._treeView.selectionModel()
        indexes = selection_model.selectedIndexes()
        selected_items = []
        for index in indexes:
            selected_items.append(index.internalPointer().data)
        self._main_window.on_tree_selection_changed(selected_items)

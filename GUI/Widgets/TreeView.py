from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QTreeView

from Data.Document import Document
from GUI.Models.DocumentModel import DocumentItemModel


class TreeViewDock(QDockWidget):
    def __init__(self, parent, document: Document):
        QTreeView.__init__(self, parent)
        self.setWindowTitle("Project view")
        self.setObjectName("TreeViewDock")
        self._doc = document
        self._treeView = QTreeView(self)
        self.setWidget(self._treeView)
        self._treeView.setModel(DocumentItemModel(document))

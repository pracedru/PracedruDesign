from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QWidget

from Data.Document import Document
from Data.Vertex import Vertex
from GUI.Widgets.Drawers import draw_sketch


class NewDrawingViewWidget(QDialog):
    def __init__(self, parent, document: Document):
        QDialog.__init__(self, parent)
        self._doc = document
        layout = QVBoxLayout()
        self.setLayout(layout)
        content_widget = QWidget(self)
        content_widget.setLayout(QHBoxLayout())
        layout.addWidget(content_widget)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(dialog_buttons)

        controls_widget = QWidget()
        controls_widget.setLayout(QGridLayout())
        controls_widget.layout().addWidget(QLabel("Size"), 0, 0)
        paper_sizes = QComboBox(controls_widget)
        paper_sizes.addItems(["A0", "A1"])
        controls_widget.layout().addWidget(paper_sizes, 1, 0)
        controls_widget.layout().addWidget(QLabel("Header"), 2, 0)
        headers = QComboBox(controls_widget)
        headers.addItems(["Default", "BEnte"])
        controls_widget.layout().addWidget(headers, 3, 0)
        controls_widget.setMaximumWidth(150)

        content_widget.layout().addWidget(controls_widget)
        content_widget.layout().addWidget(HeaderViewWidget(self, None))


class HeaderViewWidget(QWidget):
    def __init__(self, parent, header):
        QWidget.__init__(self, parent)
        self._header = header
        self.setMinimumHeight(250)
        self.setMinimumWidth(250)

    def set_header(self, header):
        self._header = header
        self.update()

    def paintEvent(self, QPaintEvent):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.fillRect(QPaintEvent.rect(), QColor(255,255,255))
        half_width = self.width() / 2
        half_height = self.height() / 2
        center = Vertex(half_width, half_height)
        scale = 1
        offset = Vertex()
        if self._header is not None:
            draw_sketch(qp, self._header, scale, offset, center)
        qp.end()
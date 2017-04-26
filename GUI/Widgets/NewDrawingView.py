from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QWidget

from Data import Paper
from Data.Document import Document
from Data.Vertex import Vertex
from GUI.Widgets.Drawers import draw_sketch, create_pens


class NewDrawingViewWidget(QDialog):
    def __init__(self, parent, document: Document):
        QDialog.__init__(self, parent)
        self._doc = document
        layout = QVBoxLayout()
        self.setLayout(layout)
        content_widget = QWidget(self)
        content_widget.setLayout(QHBoxLayout())
        layout.addWidget(content_widget)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok )
        layout.addWidget(dialog_buttons)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)

        controls_widget = QWidget()
        controls_layout = QGridLayout()
        controls_widget.setLayout(controls_layout)
        controls_layout.addWidget(QLabel("Name"), 0, 0)
        self._name_edit = QLineEdit("New Drawing")
        controls_layout.addWidget(self._name_edit, 1, 0)
        controls_layout.addWidget(QLabel("Size"), 2, 0)
        self._paper_sizes = QComboBox(controls_widget)
        sizes = []
        for size in Paper.Sizes:
            sizes.append(size)
        sizes.sort()
        self._paper_sizes.addItems(sizes)
        controls_layout.addWidget(self._paper_sizes, 3, 0)
        controls_layout.addWidget(QLabel("Header"), 4, 0)
        self._headers = QComboBox(controls_widget)

        for header in document.get_drawings().get_headers():
            self._headers.addItem(header.name)

        controls_layout.addWidget(self._headers, 5, 0)
        controls_widget.setMaximumWidth(150)

        controls_layout.addWidget(QLabel("Orientation"), 6, 0)
        self._orientations = QComboBox(controls_widget)
        self._orientations.addItems(["Landscape", "Portrait"])
        controls_layout.addWidget(self._orientations, 7, 0)
        controls_layout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding), 8, 0)

        content_widget.layout().addWidget(controls_widget)
        self._header_view = HeaderViewWidget(self, None, self._doc)
        content_widget.layout().addWidget(self._header_view)
        self._header_view.set_header(self.header)

    @property
    def header(self):
        for header in self._doc.get_drawings().get_headers():
            if header.name == self._headers.currentText():
                return header
        return None

    @property
    def size(self):
        return Paper.Sizes[self._paper_sizes.currentText()]

    @property
    def name(self):
        return self._name_edit.text()

    @property
    def orientation(self):
        return self._orientations.currentIndex()


class HeaderViewWidget(QWidget):
    def __init__(self, parent, header, document):
        QWidget.__init__(self, parent)
        self._doc = document
        self._header = header
        self.setMinimumHeight(250)
        self.setMinimumWidth(250)

    def set_header(self, header):
        self._header = header
        self.update()

    def paintEvent(self, QPaintEvent):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        pens = create_pens(self._doc, 3000, QtGui.QColor(0, 0, 0))
        qp.fillRect(QPaintEvent.rect(), QColor(255, 255, 255))
        half_width = self.width() / 2
        half_height = self.height() / 2
        center = Vertex(half_width, half_height)
        if self._header is not None:
            limits = self._header.get_limits()
            header_width = limits[2] - limits[0]
            header_height = limits[3] - limits[1]
            scale_x = self.width() / header_width
            scale_y = self.height() / header_height
            scale = min(scale_x, scale_y)*0.9
            offset = Vertex(-limits[0] - header_width/2, -limits[1] - header_height/2)
            draw_sketch(qp, self._header, scale, offset, center, pens, {})
        qp.end()
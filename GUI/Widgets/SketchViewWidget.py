from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget

from Data.Vertex import Vertex
from GUI.Widgets.Drawers import create_pens, draw_sketch


class SketchViewWidget(QWidget):
    def __init__(self, parent, sketch, document):
        QWidget.__init__(self, parent)
        self._doc = document
        self._header = sketch
        self.setMinimumHeight(250)
        self.setMinimumWidth(250)

    def set_sketch(self, sketch):
        self._header = sketch
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        pens = create_pens(self._doc, 3000, QColor(0, 0, 0))
        qp.fillRect(event.rect(), QColor(255, 255, 255))
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

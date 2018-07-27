from PyQt5 import QtGui
from PyQt5.Qt import Qt
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QSizePolicy, QSpacerItem
from GUI.init import gui_scale, get_stylesheet
from GUI.Ribbon.RibbonButton import RibbonButton

__author__ = 'mamj'


class RibbonPane(QWidget):
    def __init__(self, parent, name):
        QWidget.__init__(self, parent)
        self.setStyleSheet(get_stylesheet("ribbonPane"))
        hlayout = QHBoxLayout()
        hlayout.setSpacing(0)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hlayout)
        vWidget = QWidget(self)
        hlayout.addWidget(vWidget)
        hlayout.addWidget(RibbonSeparator(self))
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vWidget.setLayout(vlayout)
        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color:rgba(0, 0, 0, 50%);")
        contentWidget = QWidget(self)
        vlayout.addWidget(contentWidget)
        vlayout.addWidget(label)
        contentLayout = QHBoxLayout()
        contentLayout.setAlignment(Qt.AlignLeft)
        contentLayout.setSpacing(0)
        contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout = contentLayout
        contentWidget.setLayout(contentLayout)

    def add_ribbon_widget(self, widget):
        self.contentLayout.addWidget(widget, 0, Qt.AlignTop)

    def add_grid_widget(self, width):
        widget = QWidget()
        # widget.setMaximumWidth(width)
        gridLayout = QGridLayout()
        widget.setLayout(gridLayout)
        gridLayout.setSpacing(4)
        gridLayout.setContentsMargins(4, 4, 4, 4)
        self.contentLayout.addWidget(widget)
        gridLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        return gridLayout

class RibbonSeparator(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setMinimumHeight(gui_scale()*80)
        self.setMaximumHeight(gui_scale()*80)
        self.setMinimumWidth(5)
        self.setMaximumWidth(5)
        self.setLayout(QHBoxLayout())

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QPen(QtGui.QColor(0, 0, 0, 50)))
        qp.drawLine(QPointF(2, 0), QPointF(2, self.height()))
        qp.end()
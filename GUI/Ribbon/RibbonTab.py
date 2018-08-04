from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from GUI.init import tr
from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.Ribbon.RibbonPane import RibbonPane


class RibbonTab(QWidget):
  def __init__(self, parent, name):
    QWidget.__init__(self, parent)
    layout = QHBoxLayout()
    self.setLayout(layout)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignLeft)
    self._panes = {}

  def add_ribbon_pane(self, name):
    name = tr(name, "ribbon")
    ribbon_pane = RibbonPane(self, name)
    self._panes[name] = ribbon_pane
    self.layout().addWidget(ribbon_pane)
    return ribbon_pane

  def get_ribbon_pane(self, name):
    name = tr(name, "ribbon")
    if name in self._panes:
      return self._panes[name]
    return self.add_ribbon_pane(name)

  def add_spacer(self):
    self.layout().addSpacerItem(QSpacerItem(1, 1, QSizePolicy.MinimumExpanding))
    self.layout().setStretch(self.layout().count() - 1, 1)

from PyQt5 import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *

from GUI import gui_scale, get_stylesheet

__author__ = 'magnus'


class RibbonButton(QToolButton):
    def __init__(self, owner, action, is_large):
        QPushButton.__init__(self, owner)
        # sc = 1
        sc = gui_scale()
        self._action = action
        self.update_button_status_from_action()
        self.clicked.connect(self._action.trigger)
        self._action.changed.connect(self.update_button_status_from_action)

        if is_large:
            self.setMaximumWidth(80 * sc)
            self.setMinimumWidth(50 * sc)
            self.setMinimumHeight(75 * sc)
            self.setMaximumHeight(75 * sc)
            self.setStyleSheet(get_stylesheet("ribbonButton"))
            self.setToolButtonStyle(3)
            self.setIconSize(QSize(32 * sc, 32 * sc))
        else:
            self.setToolButtonStyle(2)
            self.setMaximumWidth(120 * sc)
            self.setIconSize(QSize(16 * sc, 16 * sc))
            self.setStyleSheet(get_stylesheet("ribbonSmallButton"))

    def update_button_status_from_action(self):
        self.setText(self._action.text())
        self.setStatusTip(self._action.statusTip())
        self.setToolTip(self._action.toolTip())
        self.setIcon(self._action.icon())
        self.setEnabled(self._action.isEnabled())
        self.setCheckable(self._action.isCheckable())
        self.setChecked(self._action.isChecked())

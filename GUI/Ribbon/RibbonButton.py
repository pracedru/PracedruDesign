
from PyQt5.QtCore import QSize, QRectF, Qt
from PyQt5.QtGui import QPainter, QFontMetrics, QFont
from PyQt5.QtWidgets import *

from GUI.init import gui_scale, get_stylesheet

__author__ = 'magnus'


class RibbonButton(QToolButton):
	def __init__(self, owner, action, is_large):
		QPushButton.__init__(self, owner)
		# sc = 1
		sc = gui_scale()
		self.text = action.text()
		self._action = action
		self.textWidth = 50;

		self.clicked.connect(self._action.trigger)
		self._action.changed.connect(self.update_button_status_from_action)
		self.font = QFont()
		self.font.setPointSizeF(10*sc)
		fm = QFontMetrics(QFont())
		for t in self.text.split("\n"):
			self.textWidth = max(self.textWidth, fm.width(t)+10)

		if is_large:
			self.setStyleSheet(get_stylesheet("ribbonButton"))
			self.setToolButtonStyle(3)
			self.setIconSize(QSize(32 * sc, 32 * sc))
			self.setMaximumWidth(90 * sc)
			self.setMinimumWidth(50 * sc)
			self.setMinimumHeight(80 * sc)
			self.setMaximumHeight(95 * sc)
		else:
			self.setToolButtonStyle(2)
			self.setMaximumWidth(120 * sc)
			self.setIconSize(QSize(16 * sc, 16 * sc))
			self.setStyleSheet(get_stylesheet("ribbonSmallButton"))

		self.update_button_status_from_action()

	def paintEvent(self, event):
		if self.toolButtonStyle() == 3:
			qp = QPainter()
			qp.begin(self)
			qp.setFont(self.font)
			qp.drawText(QRectF(0, 32, self.textWidth,60), Qt.AlignHCenter | Qt.AlignVCenter, self.text)
			qp.end()

		return super(RibbonButton, self).paintEvent(event)

	def sizeHint(self):
		return QSize(self.textWidth, 85*gui_scale())

	def update_button_status_from_action(self):
		if self.toolButtonStyle() == 3:
			pass
		else:
			self.setText(self._action.text())
		self.setStatusTip(self._action.statusTip())
		self.setToolTip(self._action.toolTip())
		self.setIcon(self._action.icon())
		self.setEnabled(self._action.isEnabled())
		self.setCheckable(self._action.isCheckable())
		self.setChecked(self._action.isChecked())

from PyQt5.QtWidgets import QWidget


class PartViewWidget(QWidget):
    def __init__(self, parent, document):
        QWidget.__init__(self, parent)
        self._document = document

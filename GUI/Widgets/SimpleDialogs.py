from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class AddArcDialog(QDialog):
    def __init__(self, parent, sketch):
        QDialog.__init__(self, parent)
        self._sketch = sketch
        self.setWindowTitle("Select parameters for arc.")
        self._params = []
        self._params.sort()
        for param_tuple in self._sketch.get_all_parameters():
            self._params.append(param_tuple[1].name)
        self.setLayout(QVBoxLayout())
        contents_widget = QWidget(self)
        contents_layout = QGridLayout()
        contents_widget.setLayout(contents_layout)
        contents_layout.addWidget(QLabel("Radius"), 0, 0)
        contents_layout.addWidget(QLabel("Start angle"), 1, 0)
        contents_layout.addWidget(QLabel("End angle"), 2, 0)
        self._radius_combo_box = QComboBox()
        self._sa_combo_box = QComboBox()
        self._ea_combo_box = QComboBox()
        self._radius_combo_box.addItems(self._params)
        self._radius_combo_box.setEditable(True)
        self._sa_combo_box.addItems(self._params)
        self._sa_combo_box.setEditable(True)
        self._ea_combo_box.addItems(self._params)
        self._ea_combo_box.setEditable(True)
        contents_layout.addWidget(self._radius_combo_box, 0, 1)
        contents_layout.addWidget(self._sa_combo_box, 1, 1)
        contents_layout.addWidget(self._ea_combo_box, 2, 1)
        self.layout().addWidget(contents_widget)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        self.layout().addWidget(dialog_buttons)

    def radius_param(self):
        return self._radius_combo_box.currentText()

    def start_angle_param(self):
        return self._sa_combo_box.currentText()

    def end_angle_param(self):
        return self._ea_combo_box.currentText()
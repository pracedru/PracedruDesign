from math import pi

from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QComboBox, QLineEdit
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from Data.Axis import Axis
from GUI.Widgets.SketchViewWidget import SketchViewWidget


class SketchDialog(QDialog):
    def __init__(self, parent, document, part):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Select sketch and plane")
        self._sketches = []
        self._planes = []
        self._doc = document
        for sketch in document.get_geometries().get_sketches():
            self._sketches.append(sketch.name)
        self._sketches.sort()
        for plane in part.get_plane_features():
            self._planes.append(plane.name)
        self._planes.sort()
        self.setLayout(QVBoxLayout())
        contents_widget = QWidget(self)
        contents_layout = QGridLayout()
        contents_widget.setLayout(contents_layout)
        contents_layout.addWidget(QLabel("Sketch"), 0, 0)
        contents_layout.addWidget(QLabel("Plane"), 1, 0)
        self._sketch_combo_box = QComboBox()
        self._plane_combo_box = QComboBox()

        self._sketch_combo_box.addItems(self._sketches)
        self._sketch_combo_box.setEditable(False)
        self._plane_combo_box.addItems(self._planes)
        self._plane_combo_box.setEditable(False)

        contents_layout.addWidget(self._sketch_combo_box, 0, 1)
        contents_layout.addWidget(self._plane_combo_box, 1, 1)

        self.layout().addWidget(contents_widget)

        self._header_view = SketchViewWidget(self, None, self._doc)
        self.layout().addWidget(self._header_view)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)

        self.layout().addWidget(dialog_buttons)
        self._sketch_combo_box.currentTextChanged.connect(self.on_sketch_selection_changed)
        self.on_sketch_selection_changed()

    def on_sketch_selection_changed(self):
        sketch_name = self._sketch_combo_box.currentText()
        sketch = self._doc.get_geometries().get_sketch_by_name(sketch_name)
        self._header_view.set_sketch(sketch)

    def sketch(self):
        return self._sketch_combo_box.currentText()

    def plane(self):
        return self._plane_combo_box.currentText()


class ExtrudeDialog(QDialog):
    def __init__(self, parent, document, part):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Area extrude")
        self._sketches = []
        self._part = part
        for sketch_feature in part.get_sketch_features():
            self._sketches.append(sketch_feature.name)
        self._sketches.sort()
        self.setLayout(QVBoxLayout())
        contents_widget = QWidget(self)
        contents_layout = QGridLayout()
        contents_widget.setLayout(contents_layout)
        contents_layout.addWidget(QLabel("Sketch"), 0, 0)
        contents_layout.addWidget(QLabel("Area"), 1, 0)
        contents_layout.addWidget(QLabel("Extrude direction"), 2, 0)
        contents_layout.addWidget(QLabel("Extrude length"), 3, 0)

        self._sketch_combo_box = QComboBox()
        self._area_combo_box = QComboBox()
        self._direction = QComboBox()

        self._direction.addItems(['Forward', 'Backward', 'Both'])

        self._sketch_combo_box.addItems(self._sketches)
        self._sketch_combo_box.setEditable(False)
        #self._area_combo_box.addItems(self._params)
        self._area_combo_box.setEditable(False)

        self._length_edit = QLineEdit(QLocale().toString(0.1))

        contents_layout.addWidget(self._sketch_combo_box, 0, 1)
        contents_layout.addWidget(self._area_combo_box, 1, 1)
        contents_layout.addWidget(self._direction, 2, 1)
        contents_layout.addWidget(self._length_edit, 3, 1)

        self.layout().addWidget(contents_widget)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        self._sketch_view = SketchViewWidget(self, None, document)
        self.layout().addWidget(self._sketch_view)
        self.layout().addWidget(dialog_buttons)

        self._sketch_combo_box.currentIndexChanged.connect(self.on_sketch_selection_changed)
        self.on_sketch_selection_changed()
        sketch = self.sketch_feature.get_objects()[0]
        self._sketch_view.set_sketch(sketch)

    def on_sketch_selection_changed(self):
        self._area_combo_box.clear()
        areas = []
        for sketch_feature in self._part.get_sketch_features():
            if sketch_feature.name == self._sketch_combo_box.currentText():
                sketch = sketch_feature.get_objects()[0]
                self._sketch_view.set_sketch(sketch)
                for area in sketch.get_areas():
                    areas.append(area[1].name)
        self._area_combo_box.addItems(areas)

    @property
    def length(self):
        return QLocale().toDouble(self._length_edit.text())[0]

    @property
    def direction(self):
        return self._direction.currentIndex()

    @property
    def sketch_feature(self):
        for sketch_feature in self._part.get_sketch_features():
            if sketch_feature.name == self._sketch_combo_box.currentText():
                return sketch_feature
        return None

    @property
    def area(self):
        for sketch_feature in self._part.get_sketch_features():
            if sketch_feature.name == self._sketch_combo_box.currentText():
                sketch = sketch_feature.get_objects()[0]
                for area_tuple in sketch.get_areas():
                    if area_tuple[1].name == self._area_combo_box.currentText():
                        return area_tuple[1]
        return None


class RevolveDialog(QDialog):
    def __init__(self, parent, document, part):
        QDialog.__init__(self, parent)
        self._doc = document
        self.setWindowTitle("Area extrude")
        self._sketches = []
        self._part = part
        for sketch_feature in part.get_sketch_features():
            self._sketches.append(sketch_feature.name)
        self._sketches.sort()
        self.setLayout(QVBoxLayout())
        contents_widget = QWidget(self)
        contents_layout = QGridLayout()
        contents_widget.setLayout(contents_layout)
        contents_layout.addWidget(QLabel("Sketch"), 0, 0)
        contents_layout.addWidget(QLabel("Area"), 1, 0)
        contents_layout.addWidget(QLabel("Axis"), 2, 0)
        contents_layout.addWidget(QLabel("Revolve direction"), 3, 0)
        contents_layout.addWidget(QLabel("Revolve angle"), 4, 0)

        self._sketch_combo_box = QComboBox()
        self._area_combo_box = QComboBox()
        self._axis_combo_box = QComboBox()
        self._direction = QComboBox()

        self._direction.addItems(['Forward', 'Backward', 'Both'])
        self._sketch_combo_box.addItems(self._sketches)
        self._length_edit = QLineEdit(QLocale().toString(360))

        contents_layout.addWidget(self._sketch_combo_box, 0, 1)
        contents_layout.addWidget(self._area_combo_box, 1, 1)
        contents_layout.addWidget(self._axis_combo_box, 2, 1)
        contents_layout.addWidget(self._direction, 3, 1)
        contents_layout.addWidget(self._length_edit, 4, 1)

        self.layout().addWidget(contents_widget)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        self._sketch_view = SketchViewWidget(self, None, document)
        self.layout().addWidget(self._sketch_view)
        self.layout().addWidget(dialog_buttons)

        self._sketch_combo_box.currentIndexChanged.connect(self.on_sketch_selection_changed)
        self.on_sketch_selection_changed()
        sketch = self.sketch_feature.get_objects()[0]
        self._sketch_view.set_sketch(sketch)

    def on_sketch_selection_changed(self):
        self._area_combo_box.clear()
        self._axis_combo_box.clear()
        self._axis_combo_box.addItems(['x', 'y', 'z'])
        areas = []
        edge_names = []
        for sketch_feature in self._part.get_sketch_features():
            if sketch_feature.name == self._sketch_combo_box.currentText():
                sketch = sketch_feature.get_objects()[0]
                self._sketch_view.set_sketch(sketch)
                for area in sketch.get_areas():
                    areas.append(area[1].name)
                areas.sort()
                for edge in sketch.get_edges():
                    edge_names.append(edge[1].name)
                edge_names.sort()
        self._axis_combo_box.addItems(edge_names)
        self._area_combo_box.addItems(areas)

    @property
    def length(self):
        return QLocale().toDouble(self._length_edit.text())[0]*pi/180

    @property
    def direction(self):
        return self._direction.currentIndex()

    @property
    def sketch_feature(self):
        for sketch_feature in self._part.get_sketch_features():
            if sketch_feature.name == self._sketch_combo_box.currentText():
                return sketch_feature
        return None

    @property
    def area(self):
        for sketch_feature in self._part.get_sketch_features():
            if sketch_feature.name == self._sketch_combo_box.currentText():
                sketch = sketch_feature.get_objects()[0]
                for area_tuple in sketch.get_areas():
                    if area_tuple[1].name == self._area_combo_box.currentText():
                        return area_tuple[1]
        return None

    def get_axis(self):
        axis = Axis(self._doc)
        axis.direction.x = 0
        axis.direction.y = 0
        axis.direction.z = 0
        name = self._axis_combo_box.currentText()
        if self._axis_combo_box.currentIndex()<3:
            if name == 'x':
                axis.direction.x = 1
            elif name == 'y':
                axis.direction.y = 1
            else:
                axis.direction.z = 1
        else:
            sketch = self.sketch_feature.get_objects()[0]
            edge = sketch.get_edge_by_name(name)
            axis.set_edge_governor(edge, sketch)
        return axis


class AddArcDialog(QDialog):
    def __init__(self, parent, sketch):
        QDialog.__init__(self, parent)
        self._sketch = sketch
        self.setWindowTitle("Select parameters for arc.")
        self._params = []
        for param_tuple in self._sketch.get_all_parameters():
            self._params.append(param_tuple[1].name)
        self._params.sort()
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
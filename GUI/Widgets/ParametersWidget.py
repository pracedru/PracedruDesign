from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtCore import QMargins
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QInputDialog, QMessageBox

import Business
from GUI import gui_scale
from GUI.Models.ParametersModel import ParametersModel


class ParametersWidget(QWidget):
    def __init__(self, parent, document):
        QWidget.__init__(self, parent)
        # self._document = document
        self._parameters = document.get_parameters()
        self.parameters_table = QTableView(self)
        self.parameters_model = ParametersModel(self._parameters)
        self.parameters_sort_model = QSortFilterProxyModel()
        self.parameters_sort_model.setSourceModel(self.parameters_model)
        self.parameters_table.setModel(self.parameters_sort_model)
        self.parameters_table.setSortingEnabled(True)
        self.parameters_sort_model.setSortCaseSensitivity(False)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.parameters_table)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        guiscale = gui_scale()
        self.parameters_table.setColumnWidth(0, 120*guiscale)
        self.parameters_table.setColumnWidth(1, 150*guiscale)
        self.parameters_table.setColumnWidth(2, 80*guiscale)
        self.parameters_table.setColumnWidth(3, 40*guiscale)
        buttons_widget = QWidget()
        buttons_widget.setLayout(QHBoxLayout())
        add_button = QPushButton("Add Parameter")
        add_button.clicked.connect(self.on_add_parameter)
        buttons_widget.layout().addWidget(add_button)
        delete_button = QPushButton("Delete Parameter")
        buttons_widget.layout().addWidget(delete_button)
        delete_button.clicked.connect(self.on_delete)
        governor_button = QPushButton("Set governor")
        governor_button.clicked.connect(self.on_set_governor)
        buttons_widget.layout().addWidget(governor_button)
        layout.addWidget(buttons_widget)
        self.installEventFilter(self)
        self.hide_hidden_params = True
        self.update_hide_parameters()
        self.parameters_table.selectionModel().selectionChanged.connect(self.on_param_selection_changed)

    def set_parameters(self, params):
        self._parameters = params
        self.parameters_model.set_parameters(params)

    def on_add_parameter(self):
        # self.parent().parent().on_add_parameter()
        Business.add_parameter(self._parameters)
        ndx = self.parameters_model.index(self.parameters_model.rowCount()-1, 0)
        index = self.parameters_sort_model.mapFromSource(ndx)
        self.parameters_table.scrollTo(index)
        sm = self.parameters_table.selectionModel()
        sm.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

    def on_set_governor(self):
        rows = self.parameters_table.selectionModel().selectedRows()
        params = []
        for param_tuple in self._parameters.get_all_parameters():
            params.append(param_tuple[1].name)
        params.sort()
        value = QInputDialog.getItem(self, "Set parameter", "Parameter:", params, 0, False)
        governor_parameter = self._parameters.get_parameter_by_name(value[0])
        for ndx in rows:
            index = self.parameters_sort_model.mapToSource(ndx)
            row = index.row()
            param = self._parameters.get_parameter_item(row)
            if param is not governor_parameter:
                param.value = (governor_parameter.name + "+" + str(round(param.value-governor_parameter.value, 4))).replace("+-", '-')

    def on_delete(self):
        txt = "Are you sure you want to delete this parameter?"
        ret = QMessageBox.warning(self, "Delete parameter?", txt, QMessageBox.Yes | QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            selection_model = self.parameters_table.selectionModel()
            indexes = selection_model.selectedIndexes()
            selected_rows = set()
            for index in indexes:
                index = self.parameters_sort_model.mapToSource(index)
                selected_rows.add(index.row())
            self.parameters_model.remove_rows(selected_rows)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self.on_delete()
                return True
        return False

    def update_hide_parameters(self):
        rowcount = self.parameters_sort_model.rowCount()
        for i in range(rowcount):
            index = self.parameters_model.index(i, 0)
            index = self.parameters_sort_model.mapFromSource(index)
            row = index.row()
            if self.hide_hidden_params:
                hide = self.parameters_model.row_hidden(i)
                if hide:
                    self.parameters_table.hideRow(row)
                else:
                    self.parameters_table.showRow(row)
            else:
                self.parameters_table.showRow(i)

    def on_param_selection_changed(self, selection):
        pass
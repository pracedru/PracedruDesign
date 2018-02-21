from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox
from Data.Parameters import *
from GUI import formula_from_locale, formula_to_locale

__author__ = 'mamj'

col_header = ["Name", "Expression", "Value", 'Hide']


class ParametersModel(QAbstractTableModel):
  def __init__(self, parameters: Parameters):
    QAbstractItemModel.__init__(self)
    self._parameters = parameters
    parameters.add_change_handler(self.on_parameters_changed)
    self.old_row_count = 0

  def set_parameters(self, params):
    self.layoutAboutToBeChanged.emit()
    self._parameters.remove_change_handler(self.on_parameters_changed)
    self._parameters = params
    self._parameters.add_change_handler(self.on_parameters_changed)
    self.layoutChanged.emit()

  def rowCount(self, model_index=None, *args, **kwargs):
    return self._parameters.length_all

  def columnCount(self, model_index=None, *args, **kwargs):
    return 4

  def data(self, model_index: QModelIndex, int_role=None):
    col = model_index.column()
    row = model_index.row()
    data = None
    if int_role == Qt.DisplayRole:
      param_item = self._parameters.get_parameter_item(row)
      if col == 0:
        data = param_item.full_name
      elif col == 1:
        if param_item is Parameters:
          param = param_item.get_parameter(col - 2)
        else:
          param = param_item
        data = formula_to_locale(param.formula)
      elif col == 2:
        if param_item is Parameters:
          param = param_item.get_parameter(col - 2)
        else:
          param = param_item
        data = param.value
      elif col == 3:
        data = None  # param_item.hidden
    elif int_role == Qt.CheckStateRole:
      param_item = self._parameters.get_parameter_item(row)
      if col == 3:
        if param_item.hidden:
          return Qt.Checked
        else:
          return Qt.Unchecked
    elif int_role == Qt.EditRole:
      param_item = self._parameters.get_parameter_item(row)
      if col == 0:
        data = param_item.name
      elif col == 1:
        if param_item is Parameters:
          param = param_item.get_parameter(col - 1)
        else:
          param = param_item
        if param.formula != "":
          data = data = formula_to_locale(param.formula)
        else:
          data = QLocale().toString(param.value)
      elif col == 2:
        if param_item is Parameters:
          param = param_item.get_parameter(col - 2)
        else:
          param = param_item
        if param.formula != "":
          data = formula_to_locale(param.formula)
        else:
          data = QLocale().toString(param.value)
    return data

  def setData(self, model_index: QModelIndex, value: QVariant, int_role=None):
    col = model_index.column()
    row = model_index.row()
    param_item = self._parameters.get_parameter_item(row)
    if col == 0:
      param_item.name = value
      return True
    elif col == 1 or col == 2:
      if param_item is Parameters:
        param = param_item.get_parameter(col - 1)
      else:
        param = param_item
      if isinstance(value, float):
        param.value = value
        return True
      parsed = QLocale().toDouble(value)
      if parsed[1]:
        param.value = parsed[0]
      else:
        try:
          if value == "":
            param.value = 0.0
          else:
            param.value = formula_from_locale(value)
        except Exception as ex:
          QMessageBox.information(None, "Error", str(ex))
      return True
    elif col == 3:
      if int_role == Qt.CheckStateRole:
        hide = value == Qt.Checked
        param_item.hidden = hide
    return False

  def on_parameters_changed(self, event):
    if type(event.object) is Parameter:
      if event.type == event.BeforeObjectAdded:
        parent = QModelIndex()
        row = self.rowCount()
        self.beginInsertRows(parent, row, row)
      if event.type == event.ObjectAdded:
        self.endInsertRows()
      if event.type == event.BeforeObjectRemoved:
        row = self._parameters.get_index_of(event.object)
        self.beginRemoveRows(QModelIndex(), row, row)
      if event.type == event.ObjectRemoved:
        self.endRemoveRows()
      if event.type == event.ValueChanged:
        param = event.sender
        if type(param) is Parameter:
          row = self._parameters.get_index_of(param)
          left = self.createIndex(row, 0)
          right = self.createIndex(row, 3)
          self.dataChanged.emit(left, right)
      if event.type == event.HiddenChanged:
        param = event.sender
        if type(param) is Parameter:
          row = self._parameters.get_index_of(param)
          left = self.createIndex(row, 3)
          right = self.createIndex(row, 3)
          self.dataChanged.emit(left, right)

  def flags(self, model_index: QModelIndex):
    default_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
    if model_index.column() == 3:
      default_flags = Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
    return default_flags

  def headerData(self, p_int, orientation, int_role=None):
    if int_role == Qt.DisplayRole:
      if orientation == Qt.Vertical:
        return p_int
      else:
        return col_header[p_int]

    else:
      return

  def get_parameters_object(self):
    return self._parameters

  def remove_rows(self, rows):
    params = []
    for row in rows:
      params.append(self._parameters.get_parameter_item(row))
    self._parameters.delete_parameters(params)

  def row_hidden(self, row):
    return self._parameters.get_parameter_item(row).hidden

  def get_parameter_from_row(self, row):
    return self._parameters.get_parameter_item(row)

  def get_row_from_parameter(self, parameter):
    return self._parameters.get_index_of(parameter)

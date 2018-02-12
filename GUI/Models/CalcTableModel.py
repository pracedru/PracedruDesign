from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt

col_header_letters  = "ABCDEFGHIJKLMNOPQRSTUVXYZ"

class CalcTableModel(QAbstractTableModel):
  def __init__(self, doc):
    QAbstractTableModel.__init__(self)
    self._doc = doc

  def rowCount(self, model_index=None, *args, **kwargs):
    return 30

  def columnCount(self, model_index=None, *args, **kwargs):
    return 10

  def set_table(self, calc_table):
    self._calc_table = calc_table

  def data(self, index: QModelIndex, role: int = ...):
    if role == Qt.DisplayRole:
      cell = self._calc_table.get_cell(index.row(), index.column())
      if cell is not None:
        return cell.value
    if role == Qt.EditRole:
      cell = self._calc_table.get_cell(index.row(), index.column())
      if cell is not None:
        return cell.formula
    return None

  def headerData(self, p_int, orientation, role):
    if role == Qt.DisplayRole:
      if orientation == Qt.Vertical:
        return p_int+1
      else:
        return self.col_header(p_int)

    else:
      return

  def col_header(self, p_int):
    return col_header_letters[p_int]

  def setData(self, index: QModelIndex, value, role):
    if role == Qt.EditRole:
      self._calc_table.set_cell_value(index.row(), index.column(), value)
      return True
    return False

  def flags(self, model_index: QModelIndex):
    default_flags = Qt.ItemIsSelectable

    default_flags = default_flags | Qt.ItemIsEditable | Qt.ItemIsEnabled
    return default_flags
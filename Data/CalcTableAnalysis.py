from Data.Analysis import Analysis
from Data.Events import ChangeEvent


class CalcTableAnalysis(Analysis):
  def __init__(self, name, analysisType, document):
    Analysis.__init__(self, name, analysisType, document)
    self._row_count = 0
    self._col_count = 0
    self._rows = {}

  def get_cell(self, row, col):
    if row in self._rows.keys():
      if col in self._rows[row].keys():
        return self._rows[row][col]
    return None

  def set_cell_value(self, row, col, value):
    cell = self.get_cell(row, col)
    if cell == None:
      cell = self.create_parameter()
      if row not in self._rows.keys():
        self._rows[row] = {}
      self._rows[row][col] = cell
    if value == "":
      cell.changed(ChangeEvent(self, ChangeEvent.Deleted, cell))
      self._rows[row].pop(col)
    else:
      cell.value = value


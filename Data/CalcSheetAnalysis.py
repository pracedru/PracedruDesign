from Data.Analysis import Analysis
from Data.Events import ChangeEvent
from Data.Paper import Paper
from Data.Vertex import Vertex


class CalcSheetAnalysis(Analysis):
  def __init__(self, name, document):
    Analysis.__init__(self, name, Analysis.CalcSheetAnalysisType, document)
    self._calcs = []
    self._size = Vertex(1,1)

  def get_calculations(self):
    return self._calcs

  def create_calculation(self):
    pass

  @property
  def size(self):
    return [self._size.x, self._size.y]
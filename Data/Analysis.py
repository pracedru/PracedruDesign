from enum import Enum

from Data.Objects import IdObject
from Data.Parameters import Parameters

class AnalysisType(Enum):
  CalcSheet = 0
  CalcTable = 1
  SpatialNumerical = 2

class Analysis(IdObject, Parameters):
  def __init__(self, name, analysisType, document):
    IdObject.__init__(self)
    Parameters.__init__(self, name, document.get_parameters())
    self._analysisType = analysisType
    self._doc = document

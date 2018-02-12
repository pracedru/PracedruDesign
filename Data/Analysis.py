from Data.Objects import IdObject
from Data.Parameters import Parameters


class Analysis(IdObject, Parameters):
  CalcSheetAnalysisType = 0
  CalcTableAnalysisType = 1
  SpatialNumericalAnalysisType = 2

  def __init__(self, name, analysisType, document):
    IdObject.__init__(self)
    Parameters.__init__(self, name, document.get_parameters())
    self._analysisType = analysisType
    self._doc = document

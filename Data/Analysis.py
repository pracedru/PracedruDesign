from Data.Objects import IdObject, NamedObservableObject


class Analysis(IdObject, NamedObservableObject):
    CalcSheetAnalysis = 0
    CalcTableAnalysis = 1
    SpatialNumericalAnalysis = 2

    def __init__(self, name, analysisType, document):
        IdObject.__init__(self)
        NamedObservableObject.__init__(self, name)
        self._analysisType = analysisType
        self._doc = document
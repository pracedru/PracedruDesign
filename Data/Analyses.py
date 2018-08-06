from Data.Analysis import Analysis, AnalysisType
from Data.CalcSheetAnalysis import CalcSheetAnalysis
from Data.CalcTableAnalysis import CalcTableAnalysis
from Data.Events import ChangeEvent
from Data.Objects import ObservableObject


class Analyses(ObservableObject):
	def __init__(self, document):
		ObservableObject.__init__(self)
		self._doc = document
		self._analyses = {}

	def items(self):
		return self._analyses.items()

	@property
	def name(self):
		return "Analyses"

	def create_calc_table_analysis(self, name):
		analysis = CalcTableAnalysis(name, self._doc)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, analysis))
		self._analyses[analysis.uid] = analysis
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, analysis))
		analysis.add_change_handler(self.analysis_changed)
		return analysis

	def create_calc_sheet_analysis(self, name):
		analysis = CalcSheetAnalysis(name, self._doc)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, analysis))
		self._analyses[analysis.uid] = analysis
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, analysis))
		analysis.add_change_handler(self.analysis_changed)
		return analysis

	def analysis_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			if isinstance(event.object, Analysis):
				if event.object.uid in self._analyses.keys():
					self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
					self._analyses.pop(event.object.uid)
					self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
		self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

	def serialize_json(self):
		return {
			'analyses': self._analyses
		}

	@staticmethod
	def deserialize(data, document):
		analyses = Analyses(document)
		if data is not None:
			analyses.deserialize_data(data, document)
		return analyses

	def deserialize_data(self, data, document):
		for analysis_uid in data['analyses']:
			analysis_data = data['analyses'][analysis_uid]
			analysis = None

			if analysis_data['type'] == AnalysisType.CalcTable.value:
				analysis = CalcTableAnalysis.deserialize(analysis_data, document)
				analysis.add_change_handler(self.analysis_changed)
			# if geometry_data['type'] == Geometry.Part:
			#  geometry = Part.deserialize(geometry_data, document.get_parameters(), document)
			if analysis is not None:
				self._analyses[analysis.uid] = analysis

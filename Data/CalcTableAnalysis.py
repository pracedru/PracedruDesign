import math

from Data.Analysis import Analysis, AnalysisType
from Data.Events import ChangeEvent
from Data.Objects import IdObject
from Data.Parameters import Parameters

col_header_letters = "ABCDEFGHIJKLMNOPQRSTUVXYZ"


def col_letter_to_index(letters):
	value = 0
	length = len(letters)
	for i in range(length):
		potens = length - i - 1
		letter_index = col_header_letters.index(letters[i])
		if potens > 0:
			letter_index += 1
		value += (len(col_header_letters) ** potens) * (letter_index)
	return int(value)


def col_index_to_letter(index):
	if index >= len(col_header_letters):
		rest = index % len(col_header_letters)
		id = math.floor(index / len(col_header_letters)) - 1
		return col_index_to_letter(id) + col_index_to_letter(rest)
	else:
		return col_header_letters[index]


def cell_name_to_indexes(name):
	Letters = ""
	number = ""
	letters_finished = False
	for l in name:
		if l.isalpha():
			Letters += l
			if letters_finished:
				raise ValueError("Cell address syntax error")
		else:
			letters_finished = True
			if len(Letters) == 0:
				raise ValueError("Cell address syntax error")
			number += l
	return [col_letter_to_index(Letters), int(number)]


class CalcTableAnalysis(Analysis):
	def __init__(self, name, document):
		Analysis.__init__(self, name, AnalysisType.CalcTable, document)
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
		if cell is None:
			if value != "":
				cell = self.create_parameter(col_index_to_letter(col) + str(row + 1))
				if row not in self._rows.keys():
					self._rows[row] = {}
				self._rows[row][col] = cell
		if value == "" and cell is not None:
			self.delete_parameter(cell.uid)
			self._rows[row].pop(col)
		elif cell is not None:
			cell.value = value

	def serialize_rows(self):
		rows = {}
		for row_tuple in self._rows.items():
			row_index = row_tuple[0]
			rows[row_index] = {}
			for col_tuple in row_tuple[1].items():
				col_index = col_tuple[0]
				parm = col_tuple[1]
				rows[row_index][col_index] = parm.uid
		return rows

	def deserialize_rows(self, data):
		for row_index in data:
			cols = data[row_index]
			for col_index in cols:
				uid = cols[col_index]
				cell = self.get_parameter_by_uid(uid)
				if row_index not in self._rows.keys():
					self._rows[int(row_index)] = {}
				self._rows[int(row_index)][int(col_index)] = cell

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'parameters': Parameters.serialize_json(self),
			'rows': self.serialize_rows(),
			'type': self._analysisType.value
		}

	@staticmethod
	def deserialize(data, document):
		sketch = CalcTableAnalysis("", document)
		if data is not None:
			sketch.deserialize_data(data)
		return sketch

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		Parameters.deserialize_data(self, data['parameters'])
		self.deserialize_rows(data['rows'])

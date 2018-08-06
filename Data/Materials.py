from Data.Events import ChangeEvent
from Data.Objects import ObservableObject, IdObject

__author__ = 'mamj'


class Material(IdObject, ObservableObject):
	def __init__(self, doc):
		IdObject.__init__(self)
		ObservableObject.__init__(self)
		self._name = "New Material"
		self._allow_stresses = [[273.15, 250e6], [293.15, 250e6]]
		self._poissons_ratios = [[273.15, 0.3], [293.15, 0.3]]
		self._youngs_moduli = [[273.15, 203e9], [293.15, 203e9]]
		self._alphas = [[273.15, 1.11e-5], [293.15, 1.11e-5]]
		self._ks = [[273.15, 60.0], [293.15, 60.0]]
		self._areas = set()
		self._doc = doc
		self._material_number = 1

	@property
	def name(self):
		return self._name

	def set_name(self, name):
		self._name = name
		self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

	def get_poissons_ratio(self, temp):
		return self._interpolate(self._poissons_ratios, temp)

	def get_poissons_ratios(self):
		return self._poissons_ratios

	def add_poissons_ratio(self, temp, poissons):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, self._poissons_ratios))
		if temp is None:
			temp = self._poissons_ratios[len(self._poissons_ratios) - 1][0]
		if poissons is None:
			poissons = self._poissons_ratios[len(self._poissons_ratios) - 1][1]
		self._poissons_ratios.append([temp, poissons])
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, self._poissons_ratios))

	def get_youngs_modulus(self, temp):
		return self._interpolate(self._youngs_moduli, temp)

	def get_youngs_moduli(self):
		return self._youngs_moduli

	def add_youngs_modulus(self, temp, youngs):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, self._youngs_moduli))
		if temp is None:
			temp = self._youngs_moduli[len(self._youngs_moduli) - 1][0]
		if youngs is None:
			youngs = self._youngs_moduli[len(self._youngs_moduli) - 1][1]
		self._youngs_moduli.append([temp, youngs])
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, self._youngs_moduli))

	def get_ks(self):
		return self._ks

	def add_k(self, temp, k):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, self._ks))
		if temp is None:
			temp = self._ks[len(self._ks) - 1][0]
		if k is None:
			k = self._ks[len(self._ks) - 1][1]
		self._ks.append([temp, k])
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, self._ks))

	def get_areas(self):
		areas = []
		for area in self._areas:
			areas.append(area)
		return areas

	def get_allow_stresses(self):
		return self._allow_stresses

	def add_allowable_stress(self, temp, stress):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, self._allow_stresses))
		if temp is None:
			temp = self._allow_stresses[len(self._allow_stresses) - 1][0]
		if stress is None:
			stress = self._allow_stresses[len(self._allow_stresses) - 1][1]
		self._allow_stresses.append([temp, stress])
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, self._allow_stresses))

	def get_alphas(self):
		return self._alphas

	def add_alpha(self, temp, alpha):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, self._alphas))
		if temp is None:
			temp = self._alphas[len(self._alphas) - 1][0]
		if alpha is None:
			alpha = self._alphas[len(self._alphas) - 1][1]
		self._alphas.append([temp, alpha])
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, self._alphas))

	def add_areas(self, areas):
		for area in areas:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, area))
			self._areas.add(area)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, area))
			area.add_change_handler(self.on_area_changed)

	def remove_area(self, area):
		if area in self._areas:
			self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, area))
			self._areas.remove(area)
			self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, area))
			area.remove_change_handler(self.on_area_changed)

	def on_area_changed(self, event):
		if event.type == ChangeEvent.Deleted:
			if event.object in self._areas:
				self._areas.remove(event.object)
				event.object.remove_change_handler(self.on_area_changed)

	@property
	def number(self):
		return self._material_number

	@number.setter
	def number(self, value):
		self._material_number = value

	@staticmethod
	def _interpolate(table, temp):
		if len(table) == 1:
			return table[0][1]
		counter = 0
		for tuple in table:
			t = tuple[0]
			if t > temp:
				if counter == 0:
					next_t = table[1][0]
					next_val = table[1][1]
					delta = (next_val - tuple[1]) / next_t - t
					return tuple[1] + delta * (temp - t)
				else:
					prev_t = table[counter - 1][0]
					prev_val = table[counter - 1][1]
					delta = (prev_val - tuple[1]) / prev_t - t
					return tuple[1] + delta * (temp - t)
			if counter >= len(table) - 1:
				return tuple[1]
			counter += 1

	def _area_uids(self):
		uids = []
		for area in self._areas:
			uids.append(area.uid)
		return uids

	def serialize_json(self):
		return {
			'uid': IdObject.serialize_json(self),
			'name': self._name,
			'number': self._material_number,
			'sa': self._allow_stresses,
			'youngs': self._youngs_moduli,
			'poissons': self._poissons_ratios,
			'alpha': self._alphas,
			'ks': self._ks,
			'areas': self._area_uids()
		}

	@staticmethod
	def deserialize(data, document):
		material = Material(document)
		if data is not None:
			material.deserialize_data(data)
		return material

	def deserialize_data(self, data):
		IdObject.deserialize_data(self, data['uid'])
		self._name = data['name']
		self._material_number = data.get('number', 0)
		self._youngs_moduli = data.get('youngs', [])
		self._poissons_ratios = data.get('poissons', [])
		self._alphas = data.get('alpha', [])
		self._ks = data.get('ks', [])
		self._allow_stresses = data.get('sa', [])
		areas_object = self._doc.get_areas()
		for area_uid in data.get('areas', []):
			area = areas_object.get_area_item(area_uid)
			self._areas.add(area)
			area.add_change_handler(self.on_area_changed)


class Materials(ObservableObject):
	def __init__(self, doc):
		ObservableObject.__init__(self)
		self._materials = {}
		self._doc = doc
		self._material_counter = 1

	def create_material(self):
		mat = Material(self._doc)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, mat))
		self._materials[mat.uid] = mat
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, mat))
		mat.number = self._material_counter
		self._material_counter += 1
		mat.add_change_handler(self.on_material_changed)
		return mat

	def add_material(self, material_data):
		mat = Material.deserialize(material_data, self._doc)
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, mat))
		self._materials[mat.uid] = mat
		self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, mat))
		mat.number = self._material_counter
		self._material_counter += 1
		mat.add_change_handler(self.on_material_changed)

	def get_material(self, uid):
		return self._materials[uid]

	def get_materials(self):
		return self._materials.items()

	def on_material_changed(self, event):
		self.changed(event)

	def remove_material(self, material):
		self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, material))
		self._materials.pop(material.uid)
		self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, material))

	def remove_materials(self, materials):
		for material in materials:
			self.remove_material(material)

	def serialize_json(self):
		return {
			'materials': self._materials,
			'material_counter': self._material_counter
		}

	@staticmethod
	def deserialize(data, document):
		materials = Materials(document)
		if data is not None:
			materials.deserialize_data(data)
		return materials

	def deserialize_data(self, data):
		self._material_counter = data.get('material_counter', 0)
		counter = 1
		for material_data_tuple in data.get('materials', {}).items():
			material_data = material_data_tuple[1]
			material = Material.deserialize(material_data, self._doc)
			self._materials[material.uid] = material
			material.add_change_handler(self.on_material_changed)
			if self._material_counter == 0 or material.number == 0:
				material.number = counter
			counter += 1
		if self._material_counter == 0:
			self._material_counter = counter

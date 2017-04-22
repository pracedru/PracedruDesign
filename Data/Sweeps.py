from math import cos, pi

from math import sin

from Data.Areas import Area
from Data.Sketch import Edge
from Data.Events import ChangeEvent
from Data.Objects import ObservableObject
from Data.Vertex import Vertex

__author__ = 'mamj'


class SweepDefinition(ObservableObject):
    AreaSweep = 1
    LineSweep = 2

    def __init__(self, document):
        ObservableObject.__init__(self)
        self._doc = document
        self._geometry_elements = []
        self._meta_data_list = []
        self.name = 'New Sweep'
        self._type = SweepDefinition.AreaSweep
        self._sfak = 1.0
        self._ramp_dist = 0.0
        self._use_sfak = False
        self._ramp1 = False
        self._ramp2 = False

    def get_element_uids(self):
        elements_uids = []
        for element in self._geometry_elements:
            elements_uids.append(element.uid)
        return elements_uids

    def add_element(self, element):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, element))
        self._geometry_elements.append(element)
        self._meta_data_list.append([4, 0, 0])
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, element))
        element.add_change_handler(self.on_element_changed)

    def remove_element(self, element):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, element))
            self._geometry_elements.remove(element)
            self._meta_data_list.pop(index)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, element))
            element.remove_change_handler(self.on_element_changed)

    def remove_elements(self, elements):
        for element in elements:
            self.remove_element(element)

    def on_element_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if event.object in self._geometry_elements:
                self._geometry_elements.remove(event.object)
        self.changed(event)

    def get_divisions_of_element(self, element):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            return self._meta_data_list[index][0]
        return 0

    def set_divisions_of_element(self, element, value):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            self._meta_data_list[index][0] = value
            self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, element))

    def set_offset1_of_element(self, element, value):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            self._meta_data_list[index][1] = value
            self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, element))

    def set_offset2_of_element(self, element, value):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            self._meta_data_list[index][2] = value
            self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, element))

    def get_offset1_of_element(self, element):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            return self._meta_data_list[index][1]
        return 0

    def get_offset2_of_element(self, element):
        if element in self._geometry_elements:
            index = self._geometry_elements.index(element)
            return self._meta_data_list[index][2]
        return 0

    @property
    def ramp1(self):
        return self._ramp1

    @ramp1.setter
    def ramp1(self, value):
        self._ramp1 = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    @property
    def ramp2(self):
        return self._ramp2

    @ramp2.setter
    def ramp2(self, value):
        self._ramp2 = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    @property
    def use_sfak(self):
        return self._use_sfak

    def set_use_sfak(self, value):
        self._use_sfak = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    def get_elements(self):
        return self._geometry_elements

    @property
    def sfak(self):
        return self._sfak

    @sfak.setter
    def sfak(self, value):
        self._sfak = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    @property
    def ramp_distance(self):
        return self._ramp_dist

    @ramp_distance.setter
    def ramp_distance(self, value):
        self._ramp_dist = value
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    @property
    def length(self):
        return len(self._geometry_elements)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value != self._type:
            self._geometry_elements.clear()
            self.changed(ChangeEvent(self, ChangeEvent.Cleared, self))
        self._type = value

    def serialize_json(self):
        return {
            'type': self._type,
            'name': self.name,
            'sfak': self._sfak,
            'ramp': self._ramp_dist,
            'ramp1': self._ramp1,
            'ramp2': self._ramp2,
            'usesfak': self._use_sfak,
            'elements': self.get_element_uids(),
            'metadata': self._meta_data_list
        }

    @staticmethod
    def deserialize(data, document):
        sweep_item = SweepDefinition(document)
        if data is not None:
            sweep_item.deserialize_data(data)
        return sweep_item

    def deserialize_data(self, data):
        self._type = data['type']
        self.name = data.get('name', self.name)
        self._sfak = data.get('sfak', 1.0)
        self._ramp_dist = data.get('ramp', 0.0)
        self._ramp1 = bool(data.get('ramp1', False))
        self._ramp2 = bool(data.get('ramp2', False))
        self._use_sfak = bool(data.get('usesfak', False))
        areas_object = self._doc.get_areas()
        edges_object = self._doc.get_edges()
        first = True
        for element_uid in data.get('elements', []):
            element = areas_object.get_area_item(element_uid)
            if element is None:
                element = edges_object.get_edge(element_uid)
            if element is not None:
                self._geometry_elements.append(element)
                element.add_change_handler(self.on_element_changed)
        default_meta = []
        for i in range(len(self._geometry_elements)):
            default_meta.append([4, 0.0, 0.0])
        self._meta_data_list = data.get('metadata', default_meta)


class Sweeps(ObservableObject):
    def __init__(self, document):
        ObservableObject.__init__(self)
        self._doc = document
        self._sweeps_list = []
        self._sweep_lines = []

    def create_sweep_definition(self, type):
        sweep_item = SweepDefinition(self._doc)
        sweep_item.type = type
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, sweep_item))
        self._sweeps_list.append(sweep_item)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, sweep_item))
        sweep_item.add_change_handler(self.on_sweep_changed)
        return sweep_item

    def remove_sweep(self, sweep_item):
        if sweep_item in self._sweeps_list:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, sweep_item))
            self._sweeps_list.remove(sweep_item)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, sweep_item))
            sweep_item.remove_change_handler(self.on_sweep_changed)

    def remove_sweeps(self, sweep_items):
        for sweep_item in sweep_items:
            self.remove_sweep(sweep_item)

    def on_sweep_changed(self, event):
        self._sweep_lines.clear()
        self.changed(event)

    def get_sweep_definitions(self):
        return self._sweeps_list

    def move_sweep_up(self, sweep):
        index = self._sweeps_list.index(sweep)
        self._sweeps_list.insert(index-1, self._sweeps_list.pop(index))
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, sweep))

    def move_sweep_down(self, sweep):
        index = self._sweeps_list.index(sweep)
        self._sweeps_list.insert(index + 1, self._sweeps_list.pop(index))
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, sweep))

    def update_sweeps(self):
        self._sweep_lines.clear()
        part_counter = 0
        for sweep_def in self._sweeps_list:
            part_counter += 1
            if sweep_def.type == SweepDefinition.AreaSweep:
                areas = []
                edges = []
                for element in sweep_def.get_elements():
                    if type(element) is Area:
                        areas.append(element)
                    elif type(element) is Edge:
                        edges.append(element)
                counter = 0
                for edge in edges:
                    if edge.type == Edge.LineEdge:
                        divisions = sweep_def.get_divisions_of_element(edge)
                        os1 = sweep_def.get_offset1_of_element(edge)
                        os2 = sweep_def.get_offset2_of_element(edge)

                        div_length = (edge.length+os1+os2)/divisions
                        angle = edge.angle()
                        kps = edge.get_end_key_points()
                        for i in range(divisions):
                            x = kps[0].x + ((i + 0.5) * div_length - os1) * cos(angle)
                            y = kps[0].y + ((i + 0.5) * div_length - os1) * sin(angle)
                            kp = Vertex(x, y)

                            for area in areas:
                                if edge in area.get_edges():
                                    int_edges = area.get_intersecting_edges(kp, angle+pi/2)
                                    if len(int_edges) > 1:
                                        e1 = int_edges[0][0]
                                        e2 = int_edges[1][0]
                                        a1 = e1.angle(kp)
                                        a2 = e2.angle(kp)
                                        a_diff = a2 - a1
                                        #if a_diff < 0:
                                        #    a_diff += 2 * pi
                                        if 3 * pi / 2 > a_diff > pi / 2:
                                            a_diff -= pi
                                        if -3 * pi / 2 < a_diff < -pi / 2:
                                            a_diff += pi
                                        # if a_diff > pi:
                                        #    a_diff = 2*pi-a_diff

                                        int_edges = area.get_intersecting_edges(kp, (a1 + a_diff/2) + pi / 2)
                                        if len(int_edges) > 1:
                                            counter += 1
                                            meta = {}
                                            int_edges.append(meta)
                                            meta['name'] = sweep_def.name
                                            meta['path_no'] = counter
                                            meta['part_no'] = part_counter
                                            meta['use_sfak'] = sweep_def.use_sfak
                                            kps = edge.get_end_key_points()
                                            if sweep_def.ramp1 and sweep_def.ramp2:
                                                min_dist = min(kps[0].distance(kp), kps[1].distance(kp))
                                            elif sweep_def.ramp1:
                                                min_dist = kps[0].distance(kp)
                                            elif sweep_def.ramp2:
                                                min_dist = kps[1].distance(kp)
                                            else:
                                                min_dist = sweep_def.ramp_distance
                                            if min_dist < sweep_def.ramp_distance:
                                                meta['sfak'] = 1 + (sweep_def.sfak-1)*min_dist/sweep_def.ramp_distance
                                            else:
                                                meta['sfak'] = sweep_def.sfak
                                            meta['ramp_distance'] = sweep_def.ramp_distance
                                            self._sweep_lines.append(int_edges)

    def get_sweeps_lines(self):
        if len(self._sweep_lines) == 0:
            self.update_sweeps()
        return self._sweep_lines


    def serialize_json(self):
        return {
            'sweepsList': self._sweeps_list
        }

    @staticmethod
    def deserialize(data, document):
        sweeps = Sweeps(document)
        if data is not None:
            sweeps.deserialize_data(data)
        return sweeps

    def deserialize_data(self, data):
        for sweep_data in data.get('sweepsList', []):
            sweep_item = SweepDefinition.deserialize(sweep_data, self._doc)
            self._sweeps_list.append(sweep_item)
            sweep_item.add_change_handler(self.on_sweep_changed)
            # self.update_sweeps()

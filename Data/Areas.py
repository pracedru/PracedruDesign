from math import pi, cos, sin, tan

from Data.Sketch import Edge
from Data.Events import ChangeEvent
from Data.Objects import IdObject, ObservableObject
from Data.Point3d import KeyPoint
from Data.Vertex import Vertex

__author__ = 'mamj'


class Areas(ObservableObject):
    def __init__(self):
        ObservableObject.__init__(self)
        self._areas = {}
        self.naming_index = 1

    def create_area(self):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, None))
        area = Area()
        self._areas[area.uid] = area
        area.set_name("Area" + str(self.naming_index))
        self.naming_index += 1
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, area))
        area.add_change_handler(self.on_area_changed)
        return area

    def remove_area(self, area):
        if area.uid in self._areas:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, area))
            self._areas.pop(area.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, area))
            area.changed(ChangeEvent(self, ChangeEvent.Deleted, area))

    def remove_areas(self, areas):
        for area in areas:
            self.remove_area(area)

    def get_areas(self):
        return self._areas.items()

    def clear(self):
        self._areas.clear()
        self.naming_index = 1
        self.changed(ChangeEvent(self, ChangeEvent.Cleared, self))

    @property
    def length(self):
        return len(self._areas)

    def get_area_item(self, uid):
        if uid in self._areas:
            return self._areas[uid]
        return None

    def on_area_changed(self, event: ChangeEvent):
        if event.type == ChangeEvent.Deleted:
            self.remove_area(event.object)
        self.changed(event)


    @staticmethod
    def deserialize(data, doc):
        areas = Areas()
        areas.deserialize_data(data, doc)
        return areas

    def serialize_json(self):
        return \
            {
                'areas': self._areas,
                'naming_index': self.naming_index
            }

    def deserialize_data(self, data, doc):
        if data is not None:
            for area_data_tuple in data.get('areas', {}).items():
                area_data = area_data_tuple[1]
                area = Area.deserialize(area_data, doc)
                self._areas[area.uid] = area
                area.add_change_handler(self.on_area_changed)
            self.naming_index = data['naming_index']


class Area(IdObject, ObservableObject):
    def __init__(self):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._edges = []
        self._key_points = None
        self._name = "New Area"

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        self.changed(ChangeEvent(self, ChangeEvent.ValueChanged, self))

    def inside(self, point):
        # This is uncommented since arcs can go beyond the bounding box of all keypoints
        # top_left = Vertex()
        # bottom_right = Vertex()
        # first = True
        # for edge in self._edges:
        #     for kp in edge.get_end_key_points():
        #         if first:
        #             first = False
        #             top_left.x = kp.x
        #             bottom_right.x = kp.x
        #             top_left.y = kp.y
        #             bottom_right.y = kp.y
        #         else:
        #             if kp.x < top_left.x:
        #                 top_left.x = kp.x
        #             if kp.x > bottom_right.x:
        #                 bottom_right.x = kp.x
        #             if kp.y > top_left.y:
        #                 top_left.y = kp.y
        #             if kp.y < bottom_right.y:
        #                 bottom_right.y = kp.y
        # if bottom_right.x > point.x > top_left.x:
        #     if top_left.y > point.y > bottom_right.y:
        anglesum = 0.0
        last_point = None
        for pnt in self.get_inside_key_points():
            if last_point is not None:
                angle = point.angle_between(last_point, pnt)
                if angle > pi:
                    angle = -(2*pi-angle)
                anglesum += angle
            last_point = pnt
        if abs(anglesum) > pi:
            return True
        return False

    def get_intersecting_edges(self, kp, gamma):
        intersecting_edges = []
        for edge in self._edges:
            if edge.type is Edge.LineEdge:
                kps = edge.get_end_key_points()
                x1 = kps[0].x
                y1 = kps[0].y
                x2 = kps[1].x
                y2 = kps[1].y
                x3 = kp.x
                y3 = kp.y
                x4 = kp.x + cos(gamma)
                y4 = kp.y + sin(gamma)
                denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
                if denom != 0:
                    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
                    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
                    int_kp = Vertex(px, py)
                    if edge.distance(int_kp) < 0.001:
                        intersecting_edges.append([edge, int_kp])
            elif edge.type is Edge.ArcEdge:
                center_kp = edge.get_key_points()[0]
                radius = edge.get_meta_data('r')
                sa = edge.get_meta_data('sa')
                ea = edge.get_meta_data('ea')
                alpha = kp.angle2d(center_kp)
                dist = kp.distance(center_kp)
                beta = alpha-gamma
                rad_ray_dist = sin(beta)*dist
                if rad_ray_dist < radius:
                    omega = center_kp.angle2d(kp)
                    int_kp = Vertex(center_kp.x + cos(omega)*radius, center_kp.y + sin(omega)*radius)
                    if edge.distance(int_kp) < 0.001:
                        intersecting_edges.append([edge, int_kp])

        return intersecting_edges

    def insert_edge(self, edge):
        kps = edge.get_end_key_points()
        index = -1
        if kps[0] in self.get_key_points():
            index = self._key_points.index(kps[0])
        if index != -1:
            self._edges.insert(index, edge)
        else:
            self._edges.append(edge)
        edge.add_change_handler(self.on_edge_changed)
        self._key_points = None

    def add_edge(self, edge):
        self._edges.append(edge)
        edge.add_change_handler(self.on_edge_changed)
        self._key_points = None

    def on_edge_changed(self, event: ChangeEvent):
        if event.type == ChangeEvent.Deleted:
            if type(event.object) is Edge:
                if event.object.type != Edge.FilletLineEdge:
                    self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))
                else:
                    fillet_edge = event.object
                    self._edges.remove(fillet_edge)
                    fillet_edge.remove_change_handler(self.on_edge_changed)
                    self._key_points = None
            if type(event.object) is KeyPoint:
                self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def get_key_points(self):
        if self._key_points is None:
            self._key_points = []
            this_kp = self._edges[0].get_end_key_points()[0]
            next_kp = self._edges[0].get_end_key_points()[1]
            if this_kp == self._edges[1].get_end_key_points()[0] or this_kp == self._edges[1].get_end_key_points()[1]:
                this_kp = self._edges[0].get_end_key_points()[1]
                next_kp = self._edges[0].get_end_key_points()[0]
            self._key_points.append(this_kp)
            self._key_points.append(next_kp)
            for i in range(1, len(self._edges)):
                edge = self._edges[i]
                if edge.type != Edge.FilletLineEdge:
                    if next_kp == edge.get_end_key_points()[0]:
                        next_kp = edge.get_end_key_points()[1]
                    else:
                        next_kp = edge.get_end_key_points()[0]
                    self._key_points.append(next_kp)
        return self._key_points

    def get_inside_key_points(self):
        key_points = []
        this_kp = self._edges[0].get_end_key_points()[0]
        next_kp = self._edges[0].get_end_key_points()[1]
        if this_kp == self._edges[1].get_end_key_points()[0] or this_kp == self._edges[1].get_end_key_points()[1]:
            this_kp = self._edges[0].get_end_key_points()[1]
            next_kp = self._edges[0].get_end_key_points()[0]
        key_points.append(this_kp)
        if self._edges[0].type == Edge.ArcEdge:
            ckp = self._edges[0].get_key_points()[0]
            sa = self._edges[0].get_meta_data('sa')
            ea = self._edges[0].get_meta_data('ea')
            r = self._edges[0].get_meta_data('r')
            diff = ea - sa
            if diff < 0:
                diff += 2 * pi
            ma = sa + diff / 2
            key_points.append(Vertex(ckp.x + cos(ma) * r, ckp.y + sin(ma) * r))
        key_points.append(next_kp)
        for i in range(1, len(self._edges)):
            edge = self._edges[i]
            if edge.type != Edge.FilletLineEdge:
                if edge.type == Edge.ArcEdge:
                    ckp = edge.get_key_points()[0]
                    sa = edge.get_meta_data('sa')
                    ea = edge.get_meta_data('ea')
                    r = edge.get_meta_data('r')
                    diff = ea-sa
                    if diff < 0:
                        diff += 2 * pi
                    ma = sa + diff / 2
                    key_points.append(Vertex(ckp.x + cos(ma) * r, ckp.y + sin(ma) * r))
                if next_kp == edge.get_end_key_points()[0]:
                    next_kp = edge.get_end_key_points()[1]
                else:
                    next_kp = edge.get_end_key_points()[0]
                key_points.append(next_kp)
        return key_points

    def get_edges(self):
        return self._edges

    def get_edge_uids(self):
        edge_uids = []
        for edge in self._edges:
            edge_uids.append(edge.uid)
        return edge_uids

    @staticmethod
    def deserialize(data, doc):
        area = Area()
        area.deserialize_data(data, doc)
        return area

    def serialize_json(self):
        return \
            {
                'uid': IdObject.serialize_json(self),
                'edges': self.get_edge_uids(),
                'name': self.name
            }

    def deserialize_data(self, data, doc):
        IdObject.deserialize_data(self, data['uid'])
        edges_object = doc.get_edges()
        for edge_uid in data['edges']:
            edge = edges_object.get_edge(edge_uid)
            self._edges.append(edge)
            edge.add_change_handler(self.on_edge_changed)
        self._name = data['name']


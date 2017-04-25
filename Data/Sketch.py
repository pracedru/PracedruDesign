from math import pi, sin, cos, tan
#from Data import Document
from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Geometry import Geometry
from Data.Objects import IdObject, ObservableObject
from Data.Parameters import Parameters
from Data.Point3d import KeyPoint
from Data.Vertex import Vertex

__author__ = 'mamj'


class Sketch(Geometry):
    def __init__(self, params_parent):
        Geometry.__init__(self, params_parent, "New Sketch", Geometry.Sketch)
        self._key_points = {}
        self._edges = {}
        self._texts = {}
        self.threshold = 0.1
        self.edge_naming_index = 1

    def add_edge(self, edge):
        self._edges[edge.uid] = edge

    def clear(self):
        self._key_points.clear()
        self._edges.clear()
        self.edge_naming_index = 1
        self.changed(ChangeEvent(self, ChangeEvent.Cleared, self))

    def get_limits(self):
        limits = [1.0e16, 1.0e16, -1.0e16, -1.0e16]
        for pnt in self._key_points.values():
            limits[0] = min(pnt.x, limits[0])
            limits[1] = min(pnt.y, limits[1])
            limits[2] = max(pnt.x, limits[2])
            limits[3] = max(pnt.y, limits[3])
        return limits

    # def get_edges_from_key_point(self, kp):
    #     edges = []
    #     for edge_tuple in self._edges.items():
    #         edge = edge_tuple[1]
    #         if kp in edge.get_end_key_points():
    #             edges.append(edge)
    #     return edges

    @property
    def key_point_count(self):
        return len(self._key_points)

    @property
    def edges_count(self):
        return len(self._edges)

    def get_edge(self, uid):
        if uid in self._edges:
            return self._edges[uid]
        else:
            return None

    def get_key_point(self, uid):
        try:
            return self._key_points[uid]
        except KeyError:
            return KeyPoint(self)

    def get_fillet(self, uid):
        if uid in self._fillets:
            return self._fillets[uid]
        else:
            return None

    def get_parent(self):
        return self._parent

    def get_next_edge_naming_index(self):
        self.edge_naming_index += 1
        return self.edge_naming_index - 1

    def remove_edge(self, edge):
        if edge.uid in self._edges:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, edge))
            self._edges.pop(edge.uid)
            edge.changed(ChangeEvent(self, ChangeEvent.Deleted, edge))
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, edge))

    def remove_edges(self, edges):
        for edge in edges:
            self.remove_edge(edge)

    def remove_key_points(self, key_points):
        for kp in key_points:
            if kp.uid in self._key_points:
                kp.changed(ChangeEvent(self, ChangeEvent.Deleted, kp))
                self._key_points.pop(kp.uid)

    def create_key_point(self, x, y, z, ts=None):
        key_point = None
        for p_tuple in self._key_points.items():
            p = p_tuple[1]
            if ts is None:
                ts = self.threshold
            if abs(p.x - x) < ts and abs(p.y - y) < ts and abs(p.z - z) < ts:
                key_point = p
                break
        if key_point is None:
            key_point = KeyPoint(self, x, y, z)
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, key_point))
            self._key_points[key_point.uid] = key_point
            self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, key_point))
            key_point.add_change_handler(self.on_kp_changed)
        return key_point

    def create_fillet_edge(self, kp):
        fillet_edge = None
        if kp.uid in self._key_points:
            fillet_edge = Edge(self, Edge.FilletLineEdge)
            fillet_edge.set_name("Edge" + str(self.edge_naming_index))
            fillet_edge.add_key_point(kp)
            self.edge_naming_index += 1
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, fillet_edge))
            self._edges[fillet_edge.uid] = fillet_edge
            self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, fillet_edge))
            fillet_edge.add_change_handler(self.on_edge_changed)
        return fillet_edge

    def create_text(self, key_point, value, height):
        text = Text(self, key_point, value, height)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, text))
        self._texts[text.uid] = text
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, text))
        text.add_change_handler(self.on_text_changed)
        return text

    def create_line_edge(self, key_point1, key_point2):
        line_edge = Edge(self, Edge.LineEdge)
        line_edge.set_name("Edge" + str(self.edge_naming_index))
        self.edge_naming_index += 1
        line_edge.add_key_point(key_point1)
        line_edge.add_key_point(key_point2)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, line_edge))
        self._edges[line_edge.uid] = line_edge
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, line_edge))
        line_edge.add_change_handler(self.on_edge_changed)
        return line_edge

    def create_arc_edge(self, center_key_point, start_angle, end_angle, radius):
        arc_edge = Edge(self, Edge.ArcEdge)
        arc_edge.set_name("Edge" + str(self.edge_naming_index))
        self.edge_naming_index += 1
        arc_edge.add_key_point(center_key_point)
        arc_edge.set_meta_data("sa", start_angle)
        arc_edge.set_meta_data("ea", end_angle)
        arc_edge.set_meta_data("r", radius)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, arc_edge))
        self._edges[arc_edge.uid] = arc_edge
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, arc_edge))
        arc_edge.add_change_handler(self.on_edge_changed)
        return arc_edge

    def get_edges(self):
        return self._edges.items()

    def get_key_points(self):
        return self._key_points.items()

    def get_texts(self):
        return self._texts.items()

    def on_kp_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def on_text_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def on_edge_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if event.object.uid in self._edges:
                self._edges.pop(event.object.uid)
            event.object.remove_change_handler(self.on_edge_changed)

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'parameters': Parameters.serialize_json(self),
            'key_points': self._key_points,
            'edges': self._edges,
            'texts': self._texts,
            'threshold': self.threshold,
            'edge_naming_index': self.edge_naming_index,
            'type': self._geometry_type
        }

    @staticmethod
    def deserialize(data, param_parent):
        sketch = Sketch(param_parent)
        if data is not None:
            sketch.deserialize_data(data)
        return sketch

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        Parameters.deserialize_data(self, data['parameters'])
        self.threshold = data.get('threshold', 0.1)
        self.edge_naming_index = data.get('edge_naming_index', 0)
        for kp_data_tuple in data.get('key_points', {}).items():
            kp_data = kp_data_tuple[1]
            kp = KeyPoint.deserialize(kp_data, self)
            self._key_points[kp.uid] = kp
            kp.add_change_handler(self.on_kp_changed)
        for edge_data_tuple in data.get('edges', {}).items():
            edge_data = edge_data_tuple[1]
            edge = Edge.deserialize(self, edge_data)
            self._edges[edge.uid] = edge
            edge.add_change_handler(self.on_edge_changed)
        for text_data_tuple in data.get('texts', {}).items():
            text_data = text_data_tuple[1]
            text = Text.deserialize(self, text_data)
            self._texts[text.uid] = text
            text.add_change_handler(self.on_text_changed)

        if self.edge_naming_index == 0:
            for edge_tuple in self._edges.items():
                edge = edge_tuple[1]
                if "Edge" in edge.name:
                    try:
                        index = int(edge.name.replace("Edge", ""))
                        self.edge_naming_index = max(self.edge_naming_index, index)
                    except ValueError:
                        pass
            self.edge_naming_index += 1


class Text(IdObject, ObservableObject):
    Bottom = 0
    Top = 1
    Center = 2
    Left = 0
    Right = 1

    def __init__(self, sketch, key_point=None, value="", height=0.01, angle=0, vertical_alignment=Center, horizontal_alignment=Center):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._sketch = sketch
        self._vertical_alignment = vertical_alignment
        self._horizontal_alignment = horizontal_alignment
        self._value = value
        self._height = height
        self._angle = angle
        self._key_point = key_point

    @property
    def name(self):
        return self._value

    @property
    def key_point(self):
        return self._key_point

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        old_value = self._value
        self._value = value
        self.changed(ValueChangeEvent(self, 'value', old_value, value))

    @property
    def vertical_alignment(self):
        return self._vertical_alignment

    @property
    def horizontal_alignment(self):
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, value):
        self._horizontal_alignment = value
        self.changed(ValueChangeEvent(self, 'horizontal_alignment', 0, value))

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        old_value = self._height
        self._height = value
        self.changed(ValueChangeEvent(self, 'height', old_value, value))

    @property
    def angle(self):
        return self._angle

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'kp': self._key_point.uid,
            'value': self._value,
            'height': self._height,
            'angle': self._angle,
            'valign': self._vertical_alignment,
            'halign': self._horizontal_alignment
        }

    @staticmethod
    def deserialize(sketch, data):
        text = Text(sketch)
        if data is not None:
            text.deserialize_data(data)
        return text

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        self._key_point = self._sketch.get_key_point(data['kp'])
        self._value = data['value']
        self._height = data['height']
        self._angle = data['angle']
        self._vertical_alignment = data['valign']
        self._horizontal_alignment = data['halign']


class Attribute(Text):
    def __init__(self, name, default_value):
        Text.__init__(default_value)
        self._name = name

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def serialize_json(self):
        return {
            'text': Text.serialize_json(self),
            'name': self._name,
        }

    @staticmethod
    def deserialize(data, param_parent):
        text = Text(param_parent)
        if data is not None:
            text.deserialize_data(data)
        return text

    def deserialize_data(self, data):
        Text.deserialize_data(self, data['text'])
        self._name = data['name']


class Edge(IdObject, ObservableObject):
    LineEdge = 1
    ArcEdge = 2
    EllipseEdge = 3
    PolyLineEdge = 4
    FilletLineEdge = 5
    CircleEdge = 3

    def __init__(self, sketch, type=LineEdge):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._type = type
        self._sketch = sketch
        self._key_points = []
        self._meta_data = {}
        self._meta_data_parameters = {}
        self._name = "New Edge"

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def set_meta_data(self, name, value):
        self._meta_data[name] = value

    def get_meta_data(self, name):
        return self._meta_data[name]

    def get_meta_data_parameter(self, name):
        doc = self._sketch.get_document()
        for param_tuple in self._meta_data_parameters.items():
            if param_tuple[1] == name:
                return doc.get_parameters().get_parameter_by_uid(param_tuple[0])
        return None

    def set_meta_data_parameter(self, name, parameter):
        self._meta_data_parameters[parameter.uid] = name
        doc = self._sketch.get_document()
        param = doc.get_parameters().get_parameter_by_uid(parameter.uid)
        self._meta_data[name] = param.value
        param.add_change_handler(self.on_parameter_change)

    def on_parameter_change(self, event):
        param = event.sender
        uid = param.uid
        meta_name = self._meta_data_parameters[uid]
        self._meta_data[meta_name] = param.value

    def get_key_points(self):
        kps = []
        for uid in self._key_points:
            kps.append(self._sketch.get_key_point(uid))
        return kps

    def get_key_point_uids(self):
        kps = []
        for uid in self._key_points:
            kps.append(uid)
        return kps

    def get_end_key_points(self):
        if self._type == Edge.LineEdge:
            return self.get_key_points()
        elif self._type == Edge.ArcEdge:
            ckp = self._sketch.get_key_point(self._key_points[0])
            if 'start_kp' in self._meta_data:
                start_kp = self._sketch.get_key_point(self._meta_data['start_kp'])
            else:
                x = ckp.x + cos(self._meta_data['sa'])*self._meta_data['r']
                y = ckp.y + sin(self._meta_data['sa'])*self._meta_data['r']
                start_kp = self._sketch.create_key_point(x, y, 0)
                start_kp.add_edge(self)
                self._meta_data['start_kp'] = start_kp.uid
            if 'end_kp' in self._meta_data:
                end_kp = self._sketch.get_key_point(self._meta_data['end_kp'])
            else:
                x = ckp.x + cos(self._meta_data['ea'])*self._meta_data['r']
                y = ckp.y + sin(self._meta_data['ea'])*self._meta_data['r']
                end_kp = self._sketch.create_key_point(x, y, 0)
                end_kp.add_edge(self)
                self._meta_data['end_kp'] = end_kp.uid
            return [start_kp, end_kp]
        elif self.type == Edge.PolyLineEdge:
            return self.get_key_points()
        elif self.type == Edge.FilletLineEdge:
            return self.get_key_points()

    def get_other_kp(self, kp):
        kps = self.get_end_key_points()
        if len(kps) > 1:
            if kps[0] == kp:
                return kps[1]
            else:
                return kps[0]
        else:
            return None

    def add_key_point(self, key_point):
        self._key_points.append(key_point.uid)
        key_point.add_change_handler(self.on_key_point_changed)
        key_point.add_edge(self)

    def on_key_point_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            event.object.remove_edge(self)
            self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))
            event.object.remove_change_handler(self.on_key_point_changed)
        self.changed(event)

    def distance(self, point):
        kps = self.get_key_points()
        if self.type == Edge.LineEdge:
            kp1 = kps[0]
            kp2 = kps[1]
            alpha1 = kp1.angle_between(kp2, point)
            alpha2 = kp2.angle_between(kp1, point)
            if alpha1 > pi:
                alpha1 = 2 * pi - alpha1
            if alpha2 > pi:
                alpha2 = 2 * pi - alpha2
            if alpha1 < pi/2 and alpha2 < pi/2:
                distance = kp1.distance(point)*sin(alpha1)
                return distance
            else:
                return min(kp1.distance(point), kp2.distance(point))
        elif self.type == Edge.ArcEdge:
            center = kps[0]
            radius = self._meta_data['r']
            sa = self._meta_data['sa']
            ea = self._meta_data['ea']
            diff = ea - sa
            if diff < 0:
                diff += 2 * pi
            angle = center.angle2d(point)
            diff2 = angle - sa
            if diff2 < 0:
                diff2 += 2 * pi
            if diff2 > diff:
                ekp = self.get_end_key_points()
                dist = min(ekp[0].distance(point), ekp[1].distance(point))
            else:
                dist = abs(center.distance(point)-radius)
            return dist
        elif self.type == Edge.FilletLineEdge:
            kp = kps[0]
            radius = self._meta_data['r']
            edges = kp.get_edges()
            edges.remove(self)
            draw_data = self.get_draw_data()
            rect = draw_data['rect']
            center = Vertex(rect[0]+rect[2]/2, rect[1]+rect[3]/2)
            dist = abs(center.distance(point) - radius)
            return dist

    def get_draw_data(self):
        edge_data = {}

        key_points = self.get_key_points()
        if self.type == Edge.LineEdge:
            edges_list = key_points[0].get_edges()
            fillet1 = None
            other_edge1 = None
            for edge_item in edges_list:
                if edge_item.type == Edge.FilletLineEdge:
                    fillet1 = edge_item
                elif edge_item is not self:
                    other_edge1 = edge_item
            edges_list = key_points[1].get_edges()
            fillet2 = None
            other_edge2 = None
            for edge_item in edges_list:
                if edge_item.type == Edge.FilletLineEdge:
                    fillet2 = edge_item
                elif edge_item is not self:
                    other_edge2 = edge_item
            fillet_offset_x = 0
            fillet_offset_y = 0

            if fillet1 is not None and other_edge1 is not None:
                r = fillet1.get_meta_data("r")
                a1 = self.angle(key_points[0])
                kp1 = self.get_other_kp(key_points[0])
                kp2 = other_edge1.get_other_kp(key_points[0])
                abtw = key_points[0].angle_between_positive_minimized(kp1, kp2)
                dist = -tan(abtw/2+pi/2)*r
                fillet_offset_x = dist * cos(a1)
                fillet_offset_y = dist * sin(a1)

            x1 = key_points[0].x + fillet_offset_x
            y1 = key_points[0].y + fillet_offset_y

            fillet_offset_x = 0
            fillet_offset_y = 0

            if fillet2 is not None and other_edge2 is not None:
                r = fillet2.get_meta_data("r")
                a1 = self.angle(key_points[1])
                kp1 = self.get_other_kp(key_points[1])
                kp2 = other_edge2.get_other_kp(key_points[1])
                abtw = key_points[1].angle_between_positive_minimized(kp2, kp1)
                dist = -tan(abtw / 2+pi/2) * r
                fillet_offset_x = dist * cos(a1)
                fillet_offset_y = dist * sin(a1)

            x2 = key_points[1].x + fillet_offset_x
            y2 = key_points[1].y + fillet_offset_y
            edge_data["type"] = 1
            edge_data["coords"] = [Vertex(x1, y1), Vertex(x2, y2)]
        elif self.type == Edge.ArcEdge:
            cx = key_points[0].x
            cy = key_points[0].y
            radius = self.get_meta_data("r")
            rect = [cx - radius, cy - 1 * radius, radius * 2, radius * 2]
            start_angle = self.get_meta_data("sa") * 180 * 16 / pi
            end_angle = self.get_meta_data("ea") * 180 * 16 / pi
            span = end_angle - start_angle
            if span < 0:
                span += 2 * 180 * 16
            edge_data["type"] = 2
            edge_data["rect"] = rect
            edge_data["sa"] = start_angle
            edge_data["span"] = span
        elif self.type == Edge.FilletLineEdge:
            kp = key_points[0]
            edges_list = kp.get_edges()
            edges_list.remove(self)
            if len(edges_list) > 1:
                edge1 = edges_list[0]
                edge2 = edges_list[1]
                kp1 = edge1.get_other_kp(kp)
                kp2 = edge2.get_other_kp(kp)
                angle_between = kp.angle_between_untouched(kp1, kp2)
                radius = self.get_meta_data("r")
                dist = radius / sin(angle_between/2)
                angle_larger = False
                while angle_between < -2*pi:
                    angle_between += 2*pi
                while angle_between > 2*pi:
                    angle_between -= 2*pi
                if abs(angle_between) > pi:
                    angle_larger = True
                    angle = edge1.angle(kp) + angle_between / 2 + pi
                else:
                    angle = edge1.angle(kp) + angle_between / 2
                if dist < 0:
                    angle += pi
                cx = key_points[0].x + dist * cos(angle)
                cy = key_points[0].y + dist * sin(angle)
                rect = [cx - radius, cy - radius, radius * 2, radius * 2]

                if angle_between < 0:
                    if angle_larger:
                        end_angle = (edge1.angle(kp) - pi/2) * 180 * 16 / pi
                        start_angle = (edge2.angle(kp) + pi/2) * 180 * 16 / pi
                    else:
                        end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
                        start_angle = (edge2.angle(kp) + 3*pi / 2) * 180 * 16 / pi
                else:
                    if angle_larger:
                        start_angle = (edge1.angle(kp) + pi/2) * 180 * 16 / pi
                        end_angle = (edge2.angle(kp) - pi/2) * 180 * 16 / pi
                    else:
                        end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
                        start_angle = (edge2.angle(kp) - pi / 2) * 180 * 16 / pi
                        end_angle += pi * 180 * 16 / pi
                        start_angle += pi * 180 * 16 / pi
                span = end_angle-start_angle
                edge_data["type"] = 2
                edge_data["rect"] = rect
                edge_data["sa"] = start_angle
                edge_data["span"] = span
        return edge_data

    def angle(self, kp=None):
        kps = self.get_end_key_points()
        if self.type == Edge.LineEdge:
            if kp is None:
                return kps[0].angle2d(kps[1])
            else:
                if kp == kps[0]:
                    return kps[0].angle2d(kps[1])
                elif kp == kps[1]:
                    return kps[1].angle2d(kps[0])
                else:
                    return kps[0].angle2d(kps[1])
        if self.type == Edge.ArcEdge:
            if kp is None:
                return self._meta_data['sa'] - pi/2
            else:
                if kp == kps[0]:
                    return self._meta_data['sa'] - pi/2
                elif kp == kps[1]:
                    return self._meta_data['ea'] - pi/2
                else:
                    center_kp = self.get_key_points()[0]
                    return center_kp.angle2d(kp) + pi/2

    @property
    def length(self):
        if self.type == Edge.LineEdge:
            kps = self.get_end_key_points()
            return kps[0].distance(kps[1])
        elif self.type == Edge.ArcEdge:
            sa = self._meta_data['sa']
            ea = self._meta_data['ea']
            r = self._meta_data['r']
            diff = ea - sa
            if diff > 2*pi:
                diff -= 2*pi
            if diff < -2*pi:
                diff += 2*pi
            return abs(diff*r)

    def coincident(self, key_point, coin_thress=None):
        kps = self.get_key_points()
        if coin_thress is None:
            threshold = self._sketch.threshold
        else:
            threshold = coin_thress
        if self.type == Edge.LineEdge:
            kp1 = kps[0]
            kp2 = kps[1]
            alpha1 = kp1.angle_between(kp2, key_point)
            alpha2 = kp2.angle_between(kp1, key_point)
            if alpha1 > pi:
                alpha1 = 2 * pi - alpha1
            if alpha2 > pi:
                alpha2 = 2 * pi - alpha2
            if alpha1 < pi/2 and alpha2 < pi/2:
                distance = kp1.distance(key_point)*sin(alpha1)
                if distance < threshold:
                    return True

        return False

    def split(self, key_point):
        kps = self.get_key_points()
        second_key_point = kps[1]
        second_key_point.remove_change_handler(self.on_key_point_changed)
        self._key_points.remove(second_key_point.uid)
        self._key_points.append(key_point.uid)
        key_point.add_change_handler(self.on_key_point_changed)
        new_edge = self._sketch.create_line_edge(key_point, second_key_point)
        return new_edge

    @property
    def type(self):
        return self._type

    @staticmethod
    def deserialize(sketch, data):
        edge = Edge(sketch)
        if data is not None:
            edge.deserialize_data(data)
        return edge

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'name': self._name,
            'type': self._type,
            'key_points': self._key_points,
            'meta_data': self._meta_data,
            'meta_data_parameters': self._meta_data_parameters
        }

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        self._type = data['type']
        self._name = data.get('name', "Edge")
        self._key_points = data['key_points']
        for kp_uid in self._key_points:
            kp = self._sketch.get_key_point(kp_uid)
            kp.add_change_handler(self.on_key_point_changed)
            kp.add_edge(self)
        self._meta_data = data.get('meta_data')
        self._meta_data_parameters = data.get('meta_data_parameters')
        for parameter_uid in self._meta_data_parameters:
            param = self._sketch.get_parameter_by_uid(parameter_uid)
            if param is not None:
                param.add_change_handler(self.on_parameter_change)
            else:
                i = 20
                # self._meta_data_parameters.pop(parameter_uid)

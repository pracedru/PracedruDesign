from math import *

import numpy as np

from Data.Edges import Edge
from Data.Events import ChangeEvent
from Data.Geometry import Geometry
from Data.Objects import IdObject, NamedObservableObject, ObservableObject
from Data.Parameters import Parameters
from Data.Point3d import KeyPoint
from Data.Vertex import Vertex


class Part(Geometry):
    def __init__(self, parameters_parent, document, name="New part"):
        Geometry.__init__(self, parameters_parent, name, Geometry.Part)
        self._doc = document
        self._plane_features = {}
        self._sketch_features = {}
        self._extrude_features = {}
        self._feature_progression = []
        self._limits = None # [Vertex(-1, -1, -1), Vertex(1, 1, 1)]
        self._update_needed = True
        self._key_points = {}
        self._edges = {}
        self._surfaces = {}

    def get_document(self):
        return self._doc

    @property
    def update_needed(self):
        return self._update_needed

    def get_key_points(self):
        return self._key_points.items()

    def get_key_point(self, uid):
        try:
            return self._key_points[uid]
        except KeyError:
            return KeyPoint(self)

    def get_surfaces(self):
        surfaces = []
        for surface_tuple in self._surfaces.items():
            surfaces.append(surface_tuple[1])
        return surfaces

    def _add_feature(self, feature):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, feature))
        self._feature_progression.append(feature)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, feature))

    def create_plane_feature(self, name, position, x_direction, y_direction):
        plane_feature = Feature(self._doc, self, PlaneFeature, name)
        plane_feature.add_vertex('p', position)
        plane_feature.add_vertex('xd', x_direction)
        plane_feature.add_vertex('yd', y_direction)
        self._plane_features[plane_feature.uid] = plane_feature
        self._add_feature(plane_feature)
        plane_feature.add_change_handler(self.on_plane_feature_changed)
        return plane_feature

    def create_sketch_feature(self, sketch, plane_feature):
        sketch_feature = Feature(self._doc, self, SketchFeature, sketch.name)
        sketch_feature.add_feature(plane_feature)
        sketch_feature.add_object(sketch)
        self._sketch_features[sketch_feature.uid] = sketch_feature
        self._add_feature(sketch_feature)
        sketch_feature.add_change_handler(self.on_sketch_feature_changed)
        self._cal_limits()
        return sketch_feature

    def create_extrude_feature(self, name, sketch_feature, area, length):
        extrude_feature = Feature(self._doc, self, ExtrudeFeature, name)
        extrude_feature.add_feature(sketch_feature)
        extrude_feature.add_object(area)
        extrude_feature.add_vertex('ex_ls', Vertex(length[0], length[1]))
        self._extrude_features[extrude_feature.uid] = extrude_feature
        self._add_feature(extrude_feature)
        extrude_feature.add_change_handler(self.on_extrude_feature_changed)
        self._update_needed = True
        self._cal_limits()

    def get_create_key_point(self, x, y, z):
        key_point = None
        for p_tuple in self._key_points.items():
            p = p_tuple[1]
            ts = 0.00001
            if abs(p.x - x) <= ts and abs(p.y - y) <= ts and abs(p.z - z) <= ts:
                key_point = p
                break
        if key_point is None:
            key_point = KeyPoint(self, x, y, z)
            self._key_points[key_point.uid] = key_point
            key_point.add_change_handler(self.on_key_point_changed)
        return key_point

    def on_key_point_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if event.sender.uid in self._key_points:
                self._key_points.pop(event.sender.uid)

    def on_edge_changed(self, event):
        if event.type == ChangeEvent.Deleted:
            if event.sender.uid in self._edges:
                self._edges.pop(event.sender.uid)

    def create_line_edge(self, key_point1, key_point2):
        line_edge = Edge(self, Edge.LineEdge)
        line_edge.name = "Edge"
        line_edge.add_key_point(key_point1)
        line_edge.add_key_point(key_point2)
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, line_edge))
        self._edges[line_edge.uid] = line_edge
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, line_edge))
        line_edge.add_change_handler(self.on_edge_changed)
        return line_edge

    def update_geometry(self):
        oldkps = []
        for kp_tuple in self._key_points.items():
            oldkps.append(kp_tuple[1])
        for kp in oldkps:
            kp.delete()
        self._surfaces.clear()
        for feature in self._feature_progression:
            if feature.feature_type == ExtrudeFeature:
                extrusion_lengths = feature.get_vertex('ex_ls')
                sketch_feature = feature.get_features()[0]
                plane_feature = sketch_feature.get_features()[0]
                p = plane_feature.get_vertex('p')
                xd = plane_feature.get_vertex('xd')
                yd = plane_feature.get_vertex('yd')
                cp = np.cross(xd.xyz, yd.xyz)
                n = cp / np.linalg.norm(cp)
                pm = np.array([xd.xyz, yd.xyz, n])
                sketch = sketch_feature.get_objects()[0]
                area = feature.get_objects()[0]
                p1 = p.xyz + n * extrusion_lengths.x
                p2 = p.xyz + n * extrusion_lengths.y
                front_edges = []
                back_edges = []
                for edge in area.get_edges():
                    draw_data = edge.get_draw_data()
                    if edge.type == Edge.LineEdge:
                        c = draw_data['coords']
                        c1 = p1 + pm.dot(c[0].xyz)
                        c2 = p1 + pm.dot(c[1].xyz)
                        kp1 = self.get_create_key_point(c1[0], c1[1], c1[2])
                        kp2 = self.get_create_key_point(c2[0], c2[1], c2[2])
                        edge1 = self.create_line_edge(kp1, kp2)
                        front_edges.append(edge1)
                        c1 = p2 + pm.dot(c[0].xyz)
                        c2 = p2 + pm.dot(c[1].xyz)
                        kp3 = self.get_create_key_point(c1[0], c1[1], c1[2])
                        kp4 = self.get_create_key_point(c2[0], c2[1], c2[2])
                        edge2 = self.create_line_edge(kp3, kp4)
                        back_edges.append(edge2)
                        edge3 = self.create_line_edge(kp1, kp3)
                        edge4 = self.create_line_edge(kp2, kp4)
                        surface = Surface()
                        surface.set_main_edges([edge1, edge2, edge3, edge4])
                        self._surfaces[surface.uid] = surface
                surface = Surface()
                surface.set_main_edges(front_edges)
                self._surfaces[surface.uid] = surface
                surface = Surface()
                surface.set_main_edges(back_edges)
                self._surfaces[surface.uid] = surface
        self._update_needed = False

    def get_feature(self, uid):
        if uid in self._plane_features:
            return self._plane_features[uid]
        if uid in self._sketch_features:
            return self._sketch_features[uid]
        if uid in self._extrude_features:
            return self._extrude_features[uid]
        return None

    def get_planes(self):
        planes = []
        for feature in self._plane_features.items():
            planes.append(feature[1])
        return planes

    @property
    def get_features(self):
        features = []
        for feature_tuple in self._plane_features.items():
            features.append(feature_tuple[1])
        for feature_tuple in self._sketch_features.items():
            features.append(feature_tuple[1])
        for feature_tuple in self._extrude_features.items():
            features.append(feature_tuple[1])
        return features

    def get_sketch_features(self):
        features = []
        for feature_tuple in self._sketch_features.items():
            features.append(feature_tuple[1])
        return features

    def _cal_limits(self):
        limits = [Vertex(-1, -1, -1), Vertex(1, 1, 1)]
        lines = self.get_lines()
        for line in lines:
            limits[0].x = min(limits[0].x, line[0])
            limits[0].y = min(limits[0].y, line[1])
            limits[0].z = min(limits[0].z, line[2])
            limits[1].x = max(limits[1].x, line[0])
            limits[1].y = max(limits[1].y, line[1])
            limits[1].z = max(limits[1].z, line[2])
        self._limits = limits

    def get_limits(self):
        if self._limits is None:
            self._cal_limits()
        return self._limits

    def get_lines(self):
        lines = []
        for sketch_feature_tuple in self._sketch_features.items():
            sketch_feature = sketch_feature_tuple[1]
            plane_feature = sketch_feature.get_features()[0]
            p = plane_feature.get_vertex('p')
            xd = plane_feature.get_vertex('xd')
            yd = plane_feature.get_vertex('yd')
            cp = np.cross(xd.xyz, yd.xyz)
            n = cp / np.linalg.norm(cp)
            pm = np.array([xd.xyz, yd.xyz, n])
            sketch = sketch_feature.get_objects()[0]
            for edge_tuple in sketch.get_edges():
                edge = edge_tuple[1]
                draw_data = edge.get_draw_data()
                if draw_data['type'] == 1:
                    c = draw_data['coords']
                    c1 = p.xyz + pm.dot(c[0].xyz)
                    c2 = p.xyz + pm.dot(c[1].xyz)
                    lines.append(c1)
                    lines.append(c2)
                elif draw_data['type'] == 2:
                    start_angle = draw_data["sa"] * pi / (180 * 16)
                    span = draw_data["span"] * pi / (180 * 16)
                    radius = draw_data["r"]
                    c = draw_data["c"]
                    divisions = abs(int(span*20))
                    for i in range(divisions):
                        cx = c.x + cos(start_angle + span*i/divisions)*radius
                        cy = c.y + sin(start_angle + span*i/divisions)*radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                        cx = c.x + cos(start_angle + span * (i + 1) / divisions) * radius
                        cy = c.y + sin(start_angle + span * (i + 1) / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                elif draw_data['type'] == 3:
                    radius = draw_data["r"]
                    c = draw_data["c"]
                    divisions = int(2 * pi * 20)
                    for i in range(divisions):
                        cx = c.x + cos(2 * pi * i / divisions) * radius
                        cy = c.y + sin(2 * pi * i / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                        cx = c.x + cos(2 * pi * (i + 1) / divisions) * radius
                        cy = c.y + sin(2 * pi * (i + 1) / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
        for edge_tuple in self._edges.items():
            edge = edge_tuple[1]
            kps = edge.get_end_key_points()
            if edge.type == Edge.LineEdge:
                lines.append(kps[0].xyz)
                lines.append(kps[1].xyz)

        return lines

    def on_plane_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._plane_features.pop(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_plane_feature_changed)

    def on_sketch_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._sketch_features.pop(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_sketch_feature_changed)
        self._cal_limits()

    def on_extrude_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._extrude_features.pop(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_extrude_feature_changed)
        self._update_needed = True
        self._cal_limits()

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'parameters': Parameters.serialize_json(self),
            'plane_features': self._plane_features,
            'sketch_features': self._sketch_features,
            'extrude_features': self._extrude_features,
            'feature_progression': self._feature_progression,
            'type': self._geometry_type,
            'edges': self._edges,
            'surfaces': self._surfaces
        }

    @staticmethod
    def deserialize(data, param_parent, document):
        part = Part(param_parent, document)
        if data is not None:
            part.deserialize_data(data)
        return part

    def deserialize_data(self, data):
        IdObject.deserialize_data(self, data['uid'])
        Parameters.deserialize_data(self, data['parameters'])
        for feature_data_tuple in data.get('plane_features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._plane_features[feature.uid] = feature
            feature.add_change_handler(self.on_plane_feature_changed)
        for feature_data_tuple in data.get('sketch_features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._sketch_features[feature.uid] = feature
            feature.add_change_handler(self.on_sketch_feature_changed)
        for feature_data_tuple in data.get('extrude_features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._extrude_features[feature.uid] = feature
            feature.add_change_handler(self.on_extrude_feature_changed)


ExtrudeFeature = 0
RevolveFeature = 1
FilletFeature = 2
PlaneFeature = 3
SketchFeature = 4


class Feature(NamedObservableObject, IdObject):
    def __init__(self, document, feature_parent, feature_type=ExtrudeFeature, name="new feature"):
        IdObject.__init__(self)
        NamedObservableObject.__init__(self, name)
        self._doc = document
        self._feature_parent = feature_parent
        if type(feature_type) is not int:
            raise TypeError("feature type must be int")
        self._feature_type = feature_type
        self._vertexes = {}
        self._edges = []
        self._features = []
        self._features_late_bind = []
        self._feature_objects = []
        self._feature_objects_late_bind = []

    def get_feature_parent(self):
        return self._feature_parent

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def add_object(self, feature_object: ObservableObject):
        feature_object.add_change_handler(self.on_object_changed)
        self._feature_objects.append(feature_object)

    def on_object_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def get_objects(self):
        if len(self._feature_objects_late_bind) > 0:
            for feature_object_uid in self._feature_objects_late_bind:
                feature_object = None
                if self._feature_type == SketchFeature:
                    feature_object = self._doc.get_geometries().get_geometry(feature_object_uid)
                if feature_object is not None:
                    self.add_object(feature_object)
            self._feature_objects_late_bind.clear()
        feats = list(self._feature_objects)
        return feats

    def add_vertex(self, key, vertex):
        self._vertexes[key] = vertex

    def get_vertex(self, key):
        if key in self._vertexes:
            return self._vertexes[key]
        return None

    def add_feature(self, feature):
        self._features.append(feature)
        feature.add_change_handler(self.on_feature_changed)

    def get_features(self):
        if len(self._features_late_bind) > 0:
            for feature_uid in self._features_late_bind:
                feature = self._feature_parent.get_feature(feature_uid)
                self._features.append(feature)
                feature.add_change_handler(self.on_feature_changed)
            self._features_late_bind.clear()
        return list(self._features)

    @property
    def feature_type(self):
        return self._feature_type

    def on_edge_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))

    def on_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event))

    def _get_edge_uids(self):
        uids = []
        for edge in self._edges:
            uids.append(edge.uid)
        return uids

    def _get_feature_uids(self):
        uids = []
        for feature in self._features:
            uids.append(feature.uid)
        return uids

    def _get_object_uids(self):
        uids = []
        for obj in self._feature_objects:
            uids.append(obj.uid)
        return uids

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'name': NamedObservableObject.serialize_json(self),
            'edges': self._get_edge_uids(),
            'vertexes': self._vertexes,
            'type': self._feature_type,
            'features': self._get_feature_uids(),
            'objects': self._get_object_uids()

        }

    @staticmethod
    def deserialize(data, feature_parent, document):
        feature = Feature(document, feature_parent)
        if data is not None:
            feature.deserialize_data(data, feature_parent)
        return feature

    def deserialize_data(self, data, feature_parent):
        IdObject.deserialize_data(self, data['uid'])
        NamedObservableObject.deserialize_data(self, data['name'])
        self._feature_type = data['type']
        for vertex_data_tuple in data.get('vertexes', {}).items():
            vertex_data = vertex_data_tuple[1]
            vertex = Vertex.deserialize(vertex_data)
            self._vertexes[vertex_data_tuple[0]] = vertex

        for edges_uid in data.get('edges', []):
            edge = self._doc.get_geometries.get_edge(edges_uid)
            self._edges.append(edge)
            edge.add_change_handler(self.on_edge_changed)

        for feature_uid in data.get('features', []):
            self._features_late_bind.append(feature_uid)

        for feature_object_uid in data.get('objects', []):
            self._feature_objects_late_bind.append(feature_object_uid)


class Surface(ObservableObject, IdObject):
    def __init__(self):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._main_edge_loop = []
        self._cutting_edges_loops = []

    def get_triangles(self):
        triangles = []
        kps = []
        if len(self._main_edge_loop) == 0:
            return triangles
        remaining_edges = list(self._main_edge_loop)
        first_edge = self._main_edge_loop[0]
        remaining_edges.remove(first_edge)
        first_kp = first_edge.get_end_key_points()[0]
        next_kp = first_edge.get_end_key_points()[1]
        kps.append(first_kp)
        kps.append(next_kp)
        while len(remaining_edges) > 0:
            edge_found = None
            for edge in remaining_edges:
                ekps = edge.get_end_key_points()
                if ekps[0] == next_kp:
                    next_kp = ekps[1]
                    edge_found = edge
                    break
                elif ekps[1] == next_kp:
                    next_kp = ekps[0]
                    edge_found = edge
                    break
            if edge_found is None:
                break
            remaining_edges.remove(edge)
            if next_kp != first_edge:
                kps.append(next_kp)
        sw = True
        st_c = 0
        en_c = len(kps) - 1
        while st_c - en_c <= 1:
            p1 = kps[st_c].xyz
            p2 = kps[en_c].xyz
            if sw:
                st_c += 1
                p3 = kps[st_c].xyz
            else:
                en_c -= 1
                p3 = kps[en_c].xyz
            sw = not sw
            triangles.append([p1, p2, p3])

        return triangles

    def set_main_edges(self, edges_loop):
        self._main_edge_loop = edges_loop
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self))

    def add_cutting_edges_loop(self, cutting_edges_loop):
        self._cutting_edges_loops.append(cutting_edges_loop)



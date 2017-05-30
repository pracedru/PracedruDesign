from math import *

import numpy as np

from Data.Axis import Axis
from Data.Edges import Edge
from Data.Events import ChangeEvent, ValueChangeEvent
from Data.Feature import Feature
from Data.Geometry import Geometry
from Data.Objects import IdObject, NamedObservableObject, ObservableObject
from Data.Parameters import Parameters
from Data.Plane import Plane
from Data.Point3d import KeyPoint
from Data.Surface import Surface
from Data.Vertex import Vertex


class Part(Geometry):
    def __init__(self, parameters_parent, document, name="New part"):
        Geometry.__init__(self, parameters_parent, name, Geometry.Part)
        self._doc = document
        self._features = {}
        self._feature_progression = []
        self._limits = None  # [Vertex(-1, -1, -1), Vertex(1, 1, 1)]
        self._update_needed = True
        self._key_points = {}
        self._edges = {}
        self._surfaces = {}
        self._color = [180, 180, 180, 255]
        self._specular = 0.5

    def get_document(self):
        return self._doc

    @property
    def specular(self):
        return self._specular

    @specular.setter
    def specular(self, value):
        old_value = self._specular
        self._specular = value
        self.changed(ValueChangeEvent(self, "specular", old_value, value))

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        old_value = self._color
        self._color = value
        self.changed(ValueChangeEvent(self, "color", old_value, value))

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

    def get_edges(self):
        return self._edges.items()

    def get_texts(self):
        return {}

    def get_new_unique_feature_name(self, name):
        unique = False
        counter = 1
        new_name = name
        while not unique:
            found = False
            for feaure_tuple in self._features.items():
                if feaure_tuple[1].name == new_name:
                    found = True
                    new_name = name + str(counter)
                    counter += 1
            if not found:
                unique = True
        return new_name

    def _add_feature(self, feature):
        self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectAdded, feature))
        self._feature_progression.append(feature.uid)
        self.changed(ChangeEvent(self, ChangeEvent.ObjectAdded, feature))

    def create_nurbs_surface(self, sketch_feature, nurbs_edges):
        name = self.get_new_unique_feature_name("New Surface")
        nurbs_surface_feature = Feature(self._doc, self, Feature.NurbsSurfaceFeature, name)
        nurbs_surface_feature.add_feature(sketch_feature)
        for edge in nurbs_edges:
            nurbs_surface_feature.add_order_item(edge.uid)
        self._features[nurbs_surface_feature.uid] = nurbs_surface_feature
        self._add_feature(nurbs_surface_feature)
        nurbs_surface_feature.add_change_handler(self.on_nurbs_surface_feature_changed)
        self._update_needed = True
        return nurbs_surface_feature

    def create_plane_feature(self, name, position, x_direction, y_direction):
        name = self.get_new_unique_feature_name(name)
        plane_feature = Feature(self._doc, self, Feature.PlaneFeature, name)
        plane_feature.add_vertex('p', position)
        plane_feature.add_vertex('xd', x_direction)
        plane_feature.add_vertex('yd', y_direction)
        self._features[plane_feature.uid] = plane_feature
        self._add_feature(plane_feature)
        plane_feature.add_change_handler(self.on_plane_feature_changed)
        return plane_feature

    def create_sketch_feature(self, sketch, plane_feature):
        name = self.get_new_unique_feature_name(sketch.name)
        sketch_feature = Feature(self._doc, self, Feature.SketchFeature, name)
        sketch_feature.add_feature(plane_feature)
        sketch_feature.add_object(sketch)
        self._features[sketch_feature.uid] = sketch_feature
        self._add_feature(sketch_feature)
        sketch_feature.add_change_handler(self.on_sketch_feature_changed)
        self._cal_limits()
        return sketch_feature

    def create_extrude_feature(self, name, sketch_feature, area, length):
        name = self.get_new_unique_feature_name(name)
        extrude_feature = Feature(self._doc, self, Feature.ExtrudeFeature, name)
        extrude_feature.add_feature(sketch_feature)
        extrude_feature.add_object(area)
        extrude_feature.add_vertex('ex_ls', Vertex(length[0], length[1]))
        self._features[extrude_feature.uid] = extrude_feature
        self._add_feature(extrude_feature)
        extrude_feature.add_change_handler(self.on_extrude_feature_changed)
        self._update_needed = True
        self._cal_limits()

    def create_revolve_feature(self, name, sketch_feature, area, length, revolve_axis):
        name = self.get_new_unique_feature_name(name)
        revolve_feature = Feature(self._doc, self, Feature.RevolveFeature, name)
        revolve_feature.add_feature(sketch_feature)
        revolve_feature.add_object(area)
        revolve_feature.add_object(revolve_axis)
        revolve_feature.add_vertex('ex_ls', Vertex(length[0], length[1]))
        self._features[revolve_feature.uid] = revolve_feature
        self._add_feature(revolve_feature)
        revolve_feature.add_change_handler(self.on_revolve_feature_changed)
        self._update_needed = True
        self._cal_limits()

    def create_key_point(self, x, y, z, ts=0.000001):
        key_point = None
        for p_tuple in self._key_points.items():
            p = p_tuple[1]
            if abs(p.x - x) <= ts and abs(p.y - y) <= ts and abs(p.z - z) <= ts:
                key_point = p
                break
        if key_point is None:
            key_point = KeyPoint(self, x, y, z)
            self._key_points[key_point.uid] = key_point
        return key_point

    def create_arc_edge(self, center, r, sa, span, plane):
        arc_edge = Edge(self, Edge.ArcEdge, plane=plane)
        arc_edge.name = "edge"
        arc_edge.add_key_point(center)
        arc_edge.set_meta_data('sa', sa)
        arc_edge.set_meta_data('ea', sa + span)
        arc_edge.set_meta_data('r', r)
        self._edges[arc_edge.uid] = arc_edge
        return arc_edge

    def create_line_edge(self, key_point1, key_point2):
        line_edge = Edge(self, Edge.LineEdge)
        line_edge.name = "Edge"
        line_edge.add_key_point(key_point1)
        line_edge.add_key_point(key_point2)
        self._edges[line_edge.uid] = line_edge
        return line_edge

    def create_nurbs_edge(self, kp):
        nurbs_edge = Edge(self, Edge.NurbsEdge)
        nurbs_edge.name = "Edge"
        nurbs_edge.add_key_point(kp)
        self._edges[nurbs_edge.uid] = nurbs_edge
        return nurbs_edge

    def create_surfaces_from_revolve(self, feature):
        surfaces = []
        extrusion_lengths = feature.get_vertex('ex_ls')
        sketch_feature = feature.get_features()[0]
        sketch = sketch_feature.get_objects()[0]
        plane_feature = sketch_feature.get_features()[0]
        p = plane_feature.get_vertex('p')
        xd = plane_feature.get_vertex('xd')
        yd = plane_feature.get_vertex('yd')
        area = feature.get_objects()[0]
        axis = feature.get_objects()[1]
        cp = np.cross(xd.xyz, yd.xyz)
        n = cp / np.linalg.norm(cp)
        pm = np.array([xd.xyz, yd.xyz, n]).transpose()

        ex_angle1 = extrusion_lengths.x
        ex_angle2 = extrusion_lengths.y
        span = ex_angle2-ex_angle1

        local_axis_origo = axis.origo
        local_axis_dir = axis.direction
        local_axis_angle = atan2(local_axis_dir.y, local_axis_dir.x)
        local_axis_perp_angle = local_axis_angle + pi/2
        local_axis_perp_dir = Vertex(cos(local_axis_perp_angle), sin(local_axis_perp_angle))
        local_axis_plane = Plane(local_axis_dir, local_axis_perp_dir)

        local_axis_perp_dir1 = local_axis_plane.get_global_xyz(0, cos(ex_angle1), sin(ex_angle1))
        local_axis_perp_dir2 = local_axis_plane.get_global_xyz(0, cos(ex_angle2), sin(ex_angle2))

        global_axis_origo = p.xyz + pm.dot(local_axis_origo.xyz)
        global_axis_dir = pm.dot(local_axis_dir.xyz)
        global_axis_dir = global_axis_dir/np.linalg.norm(global_axis_dir)
        global_axis_perp_dir1 = pm.dot(local_axis_perp_dir1)
        global_axis_perp_dir2 = pm.dot(local_axis_perp_dir2)
        cp = np.cross(global_axis_dir, global_axis_perp_dir1)
        global_norm1 = cp / np.linalg.norm(cp)
        global_axis1 = Axis(self._doc)
        global_axis1.origo.xyz = global_axis_origo
        global_axis1.direction.xyz = global_axis_dir

        plane1 = Plane(Vertex.from_xyz(global_axis_dir), Vertex.from_xyz(global_axis_perp_dir1))# , Vertex.from_xyz(global_axis_origo))
        plane2 = Plane(Vertex.from_xyz(global_axis_dir), Vertex.from_xyz(global_axis_perp_dir2))# , Vertex.from_xyz(global_axis_origo))

        plane1 = plane1.get_z_rotated_plane(-local_axis_angle)
        plane2 = plane2.get_z_rotated_plane(-local_axis_angle)

        cpm = Plane(Vertex.from_xyz(global_axis_perp_dir1), Vertex.from_xyz(global_norm1))
        front_edges = []
        back_edges = []
        for edge in area.get_edges():
            draw_data = edge.get_draw_data()
            if edge.type == Edge.LineEdge:
                kps = draw_data['coords']
                kp = kps[0]
                r = axis.distance(kp)
                c = axis.project_point(kp)
                c = pm.dot(c)
                kp = self.create_key_point(c[0], c[1], c[2])
                edge1 = self.create_arc_edge(kp, r, 0, span, cpm)

                kp = kps[1]
                r = axis.distance(kp)
                c = axis.project_point(kp)
                c = pm.dot(c)
                kp = self.create_key_point(c[0], c[1], c[2])
                edge2 = self.create_arc_edge(kp, r, 0, span, cpm)

                kps1 = edge1.get_end_key_points()
                kps2 = edge2.get_end_key_points()

                edge3 = self.create_line_edge(kps1[0], kps2[0])
                edge4 = self.create_line_edge(kps1[1], kps2[1])
                surface = Surface(Surface.SweepSurface)
                surface.set_main_edges([edge1, edge2, edge3, edge4])
                surface.set_sweep_axis(global_axis1)
                surfaces.append(surface)
                if abs(span) < 2*pi:
                    front_edges.append(edge3)
                    back_edges.append(edge4)
            elif edge.type == Edge.ArcEdge or edge.type == Edge.FilletLineEdge:
                c = draw_data['c'].xyz - local_axis_origo.xyz
                r = draw_data['r']
                sa = draw_data['sa'] * pi / (180 * 16)
                sp = draw_data['span'] * pi / (180 * 16)
                gc = global_axis_origo + plane1.get_global_xyz_array(c)
                kp = self.create_key_point(gc[0], gc[1], gc[2])
                edge1 = self.create_arc_edge(kp, r, sa, sp, plane1)

                gc = global_axis_origo + plane2.get_global_xyz_array(c)
                kp = self.create_key_point(gc[0], gc[1], gc[2])
                edge2 = self.create_arc_edge(kp, r, sa, sp, plane2)
                if abs(span) < 2 * pi:
                    front_edges.append(edge1)
                    back_edges.append(edge2)

                surface = Surface(Surface.DoubleSweepSurface)
                kps1 = edge1.get_end_key_points()
                r1 = global_axis1.distance(kps1[0])
                c1 = global_axis1.project_point(kps1[0])
                kp1 = self.create_key_point(c1[0], c1[1], c1[2])
                edge3 = self.create_arc_edge(kp1, r1, 0, span, cpm)
                r2 = global_axis1.distance(kps1[1])
                c2 = global_axis1.project_point(kps1[1])
                kp2 = self.create_key_point(c2[0], c2[1], c2[2])
                edge4 = self.create_arc_edge(kp2, r2, 0, span, cpm)
                surface.set_main_edges([edge3, edge4, edge1, edge2])
                surface.set_sweep_axis(global_axis1)
                surfaces.append(surface)

        if abs(span) < 2 * pi:
            surface = Surface(Surface.FlatSurface)
            surface.set_main_edges(front_edges)
            surfaces.append(surface)
            surface = Surface(Surface.FlatSurface)
            surface.set_main_edges(back_edges)
            surfaces.append(surface)

        return surfaces

    def create_surfaces_from_extrude(self, feature):
        surfaces = []
        extrusion_lengths = feature.get_vertex('ex_ls')
        sketch_feature = feature.get_features()[0]
        plane_feature = sketch_feature.get_features()[0]
        p = plane_feature.get_vertex('p')
        xd = plane_feature.get_vertex('xd')
        yd = plane_feature.get_vertex('yd')

        cp = np.cross(xd.xyz, yd.xyz)
        n = cp / np.linalg.norm(cp)
        pm = np.array([xd.xyz, yd.xyz, n]).transpose()
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
                kp1 = self.create_key_point(c1[0], c1[1], c1[2])
                kp2 = self.create_key_point(c2[0], c2[1], c2[2])
                edge1 = self.create_line_edge(kp1, kp2)
                front_edges.append(edge1)
                c3 = p2 + pm.dot(c[0].xyz)
                c4 = p2 + pm.dot(c[1].xyz)
                kp3 = self.create_key_point(c3[0], c3[1], c3[2])
                kp4 = self.create_key_point(c4[0], c4[1], c4[2])
                edge2 = self.create_line_edge(kp3, kp4)
                back_edges.append(edge2)
                edge3 = self.create_line_edge(kp1, kp3)
                edge4 = self.create_line_edge(kp2, kp4)
                surface = Surface(Surface.FlatSurface)
                surface.set_main_edges([edge1, edge2, edge3, edge4])
                surfaces.append(surface)
            elif edge.type == Edge.NurbsEdge:
                coords = draw_data['coords']
                coord1 = None
                for coord2 in coords:
                    if coord1 is not None:
                        c1 = p1 + pm.dot(coord1.xyz)
                        c2 = p1 + pm.dot(coord2.xyz)
                        kp1 = self.create_key_point(c1[0], c1[1], c1[2])
                        kp2 = self.create_key_point(c2[0], c2[1], c2[2])
                        edge1 = self.create_line_edge(kp1, kp2)
                        front_edges.append(edge1)
                        c1 = p2 + pm.dot(coord1.xyz)
                        c2 = p2 + pm.dot(coord2.xyz)
                        kp1 = self.create_key_point(c1[0], c1[1], c1[2])
                        kp2 = self.create_key_point(c2[0], c2[1], c2[2])
                        edge2 = self.create_line_edge(kp1, kp2)
                        back_edges.append(edge2)
                    coord1 = coord2
                    surface = Surface(Surface.NurbsSurface)

            elif edge.type == Edge.ArcEdge or edge.type == Edge.FilletLineEdge:
                plane = Plane(xd, yd)
                c = draw_data['c']
                r = draw_data['r']
                sa = draw_data['sa'] * pi / (180 * 16)
                span = draw_data['span'] * pi / (180 * 16)
                center1 = p1 + pm.dot(c.xyz)
                center_kp = self.create_key_point(center1[0], center1[1], center1[2])
                edge1 = self.create_arc_edge(center_kp, r, sa, span, plane)
                front_edges.append(edge1)
                kps1 = edge1.get_end_key_points()
                center2 = p2 + pm.dot(c.xyz)
                center_kp = self.create_key_point(center2[0], center2[1], center2[2])
                edge2 = self.create_arc_edge(center_kp, r, sa, span, plane)
                back_edges.append(edge2)
                kps2 = edge2.get_end_key_points()
                edge3 = self.create_line_edge(kps1[0], kps2[0])
                edge4 = self.create_line_edge(kps1[1], kps2[1])
                surface = Surface(Surface.SweepSurface)
                surface.set_main_edges([edge1, edge2, edge3, edge4])
                surfaces.append(surface)

        surface = Surface(Surface.FlatSurface)
        surface.set_main_edges(front_edges)
        surfaces.append(surface)
        surface = Surface(Surface.FlatSurface)
        surface.set_main_edges(back_edges)
        surfaces.append(surface)
        return surfaces

    def create_suface_from_nurbs_feature(self, nurbs_surface_feature):
        surface = Surface(Surface.NurbsSurface)
        sketch_feature = nurbs_surface_feature.get_features()[0]
        plane_feature = sketch_feature.get_features()[0]
        p = plane_feature.get_vertex('p')
        xd = plane_feature.get_vertex('xd')
        yd = plane_feature.get_vertex('yd')

        cp = np.cross(xd.xyz, yd.xyz)
        n = cp / np.linalg.norm(cp)
        pm = np.array([xd.xyz, yd.xyz, n]).transpose()
        sketch = sketch_feature.get_objects()[0]
        order_items = nurbs_surface_feature.get_order_items()
        edges = []
        for order_item in order_items:
            edge = sketch.get_edge(order_item)
            kps = edge.get_key_points()
            c = p.xyz + pm.dot(kps[0].xyz)
            kp = self.create_key_point(c[0], c[1], c[2])
            surf_edge = self.create_nurbs_edge(kp)
            for i in range(1, len(kps)):
                c = p.xyz + pm.dot(kps[i].xyz)
                kp = self.create_key_point(c[0], c[1], c[2])
                surf_edge.add_key_point(kp)
            edges.append(surf_edge)

        surface.set_main_edges(edges)
        return surface

    def update_geometry(self):
        self._surfaces.clear()
        self._edges.clear()
        self._key_points.clear()
        self._surfaces.clear()
        for feature_key in self._feature_progression:
            feature = self._features[feature_key]
            if feature.feature_type == Feature.ExtrudeFeature:
                surfaces = self.create_surfaces_from_extrude(feature)
                for surface in surfaces:
                    self._surfaces[surface.uid] = surface
            elif feature.feature_type == Feature.RevolveFeature:
                surfaces = self.create_surfaces_from_revolve(feature)
                for surface in surfaces:
                    self._surfaces[surface.uid] = surface
            elif feature.feature_type == Feature.NurbsSurfaceFeature:
                surface = self.create_suface_from_nurbs_feature(feature)
                self._surfaces[surface.uid] = surface
        self._cal_limits()
        self._update_needed = False

    def get_feature(self, uid):
        if uid in self._features:
            return self._features[uid]

        return None

    def get_feature_progression(self):
        return self._feature_progression

    def get_plane_features(self):
        planes = []
        for feature in self._features.items():
            if feature[1].feature_type == Feature.PlaneFeature:
                planes.append(feature[1])
        return planes

    def get_features_list(self):
        features = []
        for feature_tuple in self._features.items():
            features.append(feature_tuple[1])
        return features

    def get_sketch_features(self):
        features = []
        for feature_tuple in self._features.items():
            if feature_tuple[1].feature_type == Feature.SketchFeature:
                features.append(feature_tuple[1])
        return features

    def _cal_limits(self):
        limits = [Vertex(-0.001, -0.001, -0.001), Vertex(0.001, 0.001, 0.001)]
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
        if self._limits is None or self._update_needed:
            self._cal_limits()
        return self._limits

    def get_lines(self):
        lines = []
        for sketch_feature in self.get_sketch_features():
            plane_feature = sketch_feature.get_features()[0]
            p = plane_feature.get_vertex('p')
            xd = plane_feature.get_vertex('xd')
            yd = plane_feature.get_vertex('yd')
            cp = np.cross(xd.xyz, yd.xyz)
            n = cp / np.linalg.norm(cp)
            pm = np.array([xd.xyz, yd.xyz, n]).transpose()
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
                    divisions = abs(int(span * 15))
                    for i in range(divisions):
                        cx = c.x + cos(start_angle + span * i / divisions) * radius
                        cy = c.y + sin(start_angle + span * i / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                        cx = c.x + cos(start_angle + span * (i + 1) / divisions) * radius
                        cy = c.y + sin(start_angle + span * (i + 1) / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                elif draw_data['type'] == 3:
                    radius = draw_data["r"]
                    c = draw_data["c"]
                    divisions = int(2 * pi * 15)
                    for i in range(divisions):
                        cx = c.x + cos(2 * pi * i / divisions) * radius
                        cy = c.y + sin(2 * pi * i / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                        cx = c.x + cos(2 * pi * (i + 1) / divisions) * radius
                        cy = c.y + sin(2 * pi * (i + 1) / divisions) * radius
                        lines.append(p.xyz + pm.dot(np.array([cx, cy, 0])))
                elif draw_data['type'] == 4:
                    coords = draw_data['coords']
                    c1 = None
                    for c in coords:
                        c2 = p.xyz + pm.dot(c.xyz)
                        if c1 is not None:
                            lines.append(c1)
                            lines.append(c2)
                        c1 = c2
        for edge_tuple in self._edges.items():
            edge = edge_tuple[1]
            kps = edge.get_end_key_points()
            if edge.type == Edge.LineEdge:

                lines.append(kps[0].xyz)
                lines.append(kps[1].xyz)
            if edge.type == Edge.ArcEdge:
                radius = edge.get_meta_data("r")
                c = edge.get_key_points()[0]
                start_angle = edge.get_meta_data("sa")
                end_angle = edge.get_meta_data("ea")
                span = end_angle - start_angle
                pm = edge.plane.get_global_projection_matrix()
                divisions = abs(int(span * 15))
                for i in range(divisions):
                    cx = cos(start_angle + span * i / divisions) * radius
                    cy = sin(start_angle + span * i / divisions) * radius
                    lines.append(c.xyz + pm.dot(np.array([cx, cy, 0])))
                    cx = cos(start_angle + span * (i + 1) / divisions) * radius
                    cy = sin(start_angle + span * (i + 1) / divisions) * radius
                    lines.append(c.xyz + pm.dot(np.array([cx, cy, 0])))

        return lines

    def on_plane_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._features.pop(event.sender.uid)
            self._feature_progression.remove(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_plane_feature_changed)

    def on_nurbs_surface_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._features.pop(event.sender.uid)
            self._feature_progression.remove(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_plane_feature_changed)
        self._update_needed = True

    def on_sketch_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._features.pop(event.sender.uid)
            self._feature_progression.remove(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_sketch_feature_changed)
        self._update_needed = True

    def on_extrude_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._features.pop(event.sender.uid)
            self._feature_progression.remove(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_extrude_feature_changed)
        self._update_needed = True
        # self._cal_limits()

    def on_revolve_feature_changed(self, event):
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, event.sender))
        if event.type == ChangeEvent.Deleted:
            self.changed(ChangeEvent(self, ChangeEvent.BeforeObjectRemoved, event.sender))
            self._features.pop(event.sender.uid)
            self._feature_progression.remove(event.sender.uid)
            self.changed(ChangeEvent(self, ChangeEvent.ObjectRemoved, event.sender))
            event.sender.remove_change_handler(self.on_revolve_feature_changed)
        self._update_needed = True

    def delete(self):
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

    def serialize_json(self):
        return {
            'uid': IdObject.serialize_json(self),
            'parameters': Parameters.serialize_json(self),
            'features': self._features,
            'feature_progression': self._feature_progression,
            'type': self._geometry_type
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
        for feature_data_tuple in data.get('features', {}).items():
            feature = Feature.deserialize(feature_data_tuple[1], self, self._doc)
            self._features[feature.uid] = feature
            if feature.feature_type == Feature.PlaneFeature:
                feature.add_change_handler(self.on_plane_feature_changed)
            elif feature.feature_type == Feature.PlaneFeature:
                feature.add_change_handler(self.on_sketch_feature_changed)
            elif feature.feature_type == Feature.ExtrudeFeature:
                feature.add_change_handler(self.on_extrude_feature_changed)
            elif feature.feature_type == Feature.RevolveFeature:
                feature.add_change_handler(self.on_revolve_feature_changed)
        self._feature_progression = data.get('feature_progression', [])

        self._update_needed = True





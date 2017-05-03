import numpy as np
from math import *

from Data.Edges import Edge
from Data.Events import *
from Data.Vertex import Vertex
from Data.Objects import *


class Surface(ObservableObject, IdObject):
    FlatSurface = 0
    SweepSurface = 1
    DoubleSweepSurface = 2

    def __init__(self, surface_type):
        IdObject.__init__(self)
        ObservableObject.__init__(self)
        self._main_edge_loop = []
        self._cutting_edges_loops = []
        self._surface_type = surface_type

    def find_angles(self, kps, norm):
        angles = []
        total_angle = 0
        angles.append(kps[0].angle_between3d_planar(kps[1], kps[len(kps) - 1], norm))
        if angles[0] < 0:
            total_angle += 2 * pi + angles[0]
        else:
            total_angle += angles[0]
        for i in range(1, len(kps) - 1):
            angle = kps[i].angle_between3d_planar(kps[i + 1], kps[i - 1], norm)
            angles.append(angle)
            if angle < 0:
                total_angle += 2 * pi + angle
            else:
                total_angle += angle
        angle = kps[len(kps) - 1].angle_between3d_planar(kps[0], kps[len(kps) - 2], norm)
        angles.append(angle)
        if angle < 0:
            total_angle += 2 * pi + angle
        else:
            total_angle += angle
        sss = total_angle / (len(kps) - 2)
        is_positive = abs(sss) - pi < 0.001
        concaves = []
        for i in range(len(angles)):
            angle = angles[i]
            is_p_a = angle >= 0
            if is_p_a != is_positive:
                concaves.append(i)
        return angles, concaves, total_angle

    def get_triangles_of_convex(self, kps, triangles):
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

    def get_triangles(self):
        if self._surface_type == Surface.FlatSurface:
            return self.get_flat_surface_triangles()
        elif self._surface_type == Surface.SweepSurface:
            return self.get_sweep_surface_triangles()
        else:
            return self.get_double_sweep_surface_triangles()

    def get_divisions_of_edge(self, edge):
        if edge.type == Edge.ArcEdge:
            sa = edge.get_meta_data('sa')
            ea = edge.get_meta_data('ea')
            span = ea - sa
            return int(abs(span * 20))
        return 1

    def get_position_on_edge(self, edge, relative):
        if edge.type == Edge.LineEdge:
            kps = edge.get_end_key_points()
            diff = kps[1].xyz - kps[0].xyz
            p = kps[0].xyz + diff * relative
            x = p[0]
            y = p[1]
            z = p[2]
        if edge.type == Edge.ArcEdge:
            plane = edge.plane
            r = edge.get_meta_data('r')
            sa = edge.get_meta_data('sa')
            ea = edge.get_meta_data('ea')
            span = ea - sa
            c = edge.get_key_points()[0]
            divisions = int(abs(span * 10))
            x = cos(sa + span * relative) * r
            y = sin(sa + span * relative) * r
            z = 0
            cc = c.xyz + plane.get_global_xyz(x, y, z)
            x = cc[0]
            y = cc[1]
            z = cc[2]
        return Vertex(x, y, z)

    def get_double_sweep_surface_triangles(self):
        triangles = []
        return triangles

    def get_sweep_surface_triangles(self):
        triangles = []
        kps = []
        edges = []
        remaining_edges = list(self._main_edge_loop)
        first_edge = self._main_edge_loop[0]
        first_kp = first_edge.get_end_key_points()[0]
        next_kp = first_edge.get_end_key_points()[1]
        kps.append(first_kp)
        kps.append(next_kp)
        edges.append(first_edge)
        remaining_edges.remove(first_edge)
        while len(remaining_edges) > 0:
            edge_found = None
            for edge in remaining_edges:
                ekps = edge.get_end_key_points()
                if abs(np.linalg.norm(ekps[0].xyz - next_kp.xyz)) < 0.0000001:
                    next_kp = ekps[1]
                    edge_found = edge
                    break
                elif abs(np.linalg.norm(ekps[1].xyz - next_kp.xyz)) < 0.0000001:
                    next_kp = ekps[0]
                    edge_found = edge
                    break
            if edge_found is None:
                next_kp = ekps[1]
            else:
                edges.append(edge)
            remaining_edges.remove(edge)
            if next_kp is not first_kp:
                kps.append(next_kp)

        divisions = [1, 1]
        divisions[0] = self.get_divisions_of_edge(edges[0])
        divisions[1] = self.get_divisions_of_edge(edges[1])
        divisions[0] = max(self.get_divisions_of_edge(edges[2]), divisions[0])
        divisions[1] = max(self.get_divisions_of_edge(edges[3]), divisions[1])

        v11 = self.get_position_on_edge(edges[0], 0)
        v21 = self.get_position_on_edge(edges[2], 0)
        ri_old = 0
        for i in range(1, divisions[0] + 1):
            ri = i / divisions[0]
            v12 = self.get_position_on_edge(edges[0], ri)
            v22 = self.get_position_on_edge(edges[2], ri)
            v31 = self.get_position_on_edge(edges[1], 0)
            v41 = self.get_position_on_edge(edges[3], 0)
            triangles.append([v11.xyz, v21.xyz, v12.xyz])
            triangles.append([v21.xyz, v12.xyz, v22.xyz])
            rj_old = 0
            for j in range(1, divisions[1]):
                rj = j / divisions[1]
                v32 = self.get_position_on_edge(edges[1], rj)
                v42 = self.get_position_on_edge(edges[3], rj)
                triangles.append([(v11.xyz + v31.xyz) / 2, (v21.xyz + v41.xyz) / 1, (v22.xyz + v32.xyz) / 2])
                triangles.append([(v21.xyz + v41.xyz) / 1, (v22.xyz + v32.xyz) / 2, (v12.xyz + v42.xyz) / 2])
                v31 = v32
                v41 = v42
                rj_old = rj
            v11 = v12
            v21 = v22
            ri_old = ri
        return triangles

    def get_flat_surface_triangles(self):
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
                if abs(np.linalg.norm(ekps[0].xyz - next_kp.xyz)) < 0.000001:
                    next_kp = ekps[1]
                    edge_found = edge
                    break
                elif abs(np.linalg.norm(ekps[1].xyz - next_kp.xyz)) < 0.000001:
                    next_kp = ekps[0]
                    edge_found = edge
                    break
            if edge_found is None:
                next_kp = ekps[1]
            remaining_edges.remove(edge)
            if edge.type is Edge.ArcEdge:
                plane = edge.plane
                r = edge.get_meta_data('r')
                sa = edge.get_meta_data('sa')
                ea = edge.get_meta_data('ea')
                c = edge.get_key_points()[0]
                cc = c.xyz + plane.get_global_xyz(cos(sa) * r, sin(sa) * r, 0)
                ln1 = np.linalg.norm(kps[len(kps) - 1].xyz - cc)
                cc = c.xyz + plane.get_global_xyz(cos(ea) * r, sin(ea) * r, 0)
                ln2 = np.linalg.norm(kps[len(kps) - 1].xyz - cc)
                if ln1 > ln2:
                    dum = ea
                    ea = sa
                    sa = dum
                span = ea - sa
                divisions = int(abs(span * 10))
                increment = span / divisions
                for i in range(1, divisions + 1):
                    x = cos(sa + increment * i) * r
                    y = sin(sa + increment * i) * r
                    z = 0
                    cc = c.xyz + plane.get_global_xyz(x, y, z)
                    x = cc[0]
                    y = cc[1]
                    z = cc[2]
                    kps.append(Vertex(x, y, z))
                next_kp = kps[len(kps) - 1]
            elif abs(np.linalg.norm(next_kp.xyz - first_kp.xyz)) > 0.000001:  # next_kp is not first_kp:
                if abs(np.linalg.norm(next_kp.xyz - kps[len(kps) - 1].xyz)) > 0.000001:
                    kps.append(next_kp)
        v1 = kps[0].xyz - kps[1].xyz
        try:
            v2 = kps[2].xyz - kps[1].xyz
        except IndexError as e:
            print("weeeeaaaaargfh")
        if len(kps) < 3:
            return triangles
        cp = np.cross(v1, v2)
        norm = cp / np.linalg.norm(cp)

        angles, concaves, total_angle = self.find_angles(kps, norm)

        remaining_kps = list(kps)
        while len(concaves) > 0 and len(remaining_kps) > 3:
            sharpest_convex = 1e10
            m = 0
            for i in range(len(angles)):
                if i not in concaves:
                    if abs(sharpest_convex) > abs(angles[i]):
                        sharpest_convex = angles[i]
                        m = i
            p1 = remaining_kps[m].xyz
            if m < 1:
                o = len(remaining_kps) - 1
            else:
                o = m - 1
            p2 = remaining_kps[o].xyz
            if m + 1 >= len(remaining_kps):
                n = 0
            else:
                n = m + 1
            p3 = remaining_kps[n].xyz
            # if n not in concaves and o not in concaves:
            triangles.append([p1, p2, p3])
            remaining_kps.pop(m)
            angles, concaves, total_angle = self.find_angles(remaining_kps, norm)

        if len(remaining_kps) > 2:
            self.get_triangles_of_convex(remaining_kps, triangles)

        return triangles

    def set_main_edges(self, edges_loop):
        self._main_edge_loop = edges_loop
        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self))

    def add_cutting_edges_loop(self, cutting_edges_loop):
        self._cutting_edges_loops.append(cutting_edges_loop)

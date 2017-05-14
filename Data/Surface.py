import numpy as np
from math import *

from Data.Edges import Edge
from Data.Events import *
from Data.Vertex import Vertex
from Data.Objects import *


def fsign(value):
    if isclose(value, 0, abs_tol=1e-10):
        return 0
    elif value < 0:
        return -1.0
    else:
        return 1.0


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
        self._sweep_axis = None
        self._triangles = None
        self._normals = None

    def get_projected_point(self, pt1, pt2):
        delta = pt2 - pt1
        p = pt1 + delta * (pt1[2] / (pt1[2] - pt2[2]))
        return p

    def get_section_by_plane(self, plane):
        pm = plane.get_local_projection_matrix()
        section_data = {}
        loops = []
        coords = []
        triangles = self.get_faces_normals()

        for triangle in triangles:
            v1 = triangle[0]
            v2 = triangle[1]
            v3 = triangle[0]
            cp = np.cross(v2 - v1, v3 - v1)
            n = cp / np.linalg.norm(cp)
            p1 = pm.dot(v1)
            p2 = pm.dot(v2)
            p3 = pm.dot(v3)
            counter = 0
            if isclose(p1[2], 0, abs_tol=1e-8):
                coords.append(p1)
                counter += 1
            if isclose(p2[2], 0, abs_tol=1e-8):
                coords.append(p2)
                counter += 1
            if isclose(p3[2], 0, abs_tol=1e-8):
                coords.append(p3)
                counter += 1
            if counter < 2:
                s1 = fsign(p1[2])
                s2 = fsign(p2[2])
                s3 = fsign(p3[2])
                if s1 != s2 and s1 != 0 and s2 != 0:
                    coords.append(self.get_projected_point(p1, p2))
                if s2 != s3 and s2 != 0 and s3 != 0:
                    coords.append(self.get_projected_point(p2, p3))
                if s3 != s1 and s1 != 0 and s3 != 0:
                    coords.append(self.get_projected_point(p3, p1))

        section_data['coords'] = coords
        return section_data

    def set_sweep_axis(self, axis):
        self._sweep_axis = axis
        axis.add_change_handler(self.on_edge_changed)

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
            triangles.extend([p1, p2, p3])

    def get_faces_normals(self):
        if self._triangles is None:
            if self._surface_type == Surface.FlatSurface:
                self._triangles, self._normals = self.get_flat_surface_triangles()
            elif self._surface_type == Surface.SweepSurface:
                self._triangles, self._normals = self.get_sweep_surface_triangles()
            else:
                self._triangles, self._normals = self.get_double_sweep_surface_triangles()
        return self._triangles, self._normals

    def get_divisions_of_edge(self, edge):
        if edge.type == Edge.ArcEdge:
            sa = edge.get_meta_data('sa')
            ea = edge.get_meta_data('ea')
            span = ea - sa
            return max(int(abs(span * 15)), 3)
        return 1

    def get_double_surface_center_and_radius(self, edge2, relative2):
        plane2 = edge2.plane
        c2 = edge2.get_key_points()[0]
        r2 = edge2.get_meta_data('r')
        sa2 = edge2.get_meta_data('sa')
        ea2 = edge2.get_meta_data('ea')
        span2 = ea2 - sa2
        angle2 = span2 * relative2
        x = cos(sa2 + angle2) * r2
        y = sin(sa2 + angle2) * r2
        z = 0
        p1 = c2.xyz + plane2.get_global_xyz(x, y, z)
        r1 = self._sweep_axis.distance_xyz(p1)
        c1 = self._sweep_axis.project_point_xyz(p1)
        return c1, r1

    def get_position_on_double_edge(self, edge1, relative1, c1, r1):
        plane1 = edge1.plane
        sa1 = edge1.get_meta_data('sa')
        ea1 = edge1.get_meta_data('ea')
        span1 = ea1 - sa1
        x = cos(sa1 + span1 * relative1) * r1
        y = sin(sa1 + span1 * relative1) * r1
        z = 0
        cc = c1 + plane1.get_global_xyz(x, y, z)
        return cc

    def get_position_on_edge(self, edge, relative):
        if edge.type == Edge.LineEdge:
            kps = edge.get_end_key_points()
            diff = kps[1].xyz - kps[0].xyz
            cc = kps[0].xyz + diff * relative
        if edge.type == Edge.ArcEdge:
            plane = edge.plane
            r = edge.get_meta_data('r')
            sa = edge.get_meta_data('sa')
            ea = edge.get_meta_data('ea')
            span = ea - sa
            c = edge.get_key_points()[0]
            x = cos(sa + span * relative) * r
            y = sin(sa + span * relative) * r
            z = 0
            cc = c.xyz + plane.get_global_xyz(x, y, z)
        return cc

    def calc_norm(self, v1, v2, v3):
        cp = np.cross(v2 - v1, v3 - v1)
        nm = np.linalg.norm(cp)
        if nm != 0:
            n = cp / nm
        else:
            n = cp
        return n

    def get_double_sweep_surface_triangles(self):
        triangles = []
        normals = []
        edges = self._main_edge_loop
        divisions = [1, 1]
        divisions[0] = self.get_divisions_of_edge(edges[0])
        divisions[1] = self.get_divisions_of_edge(edges[1])
        divisions[0] = max(self.get_divisions_of_edge(edges[2]), divisions[0])
        divisions[1] = max(self.get_divisions_of_edge(edges[3]), divisions[1])
        n11 = None
        n21 = None
        n12 = None
        for j in range(0, divisions[1]):
            rj = j / divisions[1]
            rj1 = (j+1) / divisions[1]
            c11, r11 = self.get_double_surface_center_and_radius(edges[1], rj)
            c12, r12 = self.get_double_surface_center_and_radius(edges[1], rj1)
            v11 = self.get_position_on_double_edge(edges[0], 0, c11, r11)
            v21 = self.get_position_on_double_edge(edges[0], 0, c12, r12)
            for i in range(1, divisions[0] + 1):
                ri = i / divisions[0]
                v12 = self.get_position_on_double_edge(edges[0], ri, c11, r11)
                v22 = self.get_position_on_double_edge(edges[0], ri, c12, r12)
                triangles.extend([v11, v21, v12])
                triangles.extend([v21, v22, v12])
                n22 = self.calc_norm(v11, v21, v12)
                if i == 1:
                    n21 = n22
                if j == 0:
                    n11 = n21
                    n12 = n22
                else:
                    n11 = normals[divisions[0] * (j - 1) * 6 + i * 6-3]
                    n12 = normals[divisions[0] * (j - 1) * 6 + i * 6-2]
                normals.extend([n11, n21, n12, n21, n22, n12])
                v11 = v12
                v21 = v22
                n21 = n22

        return triangles, normals

    def get_sweep_surface_triangles(self):

        triangles = []
        normals = []
        edges = self._main_edge_loop
        divisions = [1, 1]
        divisions[0] = self.get_divisions_of_edge(edges[0])

        v11 = self.get_position_on_edge(edges[0], 0)
        v21 = self.get_position_on_edge(edges[2], 0)
        for i in range(1, divisions[0] + 1):
            ri = i / divisions[0]
            v12 = self.get_position_on_edge(edges[0], ri)
            v22 = self.get_position_on_edge(edges[2], ri)
            triangles.extend([v11, v21, v12])
            triangles.extend([v21, v22, v12])
            v11 = v12
            v21 = v22
        n1 = None
        for i in range(0, len(triangles), 6):
            v1 = triangles[i]
            v2 = triangles[i + 1]
            v3 = triangles[i + 2]
            cp = np.cross(v2 - v1, v3 - v1)
            nm = np.linalg.norm(cp)
            if nm == 0:
                v1 = triangles[i + 3]
                v2 = triangles[i + 4]
                v3 = triangles[i + 5]
                cp = np.cross(v2 - v1, v3 - v1)
                nm = np.linalg.norm(cp)
            n2 = cp / nm
            if n1 is None:
                n1 = n2
            normals.append(n1)
            normals.append(n1)
            normals.append(n2)
            normals.append(n1)
            normals.append(n2)
            normals.append(n2)
            n1 = n2
        return triangles, normals

    def get_flat_surface_triangles(self):
        triangles = []
        normals = []
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
            triangles.extend([p1, p2, p3])
            remaining_kps.pop(m)
            angles, concaves, total_angle = self.find_angles(remaining_kps, norm)

        if len(remaining_kps) > 2:
            self.get_triangles_of_convex(remaining_kps, triangles)

        v1 = triangles[0]
        v2 = triangles[1]
        v3 = triangles[2]
        cp = np.cross(v2 - v1, v3 - v1)
        nm = np.linalg.norm(cp)
        if nm != 0:
            n = cp / nm
        else:
            v1 = triangles[3]
            v2 = triangles[4]
            v3 = triangles[5]
            cp = np.cross(v2 - v1, v3 - v1)
            nm = np.linalg.norm(cp)
            n = cp / nm
        for i in range(0, len(triangles), 3):
            normals.append(n)
            normals.append(n)
            normals.append(n)
        return triangles, normals

    def set_main_edges(self, edges_loop):
        rem_ed = list(edges_loop)
        first_edge = rem_ed[0]
        rem_ed.remove(first_edge)
        self._main_edge_loop.append(first_edge)
        las_kp = first_edge.get_end_key_points()[0]
        while len(rem_ed) > 0:
            found = False
            for edge in rem_ed:
                kps = edge.get_end_key_points()
                if kps[0].distance(las_kp) < 0.000001:
                    self._main_edge_loop.append(edge)
                    found = True
                    las_kp = kps[1]
                    break
                elif kps[1].distance(las_kp) < 0.000001:
                    self._main_edge_loop.append(edge)
                    found = True
                    las_kp = kps[0]
                    break
            if not found:
                print("not found")
                if True: # if len(rem_ed) == 1:
                    self._main_edge_loop.append(edge)
                    rem_ed.remove(edge)
                    # rem_ed.clear()
                else:
                    pass # raise Exception("Unrecoverable error")
                for edge in self._main_edge_loop:
                    kps = edge.get_end_key_points()
                    print(str(kps[0].xyz))
                    print(str(kps[1].xyz))
            else:
                rem_ed.remove(edge)
            for edge in self._main_edge_loop:
                edge.add_change_handler(self.on_edge_changed)

        self.changed(ChangeEvent(self, ChangeEvent.ObjectChanged, self))

    def on_edge_changed(self, event):
        self._triangles = None

    def add_cutting_edges_loop(self, cutting_edges_loop):
        self._cutting_edges_loops.append(cutting_edges_loop)

import random
from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, QRectF, QPoint, QLocale, Qt, QEvent
from PyQt5.QtGui import QLinearGradient, QColor, QPen, QPolygon, QPainterPath, QPolygonF, QBrush, QPainter
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QInputDialog, QDialog, QMessageBox
from math import cos, pi, sin, sqrt, ceil, asin, tan

import Business
from Data.Areas import Area
from Data.Components import Component
from Data.Sketch import Edge
from Data.Geometry import Geometry
from Data.Mesh import MeshDefinition
from Data.Sweeps import SweepDefinition
from Data.Vertex import Vertex
from GUI import is_dark_theme

__author__ = 'mamj'


class ViewWidget(QWidget):
    GeometryView = 0
    EdgesView = 1
    AreasView = 2
    MaterialsView = 3
    ComponentsView = 4
    MarginsView = 5
    MeshView = 6
    SweepsView = 7

    def __init__(self, parent, document):
        QWidget.__init__(self, parent)
        self._main_window = parent
        self._doc = document
        self.setMouseTracking(True)
        self._doc.add_change_handler(self.on_document_changed)
        self._scale = 1.0
        self._offset = Vertex()
        self.left_button_hold = False
        self.right_button_hold = False
        self.middle_button_hold = False
        self._pan_ref_pos = None
        self.View = ViewWidget.GeometryView
        self.draw_functions = [
            self.draw_geometry,
            self.draw_edges,
            self.draw_areas,
            self.draw_materials,
            self.draw_components,
            self.draw_margins,
            self.draw_mesh,
            self.draw_sweeps
        ]
        self.mouse_position = None
        self._select_kp = True
        self._select_edge = True
        self._select_area = True
        self._set_similar_x = False
        self._set_similar_y = False
        self._draw_line_edge = False
        self._set_fillet_kp = False
        self._similar_coords = set()
        self.similar_threshold = 0.1
        self._kp_hover = None
        self._kp_move = None
        self._edge_hover = None
        self._area_hover = None
        self._is_dark_theme = is_dark_theme()
        self._selected_areas = []
        self._selected_edges = []
        self._selected_key_points = []
        self._selected_material = None
        self._selected_component = None
        self._selected_margin = None
        self._selected_mesh_def = None
        self._selected_sweep_def = None
        self.show_area_names = False
        self.show_key_points = False
        self.show_sfak_values = False
        self._multi_select = False
        self._create_area = False
        self.installEventFilter(self)

    def set_view(self, view):
        self.View = view
        self.update()

    def mouseMoveEvent(self, q_mouse_event):
        position = q_mouse_event.pos()
        if self.mouse_position is not None:
            mouse_move_x = self.mouse_position.x() - position.x()
            mouse_move_y = self.mouse_position.y() - position.y()
        self.mouse_position = position
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        x = (self.mouse_position.x() - width) / scale - self._offset.x
        y = -((self.mouse_position.y() - height) / scale + self._offset.y)
        edges_object = self._doc.get_edges()
        key_points = edges_object.get_key_points()
        if self.middle_button_hold:
            self._offset.x -= mouse_move_x/scale
            self._offset.y += mouse_move_y/scale
        if self.left_button_hold:
            if self._kp_move is not None:
                if self._kp_move.get_x_parameter() is None:
                    self._kp_move.x = x
                if self._kp_move.get_y_parameter() is None:
                    self._kp_move.y = y
        self._kp_hover = None
        self._edge_hover = None
        self._area_hover = None
        if self._select_kp:
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                x1 = key_point.x
                y1 = key_point.y
                if abs(x1 - x) < 5 / scale and abs(y1 - y) < 5 / scale:
                    self._kp_hover = key_point
                    break

        if self._select_edge and self._kp_hover is None:
            smallest_dist = 10e10
            closest_edge = None
            for edge_tuple in edges_object.get_edges():
                edge = edge_tuple[1]
                dist = edge.distance(Vertex(x, y, 0))
                if dist < smallest_dist:
                    smallest_dist = dist
                    closest_edge = edge
            if smallest_dist * scale < 10:
                self._edge_hover = closest_edge

        if self._select_area and self._kp_hover is None and self._edge_hover is None:
            areas_object = self._doc.get_areas()
            for area_tuple in areas_object.get_areas():
                area = area_tuple[1]
                if area.inside(Vertex(x, y, 0)):
                    self._area_hover = area
                    break

        if self._set_similar_x and self._kp_hover is not None:
            self._similar_coords.clear()
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                x1 = key_point.x
                if abs(x1 - self._kp_hover.x) < self.similar_threshold:
                    self._similar_coords.add(key_point)

        if self._set_similar_y and self._kp_hover is not None:
            self._similar_coords.clear()
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                y1 = key_point.y
                if abs(y1 - self._kp_hover.y) < self.similar_threshold:
                    self._similar_coords.add(key_point)

        if self._set_similar_x or self._select_kp or self._select_edge or self._set_similar_y:
            self.update()

    def mousePressEvent(self, q_mouse_event):
        self.setFocus()
        position = q_mouse_event.pos()
        if q_mouse_event.button() == 4:
            self.middle_button_hold = True
            self._pan_ref_pos = position
            return
        if q_mouse_event.button() == 1:
            self.left_button_hold = True
            self._move_ref_pos = position

        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        x = (self.mouse_position.x() - width) / scale - self._offset.x
        y = -((self.mouse_position.y() - height) / scale + self._offset.y)
        if self._set_similar_x or self._set_similar_y:
            params = []
            for param_tuple in self._doc.get_parameters().get_all_parameters():
                params.append(param_tuple[1].name)
            value = QInputDialog.getItem(self, "Set parameter", "Parameter:", params, 0, True)
        if self._set_similar_x and value[1] == QDialog.Accepted:
            self._set_similar_x = False
            Business.set_similar_x(self._doc, self._similar_coords, value[0])
        else:
            self._set_similar_x = False
        if self._set_similar_y and value[1] == QDialog.Accepted:
            self._set_similar_y = False
            Business.set_similar_y(self._doc, self._similar_coords, value[0])
        else:
            self._set_similar_y = False

        if self.View == ViewWidget.EdgesView or self.View == ViewWidget.AreasView:
            if self.left_button_hold and self._kp_hover is not None:
                if self._kp_hover in self._selected_key_points:
                    self._kp_move = self._kp_hover
            if self._select_edge and self._edge_hover is not None and self._kp_hover is None:
                if self._create_area or self._multi_select:
                    if self._edge_hover in self._selected_edges:
                        self._selected_edges.remove(self._edge_hover)
                    else:
                        self._selected_edges.append(self._edge_hover)
                else:
                    self._selected_edges = [self._edge_hover]
                if self._create_area:
                    self.check_edge_loop()
                self.update()
                self.parent().on_edge_selection_changed_in_view(self._selected_edges)
            elif self._select_edge and self._edge_hover is None:
                self._selected_edges = []
                self.update()
                self.parent().on_edge_selection_changed_in_view(self._selected_edges)

        if self.View == ViewWidget.EdgesView or self.View == ViewWidget.AreasView:
            if self._kp_hover is not None and self._select_kp:
                if self._multi_select or self._draw_line_edge:
                    self._selected_key_points.append(self._kp_hover)
                else:
                    self._selected_key_points = [self._kp_hover]
                self.update()
                self.parent().on_kp_selection_changed_in_view(self._selected_key_points)
            elif self._kp_hover is None and self._select_kp and len(self._selected_edges) == 0 and not self._draw_line_edge:
                self._selected_key_points = []
                self.update()
                self.parent().on_kp_selection_changed_in_view(self._selected_key_points)
        if self.View == ViewWidget.AreasView or self.View == ViewWidget.MaterialsView:
            if self._area_hover is not None and self._select_area and self.View == ViewWidget.AreasView:
                if self._multi_select:
                    self._selected_areas.append(self._area_hover)
                else:
                    self._selected_areas = [self._area_hover]
                self.update()
                self.parent().on_area_selection_changed_in_view(self._selected_areas)
            elif self.View == ViewWidget.MaterialsView and self._selected_material is not None and self._area_hover is not None:
                if self._area_hover in self._selected_material.get_areas():
                    self._selected_material.remove_area(self._area_hover)
                    if self._area_hover in self._selected_areas:
                        self._selected_areas.remove(self._area_hover)
                else:
                    self._selected_areas.append(self._area_hover)
                    self._selected_material.add_areas([self._area_hover])
                self.update()
                self.parent().on_area_selection_changed_in_view(self._selected_areas)
            elif self.View == ViewWidget.AreasView:
                self._selected_areas = []
                self.update()
                self.parent().on_area_selection_changed_in_view(self._selected_areas)
        if self.View == ViewWidget.ComponentsView:
            if self._selected_component is not None:
                if self._selected_component.type == Component.LineComponent:
                    if self._edge_hover is not None:
                        if self._edge_hover not in self._selected_component.get_elements():
                            self._selected_edges.append(self._edge_hover)
                            self._selected_component.add_element(self._edge_hover)
                        else:
                            self._selected_edges.remove(self._edge_hover)
                            self._selected_component.remove_element(self._edge_hover)
                if self._selected_component.type == Component.AreaComponent:
                    if self._area_hover is not None:
                        if self._area_hover not in self._selected_component.get_elements():
                            self._selected_areas.append(self._area_hover)
                            self._selected_component.add_element(self._area_hover)
                        else:
                            self._selected_areas.remove(self._area_hover)
                            self._selected_component.remove_element(self._area_hover)
        if self.View == ViewWidget.MarginsView:
            if self._selected_margin is not None:
                if self._edge_hover is not None:
                    if self._edge_hover in self._selected_edges:
                        self._selected_edges.remove(self._edge_hover)
                        self._selected_margin.remove_edges([self._edge_hover])
                    else:
                        self._selected_edges.append(self._edge_hover)
                        self._selected_margin.add_edge(self._edge_hover)
        if self.View == ViewWidget.MeshView:
            if self._selected_mesh_def is not None:
                if MeshDefinition.EdgeElementDivisionDefinition <= self._selected_mesh_def.type <= MeshDefinition.EdgeElementSizeDefinition:
                    if self._edge_hover is not None:
                        if self._edge_hover in self._selected_edges:
                            self._selected_edges.remove(self._edge_hover)
                            self._selected_mesh_def.remove_elements([self._edge_hover])
                        else:
                            self._selected_edges.append(self._edge_hover)
                            self._selected_mesh_def.add_element(self._edge_hover)
                elif self._selected_mesh_def.type == MeshDefinition.AreaElementSizeDefinition:
                    if self._area_hover is not None:
                        if self._area_hover not in self._selected_areas:
                            self._selected_areas.append(self._area_hover)
                            self._selected_mesh_def.add_element(self._area_hover)
                        else:
                            self._selected_areas.remove(self._area_hover)
                            self._selected_mesh_def.remove_elements([self._area_hover])
        if self.View == ViewWidget.SweepsView:
            if self._selected_sweep_def is not None:
                if self._edge_hover is not None:
                    if self._edge_hover in self._selected_edges:
                        self._selected_edges.remove(self._edge_hover)
                        self._selected_sweep_def.remove_elements([self._edge_hover])
                    else:
                        self._selected_edges.append(self._edge_hover)
                        self._selected_sweep_def.add_element(self._edge_hover)
                if self._area_hover is not None:
                    if self._area_hover not in self._selected_areas:
                        self._selected_areas.append(self._area_hover)
                        self._selected_sweep_def.add_element(self._area_hover)
                    else:
                        self._selected_areas.remove(self._area_hover)
                        self._selected_sweep_def.remove_elements([self._area_hover])
        if self.View == ViewWidget.EdgesView:
            if self._draw_line_edge:
                doc = self._doc
                edges_object = doc.get_edges()
                if self._kp_hover is None:
                    coincident_threshold = 5/scale
                    kp = Business.create_key_point(doc, x, y, 0.0, coincident_threshold)
                    self._selected_key_points.append(kp)
                if len(self._selected_key_points) == 2:
                    edges_object.create_line_edge(self._selected_key_points[0], self._selected_key_points[1])
                    self._selected_key_points.clear()
            if self._set_fillet_kp:
                if self._kp_hover is not None:
                    doc = self._doc
                    edges = self._kp_hover.get_edges()
                    if len(edges) == 2:
                        param_name = "New Fillet radius"
                        param = self._doc.get_parameters().get_parameter_by_name(param_name)
                        if param is None:
                            param = self._doc.get_parameters().create_parameter(param_name, 1.0)
                        Business.create_fillet(self._doc, self._kp_hover, param)
                    else:
                        pass
                    # self._set_fillet_kp = False

    def check_edge_loop(self):
        branches = Business.find_all_areas(self._selected_edges)
        for branch in branches:
            if branch['enclosed']:
                Business.create_area(self._doc, branch)

                self.on_escape()
                break

    def mouseReleaseEvent(self, q_mouse_event):
        if q_mouse_event.button() == 4:
            self.middle_button_hold = False
            return
        if q_mouse_event.button() == 1:
            self.left_button_hold = False
            self._kp_move = None
            return

    def eventFilter(self, obj, event):

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self.on_delete()
                return True
            if event.key() == Qt.Key_Control:
                self._multi_select = True
            if event.key() == Qt.Key_Escape:
                self.on_escape()
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Control:
                self._multi_select = False
        if event.type() == QEvent.GraphicsSceneMouseDoubleClick:
            print("double click")

        return False

    def zoom_extends(self):
        x_min = 1e12
        x_max = -1e12
        y_min = 1e12
        y_max = -1e12
        y_scale = 1
        x_scale = 1
        if self.View != self.GeometryView:
            kps = self._doc.get_edges().get_key_points()
            for kp_tuple in kps:
                kp = kp_tuple[1]
                x_min = min(kp.x, x_min)
                x_max = max(kp.x, x_max)
                y_min = min(kp.y, y_min)
                y_max = max(kp.y, y_max)
        else:
            geom = self._doc.get_geometry()
            edges = geom.get_edges()
            for edge in edges:
                if edge['Type'] == Geometry.LineEdge:
                    x1 = edge['vertexes'][0]['xyz'][0]
                    y1 = edge['vertexes'][0]['xyz'][1]
                    x2 = edge['vertexes'][1]['xyz'][0]
                    y2 = edge['vertexes'][1]['xyz'][1]
                    x_min = min(x1, x_min)
                    x_max = max(x1, x_max)
                    y_min = min(y1, y_min)
                    y_max = max(y1, y_max)
                    x_min = min(x2, x_min)
                    x_max = max(x2, x_max)
                    y_min = min(y2, y_min)
                    y_max = max(y2, y_max)
                elif edge['Type'] == Geometry.ArcEdge:
                    x = edge['vertexes'][0]['xyz'][0]
                    y = edge['vertexes'][0]['xyz'][1]
                    x_min = min(x, x_min)
                    x_max = max(x, x_max)
                    y_min = min(y, y_min)
                    y_max = max(y, y_max)

        if (y_max - y_min) != 0:
            y_scale = self.height() / (y_max - y_min)
        if (x_max - x_min) != 0:
            x_scale = self.width() / (x_max - x_min)
        scale = min(y_scale, x_scale)*0.9
        self._offset.x = -(x_min + (x_max - x_min) / 2)
        self._offset.y = -(y_min + (y_max - y_min) / 2)
        self._scale = scale
        self.update()

    def on_delete(self):
        txt = "Are you sure you want to delete these geometries?"
        ret = QMessageBox.warning(self, "Delete geometries?", txt, QMessageBox.Yes | QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            Business.remove_key_points(self._doc, self._selected_key_points)
            Business.remove_edges(self._doc, self._selected_edges)
            Business.remove_areas(self._doc, self._selected_areas)
            self._selected_key_points.clear()
            self._selected_edges.clear()
            self._selected_areas.clear()

    def on_escape(self):
        self._set_similar_x = False
        self._set_similar_y = False
        self._draw_line_edge = False
        self._create_area = False
        self._set_fillet_kp = False
        if self.View == ViewWidget.EdgesView or self.View == ViewWidget.AreasView:
            self._selected_areas.clear()
            self._selected_edges.clear()
            self._selected_key_points.clear()
            self.parent().on_area_selection_changed_in_view(self._selected_areas)
            self.parent().on_edge_selection_changed_in_view(self._selected_edges)
            self.parent().on_kp_selection_changed_in_view(self._selected_key_points)
            self.update()
        self._main_window.update_ribbon_state()

    def on_add_line(self):
        self.on_escape()
        self._select_kp = True
        self._draw_line_edge = True
        self._main_window.update_ribbon_state()

    def on_add_fillet(self):
        self.on_escape()
        self._select_kp = True
        self._set_fillet_kp = True
        self._main_window.update_ribbon_state()

    @property
    def draw_line_edge(self):
        return self._draw_line_edge

    @property
    def add_fillet_edge(self):
        return self._set_fillet_kp

    def on_set_similar_x_coordinates(self):
        self.on_escape()
        self._set_similar_x = True
        self._select_kp = True
        self._main_window.update_ribbon_state()

    @property
    def set_sim_x(self):
        return self._set_similar_x

    def on_set_similar_y_coordinates(self):
        self.on_escape()
        self._set_similar_y = True
        self._select_kp = True
        self._main_window.update_ribbon_state()

    @property
    def set_sim_y(self):
        return self._set_similar_y

    def set_selected_material(self, material):
        self._selected_material = material
        self._selected_areas.clear()
        self._selected_edges.clear()
        if material is not None:
            for area in material.get_areas():
                self._selected_areas.append(area)
            self.parent().on_area_selection_changed_in_view(self._selected_areas)
            self.update()

    def wheelEvent(self, event):
        if self.mouse_position is not None:
            delta = event.angleDelta().y() / 8
            if self._scale + self._scale * (delta * 0.01) > 0:
                self._scale += self._scale * (delta * 0.01)
                width = self.width() / 2
                height = self.height() / 2
                scale = self._scale
                x = self.mouse_position.x() - width
                y = self.mouse_position.y() - height
                distx = x / scale
                disty = y / scale
                self._offset.x -= distx * (delta * 0.01)
                self._offset.y += disty * (delta * 0.01)
                self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        p1 = QPoint(0, 0)
        p2 = QPoint(self.width(), self.height())
        p3 = QPoint(0, self.height())
        gradient = QLinearGradient(p1, p3)
        if self._is_dark_theme:
            gradient.setColorAt(0, QColor(80, 80, 90))
            gradient.setColorAt(1, QColor(50, 50, 60))
        else:
            gradient.setColorAt(0, QColor(220, 220, 230))
            gradient.setColorAt(1, QColor(170, 170, 180))
        qp.fillRect(event.rect(), gradient)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        self.draw_content(event, qp)
        qp.end()

    def draw_content(self, event, qp):
        self.draw_functions[self.View](event, qp)

    def draw_geometry(self, event, qp):
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        geom = self._doc.get_geometry()
        edges = geom.get_edges()
        for edge in edges:
            if edge['Type'] == Geometry.LineEdge:
                x1 = (edge['vertexes'][0]['xyz'][0] + self._offset.x) * scale + width
                y1 = -(edge['vertexes'][0]['xyz'][1] + self._offset.y) * scale + height
                x2 = (edge['vertexes'][1]['xyz'][0] + self._offset.x) * scale + width
                y2 = -(edge['vertexes'][1]['xyz'][1] + self._offset.y) * scale + height
                qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            elif edge['Type'] == Geometry.ArcEdge:
                radius = edge['vertexes'][1]['xyz'][2] * scale
                x = (edge['vertexes'][0]['xyz'][0] + self._offset.x) * scale + width + 0.5
                y = -(edge['vertexes'][0]['xyz'][1] + self._offset.y) * scale + height + 0.5
                rect = QRectF(x - radius, y - 1 * radius, radius * 2, radius * 2)
                start_angle = edge['vertexes'][1]['xyz'][0] * 180 * 16 / pi
                end_angle = edge['vertexes'][1]['xyz'][1] * 180 * 16 / pi + 1
                span = end_angle - start_angle
                if span < 0:
                    span += 2 * 180 * 16
                qp.drawArc(rect, start_angle, span)

    def draw_edges(self, event, qp):
        edge_hover_pen = QPen(QtGui.QColor(100, 100, 200), 4)
        normal_pen = QPen(QtGui.QColor(0, 0, 0), 2)
        select_pen_high = QPen(QtGui.QColor(255, 0, 0), 6)
        select_pen = QPen(QtGui.QColor(255, 255, 255), 2)
        if self._is_dark_theme:
            axis_pen = QPen(QtGui.QColor(40, 50, 80), 1)
            kp_pen = QPen(QtGui.QColor(0, 200, 200), 1)
            kp_pen_hl = QPen(QtGui.QColor(190, 0, 0), 3)
            kp_pen_hover = QPen(QtGui.QColor(0, 60, 150), 3)
        else:
            axis_pen = QPen(QtGui.QColor(140, 150, 180), 1)
            kp_pen = QPen(QtGui.QColor(0, 100, 200), 1)
            kp_pen_hl = QPen(QtGui.QColor(180, 50, 0), 3)
            kp_pen_hover = QPen(QtGui.QColor(0, 120, 255), 3)
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        edges_object = self._doc.get_edges()
        edges = edges_object.get_edges()

        cx = self._offset.x * scale + width
        cy = -self._offset.y * scale + height
        qp.setPen(axis_pen)
        if self.width() > cx > 0:
            qp.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
        if self.height() > cy > 0:
            qp.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

        qp.setPen(normal_pen)
        for edge_tuple in edges:
            edge = edge_tuple[1]
            self.draw_edge(edge, qp, scale, height, width)

        for edge in self._selected_edges:
            qp.setPen(select_pen_high)
            self.draw_edge(edge, qp, scale, height, width)

        for edge in self._selected_edges:
            qp.setPen(select_pen)
            self.draw_edge(edge, qp, scale, height, width)

        if self._edge_hover is not None:
            qp.setPen(edge_hover_pen)
            self.draw_edge(self._edge_hover, qp, scale, height, width)
        qp.setPen(normal_pen)

        key_points = edges_object.get_key_points()
        for kp_tuple in key_points:
            qp.setPen(kp_pen)
            key_point = kp_tuple[1]
            x1 = (key_point.x + self._offset.x) * scale + width
            y1 = -(key_point.y + self._offset.y) * scale + height
            if self._set_similar_x or self._set_similar_y:
                if key_point in self._similar_coords:
                    qp.setPen(kp_pen_hl)
            if self._kp_hover is key_point and self._select_kp:
                qp.setPen(kp_pen_hover)

            if self.show_key_points or self._kp_hover is key_point or self._set_similar_x or self._set_similar_y:
                qp.drawEllipse(QPointF(x1, y1), 4, 4)

        qp.setPen(kp_pen_hl)
        for key_point in self._selected_key_points:
            x1 = (key_point.x + self._offset.x) * scale + width
            y1 = -(key_point.y + self._offset.y) * scale + height
            qp.drawEllipse(QPointF(x1, y1), 4, 4)

    def draw_kp(self, qp, key_point, scale, width, height):
        x1 = (key_point.x + self._offset.x) * scale + width
        y1 = -(key_point.y + self._offset.y) * scale + height
        qp.drawEllipse(QPointF(x1, y1), 4, 4)

    def draw_areas(self, event, qp: QPainter):
        normal_pen = QPen(QtGui.QColor(0, 0, 0), 2)
        areas_object = self._doc.get_areas()
        areas = areas_object.get_areas()
        qp.setPen(normal_pen)
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale

        for area_tuple in areas:
            area = area_tuple[1]
            self.draw_area(area, qp, scale, height, width)

        for area_tuple in areas:
            area = area_tuple[1]
            if area not in self._selected_areas:
                for edge_tuple in area.get_edges():
                    edge = edge_tuple  # [1]
                    self.draw_edge(edge, qp, scale, height, width)
        self.draw_edges(event, qp)

    def draw_area(self, area, qp, scale, height, width):
        path = QPainterPath()
        first_kp = True
        x_max = 0
        y_max = 0
        x_min = 0
        y_min = 0
        counter = 0
        for kp in area.get_key_points():
            x = (kp.x + self._offset.x) * scale + width
            y = -(kp.y + self._offset.y) * scale + height
            if first_kp:
                path.moveTo(QPointF(x, y))
                first_kp = False
                x_max = x
                y_max = y
                x_min = x
                y_min = y
            else:
                edge = area.get_edges()[counter - 1]
                if edge.type == Edge.ArcEdge:
                    center_kp = edge.get_key_points()[0]
                    cx = (center_kp.x + self._offset.x) * scale + width
                    cy = -(center_kp.y + self._offset.y) * scale + height
                    radius = edge.get_meta_data('r')
                    start_angle = edge.get_meta_data('sa')
                    end_angle = edge.get_meta_data('ea')
                    diff = (x - (cx + cos(end_angle) * radius * scale)) + (y - (cy - sin(end_angle) * radius * scale))
                    end_angle *= 180 / pi
                    start_angle *= 180 / pi
                    sweep_length = end_angle - start_angle
                    if abs(diff) > 0.01 * radius * scale:
                        start_angle = end_angle
                        sweep_length = -sweep_length

                    path.arcTo(cx - radius * scale, cy - radius * scale, scale * radius * 2, scale * radius * 2, start_angle, sweep_length)
                else:
                    path.lineTo(QPointF(x, y))
                if x > x_max:
                    x_max = x
                if x < x_min:
                    x_min = x
                if y > y_max:
                    y_max = y
                if y < y_min:
                    y_min = y
            counter += 1

        if area in self._selected_areas:
            qp.fillPath(path, QBrush(QtGui.QColor(150, 150, 250, 180)))
        elif area == self._area_hover:
            qp.fillPath(path, QBrush(QtGui.QColor(150, 150, 180, 180)))
        else:
            qp.fillPath(path, QBrush(QtGui.QColor(150, 150, 150, 80)))

        if self.show_area_names:
            if x_max - x_min < (y_max - y_min) * 0.75:
                qp.rotate(-90)
                qp.drawText(QRectF(-y_min, x_min, y_min - y_max, x_max - x_min), Qt.AlignCenter, area.name)
                qp.rotate(90)
            else:
                qp.drawText(QRectF(x_min, y_min, x_max - x_min, y_max - y_min), Qt.AlignCenter, area.name)

    def draw_edge(self, edge, qp, scale, height, width):
        if edge is not None:
            key_points = edge.get_key_points()
            if edge.type == Edge.LineEdge:
                edges_list = key_points[0].get_edges()
                fillet1 = None
                other_edge1 = None
                for edge_item in edges_list:
                    if edge_item.type == Edge.FilletLineEdge:
                        fillet1 = edge_item
                    elif edge_item is not edge:
                        other_edge1 = edge_item
                edges_list = key_points[1].get_edges()
                fillet2 = None
                other_edge2 = None
                for edge_item in edges_list:
                    if edge_item.type == Edge.FilletLineEdge:
                        fillet2 = edge_item
                    elif edge_item is not edge:
                        other_edge2 = edge_item
                fillet_offset_x = 0
                fillet_offset_y = 0

                if fillet1 is not None and other_edge1 is not None:
                    r = fillet1.get_meta_data("r")
                    a1 = edge.angle(key_points[0])
                    kp1 = edge.get_other_kp(key_points[0])
                    kp2 = other_edge1.get_other_kp(key_points[0])
                    abtw = key_points[0].angle_between_positive_minimized(kp1, kp2)
                    dist = -tan(abtw/2+pi/2)*r
                    fillet_offset_x = dist * cos(a1)
                    fillet_offset_y = dist * sin(a1)

                x1 = (key_points[0].x + fillet_offset_x + self._offset.x) * scale + width
                y1 = -(key_points[0].y + fillet_offset_y + self._offset.y) * scale + height

                fillet_offset_x = 0
                fillet_offset_y = 0

                if fillet2 is not None and other_edge2 is not None:
                    r = fillet2.get_meta_data("r")
                    a1 = edge.angle(key_points[1])
                    kp1 = edge.get_other_kp(key_points[1])
                    kp2 = other_edge2.get_other_kp(key_points[1])
                    abtw = key_points[1].angle_between_positive_minimized(kp2, kp1)
                    dist = -tan(abtw / 2+pi/2) * r
                    fillet_offset_x = dist * cos(a1)
                    fillet_offset_y = dist * sin(a1)

                x2 = (key_points[1].x + fillet_offset_x + self._offset.x) * scale + width
                y2 = -(key_points[1].y + fillet_offset_y + self._offset.y) * scale + height
                qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            elif edge.type == Edge.ArcEdge:
                cx = (key_points[0].x + self._offset.x) * scale + width
                cy = -(key_points[0].y + self._offset.y) * scale + height
                radius = edge.get_meta_data("r") * scale
                rect = QRectF(cx - radius, cy - 1 * radius, radius * 2, radius * 2)
                start_angle = edge.get_meta_data("sa") * 180 * 16 / pi
                end_angle = edge.get_meta_data("ea") * 180 * 16 / pi
                span = end_angle - start_angle
                if span < 0:
                    span += 2 * 180 * 16
                qp.drawArc(rect, start_angle, span)
            elif edge.type == Edge.FilletLineEdge:
                kp = key_points[0]
                edges_list = kp.get_edges()
                edges_list.remove(edge)
                if len(edges_list) > 1:
                    edge1 = edges_list[0]
                    edge2 = edges_list[1]
                    kp1 = edge1.get_other_kp(kp)
                    kp2 = edge2.get_other_kp(kp)
                    angle_between = kp.angle_between_untouched(kp1, kp2)
                    radius = edge.get_meta_data("r")
                    dist = radius / sin(angle_between/2)
                    radius *= scale
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
                    cx = (key_points[0].x + dist * cos(angle) + self._offset.x) * scale + width
                    cy = -(key_points[0].y + dist * sin(angle) + self._offset.y) * scale + height
                    rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

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
                    qp.drawArc(rect, start_angle, span)

    def draw_materials(self, event, qp: QPainter):
        self.draw_areas(event, qp)

    def draw_components(self, event, qp):
        self.draw_areas(event, qp)

    def draw_margins(self, event, qp):
        self.draw_areas(event, qp)
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        edges, kps = self._doc.get_margins().get_offset_edges_and_kps()
        for edge_tuple in edges.items():
            edge = edge_tuple[1]['edge']
            key_points = edge.get_end_key_points()
            if edge.type == Edge.LineEdge:
                kp1 = key_points[0]
                kp2 = key_points[1]
                if 'okp' in kps[kp1.uid]:
                    okp1 = kps[kp1.uid]['okp']
                else:
                    okp1 = kp1
                if 'okp' in kps[kp2.uid]:
                    okp2 = kps[kp2.uid]['okp']
                else:
                    okp2 = kp2
                x1 = (okp1.x + self._offset.x) * scale + width
                y1 = -(okp1.y + self._offset.y) * scale + height
                x2 = (okp2.x + self._offset.x) * scale + width
                y2 = -(okp2.y + self._offset.y) * scale + height

                qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            elif edge.type == Edge.ArcEdge:
                kp1 = key_points[0]
                kp2 = key_points[1]
                margin = 0
                if 'okp' in kps[kp1.uid]:
                    okp1 = kps[kp1.uid]['okp']
                    margin = kps[kp1.uid]['margin']
                else:
                    okp1 = kp1
                if 'okp' in kps[kp2.uid]:
                    okp2 = kps[kp2.uid]['okp']
                    margin += kps[kp1.uid]['margin']
                    margin /= 2
                else:
                    okp2 = kp2
                ckp = edge.get_key_points()[0]
                convex = edge_tuple[1]['convex']
                if convex:
                    radius = (margin + edge.get_meta_data("r"))
                else:
                    radius = (edge.get_meta_data("r") - margin)
                dist = okp1.distance(okp2)
                radius = max(dist/2, radius)
                span = asin(dist/(2*radius))*2
                middle = (okp1.xyz + okp2.xyz)/2
                dist_to_center = cos(span/2)*radius
                alpha = okp1.angle2d(okp2) + pi / 2
                center_kp = Vertex(middle[0] + cos(alpha) * dist_to_center, middle[1] + sin(alpha) * dist_to_center)

                cx = (center_kp.x + self._offset.x) * scale + width
                cy = -(center_kp.y + self._offset.y) * scale + height
                radius *= scale
                rect = QRectF(cx - radius, cy - radius, radius * 2 - 0.5, radius * 2 - 0.5)
                span *= 180 * 16 / pi
                if span < 0:
                    span += 2 * 180 * 16
                start_angle = center_kp.angle2d(okp1) * 180 * 16 / pi
                qp.drawArc(rect, start_angle, span)

    def draw_mesh(self, event, qp):
        self.draw_areas(event, qp)

    def draw_sweeps(self, event, qp: QPainter):
        self.draw_areas(event, qp)
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        sweeps_object = self._doc.get_sweeps()
        sweep_lines = sweeps_object.get_sweeps_lines()
        for sweep_line in sweep_lines:
            length = len(sweep_line)
            meta = sweep_line[length - 1]
            sfak = meta['sfak']
            for int_edge in sweep_line:
                if type(int_edge) is list:
                    self.draw_kp(qp, int_edge[1], scale, width, height)
            x1 = (sweep_line[0][1].x + self._offset.x) * scale + width
            y1 = -(sweep_line[0][1].y + self._offset.y) * scale + height
            x2 = (sweep_line[1][1].x + self._offset.x) * scale + width
            y2 = -(sweep_line[1][1].y + self._offset.y) * scale + height
            qp.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            if self.show_sfak_values:
                qp.drawText(QPointF((x1+x2)/2-12, (y1+y2)/2-3), "%.2f" % sfak)

    def on_document_changed(self, event):
        self.update()

    @staticmethod
    def generate_random_color():
        r = int(random.random() * 255)
        g = int(random.random() * 255)
        b = int(random.random() * 255)
        maxval = max(max(r, g), b)
        r *= 255 / maxval
        g *= 255 / maxval
        b *= 255 / maxval
        return r, g, b

    def on_area_selection_changed(self, selected_areas):
        self._selected_areas = selected_areas
        self.update()

    def on_edge_selection_changed(self, selected_edges):
        self._selected_edges = selected_edges
        self.update()

    def on_kp_selection_changed(self, selected_key_points):
        self._selected_key_points = selected_key_points
        self.update()

    def get_selected_material(self):
        return self._selected_material

    def set_selected_component(self, selected_component):
        self._selected_component = selected_component
        self._selected_areas.clear()
        self._selected_edges.clear()
        if selected_component is not None:
            if selected_component.type == Component.AreaComponent:
                for area in selected_component.get_elements():
                    self._selected_areas.append(area)
            elif selected_component.type == Component.LineComponent:
                for edge in selected_component.get_elements():
                    self._selected_edges.append(edge)
        self.update()

    def set_selected_margin(self, selected_margin):
        self._selected_margin = selected_margin
        self._selected_areas.clear()
        self._selected_edges.clear()
        if selected_margin is not None:
            for edge in selected_margin.get_edges():
                self._selected_edges.append(edge)
        self.update()

    def on_create_area(self):
        self.on_escape()
        self._create_area = True
        self._doc.set_status("Select edges for new area")
        self._main_window.update_ribbon_state()

    @property
    def create_area(self):
        return self._create_area

    def on_create_mesh_def(self):
        self._selected_areas.clear()
        self._selected_edges.clear()
        self.update()

    def set_selected_mesh_definition(self, selected_mesh_def):
        self._selected_mesh_def = selected_mesh_def
        self._selected_areas.clear()
        self._selected_edges.clear()
        if selected_mesh_def is not None:
            if MeshDefinition.EdgeElementDivisionDefinition <= selected_mesh_def.type <= MeshDefinition.EdgeElementSizeDefinition:
                for element in selected_mesh_def.get_elements():
                    self._selected_edges.append(element)
            else:
                for element in selected_mesh_def.get_elements():
                    self._selected_areas.append(element)
        self.update()

    def set_selected_sweep_definition(self, selected_sweep_def):
        self._selected_sweep_def = selected_sweep_def
        self._selected_areas.clear()
        self._selected_edges.clear()
        if selected_sweep_def is not None:
            for element in selected_sweep_def.get_elements():
                if type(element) is Area:
                    self._selected_areas.append(element)
                if type(element) is Edge:
                    self._selected_edges.append(element)
        self.update()
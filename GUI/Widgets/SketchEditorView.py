from math import *

from PyQt5.QtCore import QEvent, QPoint
from PyQt5.QtGui import QColor, QLinearGradient
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, QWidget

from Business.SketchActions import *

from Data.Vertex import Vertex
from GUI import is_dark_theme
from GUI.Widgets.Drawers import *
from GUI.Widgets.SimpleDialogs import AddArcDialog


class SketchEditorViewWidget(QWidget):
    def __init__(self, parent, document, main_window):
        QWidget.__init__(self, parent)
        self._main_window = main_window
        self._states = main_window.get_states()
        self.setMouseTracking(True)
        self._doc = document
        self._is_dark_theme = is_dark_theme()
        self._sketch = None
        self._scale = 1.0
        self._offset = Vertex()
        self._mouse_position = None
        self._move_ref_pos = None
        self._pan_ref_pos = None
        self._selected_edges = []
        self._selected_key_points = []
        self._selected_texts = []
        self._selected_areas = []
        self._similar_coords = set()
        self._kp_hover = None
        self._kp_move = None
        self._edge_hover = None
        self._text_hover = None
        self.similar_threshold = 1
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                self.on_delete()
                return True
            if event.key() == Qt.Key_Control:
                self._states.multi_select = True
            if event.key() == Qt.Key_Escape:
                self.on_escape()
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Control:
                self._states.multi_select = False
        if event.type() == QEvent.GraphicsSceneMouseDoubleClick:
            print("double click")
        return False

    def on_find_all_similar(self):
        if self._sketch is not None:
            find_all_similar(self._doc, self._sketch, int(round(log10(1/self.similar_threshold))))

    def on_insert_text(self):
        self.on_escape()
        self._states.select_kp = True
        self._states.insert_text = True

    def on_zoom_fit(self):
        if self._sketch is None:
            return
        limits = self._sketch.get_limits()
        x_min = limits[0]
        x_max = limits[2]
        y_min = limits[1]
        y_max = limits[3]
        y_scale = 1
        x_scale = 1

        if (y_max - y_min) != 0:
            y_scale = self.height() / (y_max - y_min)
        if (x_max - x_min) != 0:
            x_scale = self.width() / (x_max - x_min)
        scale = min(y_scale, x_scale) * 0.9
        self._offset.x = -(x_min + (x_max - x_min) / 2)
        self._offset.y = -(y_min + (y_max - y_min) / 2)
        self._scale = scale
        self.update()

    def on_similar_thresshold_changed(self, value):
        self.similar_threshold = value

    def on_delete(self):
        txt = "Are you sure you want to delete these geometries?"
        ret = QMessageBox.warning(self, "Delete geometries?", txt, QMessageBox.Yes | QMessageBox.Cancel)
        if ret == QMessageBox.Yes:
            pass
            remove_key_points(self._doc, self._sketch, self._selected_key_points)
            remove_edges(self._doc, self._sketch, self._selected_edges)
            self._selected_key_points.clear()
            self._selected_edges.clear()

    def set_selected_key_points(self, selected_key_points):
        self._selected_key_points = selected_key_points
        self.update()

    def set_selected_edges(self, selected_edges):
        self._selected_edges = selected_edges
        self.update()

    def on_add_fillet(self):
        self.on_escape()
        if self._sketch is None:
            return
        self.setCursor(Qt.CrossCursor)
        self._states.select_kp = True
        self._states.set_fillet_kp = True
        self._main_window.update_ribbon_state()

    def on_escape(self):
        self._states.set_similar_x = False
        self._states.set_similar_y = False
        self._states.draw_line_edge = False
        self._states.create_area = False
        self._states.set_fillet_kp = False
        self._states.insert_text = False
        self._states.add_circle_edge = False
        self._states.add_attribute = False
        self._states.add_arc_edge = False
        self._states.draw_nurbs_edge = False
        self._states.select_edge = True
        self._selected_key_points.clear()
        self._selected_edges.clear()
        self.setCursor(Qt.ArrowCursor)
        self._main_window.update_ribbon_state()

    def on_set_similar_x_coordinates(self):
        self.on_escape()
        self._states.set_similar_x = True
        self._states.select_kp = True
        self._main_window.update_ribbon_state()

    def on_set_similar_y_coordinates(self):
        self.on_escape()
        self._states.set_similar_y = True
        self._states.select_kp = True
        self._main_window.update_ribbon_state()

    def on_add_line(self):
        self.on_escape()
        if self._sketch is None:
            return
        self.setCursor(Qt.CrossCursor)
        self._states.select_kp = True
        self._states.draw_line_edge = True
        self._main_window.update_ribbon_state()

    def on_add_circle(self):
        self.on_escape()
        if self._sketch is None:
            return
        self.setCursor(Qt.CrossCursor)
        self._states.select_kp = True
        self._states.add_circle_edge = True
        self._main_window.update_ribbon_state()

    def on_add_nurbs(self):
        self.on_escape()
        if self._sketch is None:
            return
        self.setCursor(Qt.CrossCursor)
        self._states.select_kp = True
        self._states.draw_nurbs_edge = True
        self._states.select_edge = False
        self._main_window.update_ribbon_state()

    def on_add_arc(self):
        self.on_escape()
        if self._sketch is None:
            return
        self.setCursor(Qt.CrossCursor)
        self._states.select_kp = True
        self._states.add_arc_edge = True
        self._main_window.update_ribbon_state()

    def on_insert_attribute(self):
        self.on_escape()
        if self._sketch is None:
            return
        self.setCursor(Qt.CrossCursor)
        self._states.select_kp = True
        self._states.add_attribute= True
        self._main_window.update_ribbon_state()

    def set_sketch(self, sketch):
        self._sketch = sketch
        self.update()

    def mouseReleaseEvent(self, q_mouse_event):
        if q_mouse_event.button() == 4:
            self._states.middle_button_hold = False
            return
        if q_mouse_event.button() == 1:
            self._states.left_button_hold = False
            self._kp_move = None
            return

    def on_create_areas(self):
        self.on_escape()
        if self._sketch is None:
            return
        go = False
        if len(self._sketch.get_areas()) > 0:
            txt = "This will replace all existing areas with new areas generated from the edges."
            txt += "Are you sure you want to do this?"
            ret = QMessageBox.warning(self, "Create areas?", txt, QMessageBox.Yes | QMessageBox.Cancel)
            if ret == QMessageBox.Yes:
                go = True
        else:
            go = True
        if go:
            create_all_areas(self._doc, self._sketch)
            self.update()

    def on_create_area(self):
        self.on_escape()
        self._states.create_area = True
        self._doc.set_status("Select edges for new area")
        self._main_window.update_ribbon_state()

    def check_edge_loop(self):
        branches = find_all_areas(self._selected_edges)
        for branch in branches:
            if branch['enclosed']:
                create_area(self._sketch, branch)
                self.on_escape()
                self.update()
                break

    def mouseMoveEvent(self, q_mouse_event):
        position = q_mouse_event.pos()
        update_view = False
        if self._mouse_position is not None:
            mouse_move_x = self._mouse_position.x() - position.x()
            mouse_move_y = self._mouse_position.y() - position.y()
        else:
            mouse_move_x = 0
            mouse_move_y = 0
        self._mouse_position = position
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale
        x = (self._mouse_position.x() - width) / scale - self._offset.x
        y = -((self._mouse_position.y() - height) / scale + self._offset.y)
        sketch = self._sketch
        if sketch is None:
            return
        key_points = sketch.get_key_points()
        if self._states.middle_button_hold:
            self._offset.x -= mouse_move_x/scale
            self._offset.y += mouse_move_y/scale
            update_view = True
        if self._states.left_button_hold:
            if self._kp_move is not None:
                if self._kp_move.get_x_parameter() is None:
                    self._kp_move.x = x
                    update_view = True
                if self._kp_move.get_y_parameter() is None:
                    self._kp_move.y = y
                    update_view = True
        self._kp_hover = None
        self._edge_hover = None
        self._text_hover = None
        if self._states.select_kp:
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                x1 = key_point.x
                y1 = key_point.y
                if abs(x1 - x) < 5 / scale and abs(y1 - y) < 5 / scale:
                    self._kp_hover = key_point
                    update_view = True
                    break

        if self._states.select_edge and self._kp_hover is None:
            smallest_dist = 10e10
            closest_edge = None
            for edge_tuple in sketch.get_edges():
                edge = edge_tuple[1]
                dist = edge.distance(Vertex(x, y, 0))
                if dist < smallest_dist:
                    smallest_dist = dist
                    closest_edge = edge
            if smallest_dist * scale < 10:
                self._edge_hover = closest_edge
                update_view = True

        if self._states.select_text and self._edge_hover is None and self._kp_hover is None:
            for text_tuple in sketch.get_texts():
                text = text_tuple[1]
                key_point = text.key_point
                x1 = key_point.x
                y1 = key_point.y
                if text.horizontal_alignment == Text.Left:
                    x1 -= text.height * 2.5
                elif text.horizontal_alignment == Text.Right:
                    x1 += text.height * 2.5
                if text.vertical_alignment == Text.Top:
                    y1 -= text.height / 2
                elif text.vertical_alignment == Text.Bottom:
                    y1 += text.height / 2
                if abs(y1 - y) < text.height/2 and abs(x1 - x) < text.height*2.5:
                    self._text_hover = text
                    update_view = True
                    break

        if self._states.set_similar_x and self._kp_hover is not None:
            self._similar_coords.clear()
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                x1 = key_point.x
                if abs(x1 - self._kp_hover.x) < self.similar_threshold:
                    self._similar_coords.add(key_point)
                    update_view = True

        if self._states.set_similar_y and self._kp_hover is not None:
            self._similar_coords.clear()
            for kp_tuple in key_points:
                key_point = kp_tuple[1]
                y1 = key_point.y
                if abs(y1 - self._kp_hover.y) < self.similar_threshold:
                    self._similar_coords.add(key_point)
                    update_view = True

        if update_view:
            self.update()

    def mousePressEvent(self, q_mouse_event):
        self.setFocus()
        position = q_mouse_event.pos()
        if q_mouse_event.button() == 4:
            self._states.middle_button_hold = True
            self._pan_ref_pos = position
            return
        if q_mouse_event.button() == 1:
            self._states.left_button_hold = True
            self._move_ref_pos = position
        position = q_mouse_event.pos()

        half_width = self.width() / 2
        half_height = self.height() / 2
        scale = self._scale
        x = (self._mouse_position.x() - half_width) / scale - self._offset.x
        y = -((self._mouse_position.y() - half_height) / scale + self._offset.y)
        if self._states.set_similar_x or self._states.set_similar_y:
            params = []
            for param_tuple in self._sketch.get_all_parameters():
                params.append(param_tuple[1].name)
            value = QInputDialog.getItem(self, "Set parameter", "Parameter:", params, 0, True)
            if self._states.set_similar_x and value[1] == QDialog.Accepted:
                self._states.set_similar_x = False
                set_similar_x(self._doc, self._sketch, self._similar_coords, value[0])
            else:
                self._states.set_similar_x = False
            if self._states.set_similar_y and value[1] == QDialog.Accepted:
                self._states.set_similar_y = False
                set_similar_y(self._doc, self._sketch, self._similar_coords, value[0])
            else:
                self._states.set_similar_y = False

        if self._states.select_text:
            if self._text_hover is not None:
                if self._states.multi_select:
                    self._selected_texts.append(self._text_hover)
                else:
                    self._selected_texts = [self._text_hover]
            else:
                self._selected_texts = []
            self._main_window.on_text_selection_changed_in_view(self._selected_texts)

        if self._states.left_button_hold and self._kp_hover is not None:
            if self._kp_hover in self._selected_key_points:
                self._kp_move = self._kp_hover
        if self._states.select_edge and self._edge_hover is not None and self._kp_hover is None:
            if self._states.multi_select:
                if self._edge_hover in self._selected_edges:
                    self._selected_edges.remove(self._edge_hover)
                else:
                    self._selected_edges.append(self._edge_hover)
            else:
                self._selected_edges = [self._edge_hover]
            self.update()
            self._main_window.on_edge_selection_changed_in_view(self._selected_edges)
        elif self._states.select_edge and self._edge_hover is None:
            self._selected_edges = []
            self.update()
            self._main_window.on_edge_selection_changed_in_view(self._selected_edges)

        if self._kp_hover is not None and self._states.select_kp:
            if self._states.multi_select or self._states.draw_line_edge or self._states.set_fillet_kp:
                self._selected_key_points.append(self._kp_hover)
            else:
                self._selected_key_points = [self._kp_hover]
            self.update()
            self._main_window.on_kp_selection_changed_in_view(self._selected_key_points)
        elif self._kp_hover is None and self._states.select_kp and len(self._selected_edges) == 0 and not self._states.draw_line_edge:
            self._selected_key_points = []
            self.update()
            self._main_window.on_kp_selection_changed_in_view(self._selected_key_points)

        if self._states.draw_line_edge:
            doc = self._doc
            sketch = self._sketch
            if self._kp_hover is None:
                coincident_threshold = 5/scale
                kp = create_key_point(doc, sketch, x, y, 0.0, coincident_threshold)
                self._selected_key_points.append(kp)
            if len(self._selected_key_points) == 2:
                sketch.create_line_edge(self._selected_key_points[0], self._selected_key_points[1])
                if not self._states.multi_select:
                    self._selected_key_points.clear()
                    self.on_escape()
                else:
                    self._selected_key_points.remove(self._selected_key_points[0])
        if self._states.draw_nurbs_edge:
            doc = self._doc
            sketch = self._sketch
            if self._kp_hover is None:
                coincident_threshold = 5/scale
                kp = create_key_point(doc, sketch, x, y, 0.0, coincident_threshold)
                self._selected_key_points.append(kp)
            else:
                kp = self._kp_hover
            if len(self._selected_edges) == 0:
                nurbs_edge = create_nurbs_edge(doc, sketch, kp)
                self._selected_edges.append(nurbs_edge)
            else:
                nurbs_edge = self._selected_edges[0]
                nurbs_edge.add_key_point(kp)

        if self._states.set_fillet_kp:
            if self._kp_hover is not None:
                edges = self._kp_hover.get_edges()
                if len(edges) != 2:
                    self._selected_key_points.remove(self._kp_hover)
                if not self._states.multi_select:
                    params = []
                    params.sort()
                    for param_tuple in self._sketch.get_all_parameters():
                        params.append(param_tuple[1].name)
                    value = QInputDialog.getItem(self, "Set radius parameter", "Parameter:", params, 0, True)
                    if value[1] == QDialog.Accepted:
                        radius_param = self._sketch.get_parameter_by_name(value[0])
                        if radius_param is None:
                            radius_param = self._sketch.create_parameter(value[0], 1.0)
                            for kp in self._selected_key_points:
                                create_fillet(self._doc, self._sketch, kp, radius_param)
                            self.on_escape()
                else:
                    pass
        if self._states.add_text:
            coincident_threshold = 5 / scale
            kp = create_key_point(self._doc, self._sketch, x, y, 0.0, coincident_threshold)
            create_text(self._doc, self._sketch, kp, "New Text", 0.003)
            self.on_escape()
        if self._states.add_circle_edge:
            coincident_threshold = 5 / scale
            kp = create_key_point(self._doc, self._sketch, x, y, 0.0, coincident_threshold)
            params = []
            params.sort()
            for param_tuple in self._sketch.get_all_parameters():
                params.append(param_tuple[1].name)
            value = QInputDialog.getItem(self, "Set radius parameter", "Parameter:", params, 0, True)
            if value[1] == QDialog.Accepted:
                radius_param = self._sketch.get_parameter_by_name(value[0])
                if radius_param is None:
                    radius_param = self._sketch.create_parameter(value[0], 1.0)
                create_circle(self._doc, self._sketch, kp, radius_param)
            self.on_escape()
        if self._states.add_arc_edge:
            coincident_threshold = 5 / scale
            add_arc_widget = AddArcDialog(self, self._sketch)
            result = add_arc_widget.exec_()
            if result == QDialog.Accepted:
                kp = create_key_point(self._doc, self._sketch, x, y, 0.0, coincident_threshold)
                radius_param = self._sketch.get_parameter_by_name(add_arc_widget.radius_param())
                start_angle_param = self._sketch.get_parameter_by_name(add_arc_widget.start_angle_param())
                end_angle_param = self._sketch.get_parameter_by_name(add_arc_widget.end_angle_param())
                if radius_param is None:
                    radius_param = self._sketch.create_parameter(add_arc_widget.radius_param(), 1.0)
                if start_angle_param is None:
                    start_angle_param = self._sketch.create_parameter(add_arc_widget.start_angle_param(), 0.0)
                if end_angle_param is None:
                    end_angle_param = self._sketch.create_parameter(add_arc_widget.end_angle_param(), pi)
                add_arc(self._doc, self._sketch, kp, radius_param, start_angle_param, end_angle_param)
            self.on_escape()

        if self._states.add_attribute:
            coincident_threshold = 5 / scale
            kp = create_key_point(self._doc, self._sketch, x, y, 0.0, coincident_threshold)
            create_attribute(self._doc, self._sketch, kp, "Attribute name", "Default value", 0.007)
            self.on_escape()

        if self._states.create_area:
            self.check_edge_loop()

    def wheelEvent(self, event):
        if self._mouse_position is not None:
            delta = event.angleDelta().y() / 8
            if self._scale + self._scale * (delta * 0.01) > 0:
                self._scale += self._scale * (delta * 0.01)
                width = self.width() / 2
                height = self.height() / 2
                scale = self._scale
                x = self._mouse_position.x() - width
                y = self._mouse_position.y() - height
                distx = x / scale
                disty = y / scale
                self._offset.x -= distx * (delta * 0.01)
                self._offset.y += disty * (delta * 0.01)
                self.update()

    def paintEvent(self, event):
        qp = QPainter()
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
        qp.setRenderHint(QPainter.Antialiasing)
        self.draw_areas(event, qp)
        self.draw_edges(event, qp)
        self.draw_texts(event, qp)
        qp.end()

    def draw_texts(self, event, qp: QPainter):
        if self._sketch is None:
            return
        sc = self._scale
        half_width = self.width() / 2
        half_height = self.height() / 2
        center = Vertex(half_width, half_height)
        normal_pen = QPen(QColor(0, 0, 0), 2)
        kp_pen_hover = QPen(QColor(0, 120, 255), 3)
        kp_pen_hl = QPen(QColor(180, 50, 0), 3)
        qp.setPen(normal_pen)
        for text_tuple in self._sketch.get_texts():
            text = text_tuple[1]
            if type(text) is Text:
                draw_text(text, qp, sc, self._offset, center)
            elif type(text) is Attribute:
                draw_attribute(text, qp, sc, self._offset, center, {})
        if self._text_hover is not None:
            qp.setPen(kp_pen_hover)
            if type(self._text_hover) is Text:
                draw_text(self._text_hover, qp, sc, self._offset, center)
            elif type(self._text_hover) is Attribute:
                draw_attribute(self._text_hover, qp, sc, self._offset, center, {})
        qp.setPen(kp_pen_hl)
        for text in self._selected_texts:
            if type(text) is Text:
                draw_text(text, qp, sc, self._offset, center)
            elif type(text) is Attribute:
                draw_attribute(text, qp, sc, self._offset, center, {})

    def draw_edges(self, event, qp):
        pens = create_pens(self._doc, 6000)
        pens_hover = create_pens(self._doc, 12000, QColor(100, 100, 200))
        pens_select_high = create_pens(self._doc, 18000, QColor(255, 0, 0))
        pens_select = create_pens(self._doc, 6000, QColor(255, 255, 255))
        if self._is_dark_theme:
            axis_pen = QPen(QColor(40, 50, 80), 1)
            kp_pen = QPen(QColor(0, 200, 200), 1)
            kp_pen_hl = QPen(QColor(190, 0, 0), 3)
            kp_pen_hover = QPen(QColor(0, 60, 150), 3)
        else:
            axis_pen = QPen(QColor(140, 150, 180), 1)
            kp_pen = QPen(QColor(0, 100, 200), 1)
            kp_pen_hl = QPen(QColor(180, 50, 0), 3)
            kp_pen_hover = QPen(QColor(0, 120, 255), 3)
        half_width = self.width() / 2
        half_height = self.height() / 2
        center = Vertex(half_width, half_height)
        scale = self._scale
        if self._sketch is None:
            return

        edges = self._sketch.get_edges()

        cx = self._offset.x * scale + half_width
        cy = -self._offset.y * scale + half_height
        qp.setPen(axis_pen)
        if self.width() > cx > 0:
            qp.drawLine(QPointF(cx, 0), QPointF(cx, self.height()))
        if self.height() > cy > 0:
            qp.drawLine(QPointF(0, cy), QPointF(self.width(), cy))

        for edge_tuple in edges:
            edge = edge_tuple[1]
            draw_edge(edge, qp, scale, self._offset, center, pens)

        for edge in self._selected_edges:
            draw_edge(edge, qp, scale, self._offset, center, pens_select_high)

        for edge in self._selected_edges:
            draw_edge(edge, qp, scale, self._offset, center, pens_select)

        if self._edge_hover is not None:
            draw_edge(self._edge_hover, qp, scale, self._offset, center, pens_hover)

        qp.setPen(pens['default'])

        key_points = self._sketch.get_key_points()
        for kp_tuple in key_points:
            qp.setPen(kp_pen)
            key_point = kp_tuple[1]

            if self._states.set_similar_x or self._states.set_similar_y:
                if key_point in self._similar_coords:
                    qp.setPen(kp_pen_hl)
            if self._kp_hover is key_point and self._states.select_kp:
                qp.setPen(kp_pen_hover)

            if self._states.show_key_points or self._kp_hover is key_point or self._states.set_similar_x or self._states.set_similar_y:
                draw_kp(qp, key_point, scale, self._offset, center)

        qp.setPen(kp_pen_hl)

        for key_point in self._selected_key_points:
            draw_kp(qp, key_point, scale, self._offset, center)

    def draw_areas(self, event, qp: QPainter):
        if self._sketch is None:
            return
        normal_pen = QPen(QColor(0, 0, 0), 2)

        areas = self._sketch.get_areas()
        qp.setPen(normal_pen)
        width = self.width() / 2
        height = self.height() / 2
        scale = self._scale

        for area_tuple in areas:
            area = area_tuple[1]
            draw_area(area, qp, scale, self._offset, height, width, True, QBrush(QColor(150, 150, 150, 80)))

        # for area_tuple in areas:
        #     area = area_tuple[1]
        #     if area not in self._selected_areas:
        #         for edge_tuple in area.get_edges():
        #             edge = edge_tuple  # [1]
                    #draw_edge(edge, qp, scale, self._offset, center, pens_select)

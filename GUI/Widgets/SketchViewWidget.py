from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget

from Data.Vertex import Vertex
from GUI.Widgets.Drawers import create_pens, draw_sketch, draw_area, draw_edge


class SketchViewWidget(QWidget):
    def __init__(self, parent, sketch, document):
        QWidget.__init__(self, parent)
        self._doc = document
        self._sketch = sketch
        self.setMinimumHeight(250)
        self.setMinimumWidth(250)
        self.setMouseTracking(True)
        self._show_areas = False
        self._areas_selectable = False
        self._edges_selectable = False
        self._change_listener = None
        self._selected_areas = []
        self._selected_edges = []
        self._area_hover = None
        self._edge_hover = None
        self._mouse_position = None

    def mouseMoveEvent(self, q_mouse_event):
        position = q_mouse_event.pos()
        if self._mouse_position is not None:
            mouse_move_x = self._mouse_position.x() - position.x()
            mouse_move_y = self._mouse_position.y() - position.y()
        else:
            mouse_move_x = 0
            mouse_move_y = 0
        self._mouse_position = position
        if self._sketch is None:
            return
        update_view = False
        if self._area_hover is not None or self._edge_hover is not None:
            update_view = True
        self._area_hover = None
        self._edge_hover = None
        width = self.width() / 2
        height = self.height() / 2
        limits = self._sketch.get_limits()
        sketch_width = limits[2] - limits[0]
        sketch_height = limits[3] - limits[1]
        scale_x = self.width() / sketch_width
        scale_y = self.height() / sketch_height
        scale = min(scale_x, scale_y) * 0.9
        offset = Vertex(-limits[0] - sketch_width / 2, -limits[1] - sketch_height / 2)
        x = (self._mouse_position.x() - width) / scale - offset.x
        y = -((self._mouse_position.y() - height) / scale + offset.y)

        if self._edges_selectable:
            smallest_dist = 10e10
            closest_edge = None
            for edge_tuple in self._sketch.get_edges():
                edge = edge_tuple[1]
                dist = edge.distance(Vertex(x, y, 0))
                if dist < smallest_dist:
                    smallest_dist = dist
                    closest_edge = edge
            if smallest_dist * scale < 10:
                self._edge_hover = closest_edge
                update_view = True
        if self._areas_selectable and self._edge_hover is None:
            for area_tuple in self._sketch.get_areas():
                area = area_tuple[1]
                if area.inside(Vertex(x, y, 0)):
                    self._area_hover = area
                    update_view = True
                    break
        if update_view:
            self.update()

    def mousePressEvent(self, q_mouse_event):
        self.setFocus()
        position = q_mouse_event.pos()
        if q_mouse_event.button() == 4:
            return
        if q_mouse_event.button() == 1:
            pass
        if self._edge_hover is not None and self._edges_selectable:
            self._selected_edges.clear()
            self._selected_edges.append(self._edge_hover)
            if self._change_listener is not None:
                self._change_listener.on_edge_selected(self._edge_hover)
            self.update()

        if self._area_hover is not None and self._areas_selectable and self._edge_hover is None:
            self._selected_areas.clear()
            self._selected_areas.append(self._area_hover)
            if self._change_listener is not None:
                self._change_listener.on_area_selected(self._area_hover)
            self.update()

    @property
    def show_areas(self):
        return self._show_areas

    @show_areas.setter
    def show_areas(self, value):
        self._show_areas = value
        self.update()

    @property
    def areas_selectable(self):
        return self._areas_selectable

    @areas_selectable.setter
    def areas_selectable(self, value):
        self._areas_selectable = value

    def set_sketch(self, sketch):
        self._sketch = sketch
        self.update()

    @property
    def edges_selectable(self):
        return self._edges_selectable

    @edges_selectable.setter
    def edges_selectable(self, value):
        self._edges_selectable = value

    def set_change_listener(self, change_listener):
        self._change_listener = change_listener

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        pens = create_pens(self._doc, 3000, QColor(0, 0, 0))
        pens_hover = create_pens(self._doc, 12000, QColor(100, 100, 200))
        pens_select_high = create_pens(self._doc, 18000, QColor(255, 0, 0))
        pens_select = create_pens(self._doc, 6000, QColor(255, 255, 255))
        qp.fillRect(event.rect(), QColor(255, 255, 255))
        half_width = self.width() / 2
        half_height = self.height() / 2
        center = Vertex(half_width, half_height)
        if self._sketch is not None:
            limits = self._sketch.get_limits()
            sketch_width = limits[2] - limits[0]
            sketch_height = limits[3] - limits[1]
            scale_x = self.width() / sketch_width
            scale_y = self.height() / sketch_height
            scale = min(scale_x, scale_y)*0.9
            offset = Vertex(-limits[0] - sketch_width/2, -limits[1] - sketch_height/2)
            draw_sketch(qp, self._sketch, scale, offset, center, pens, {})
            for edge in self._selected_edges:
                draw_edge(edge, qp, scale, offset, center, pens_select_high)
            for edge in self._selected_edges:
                draw_edge(edge, qp, scale, offset, center, pens_select)
            if self._edge_hover is not None:
                draw_edge(self._edge_hover, qp, scale, offset, center, pens_hover)
            if self._show_areas:
                qp.setPen(pens['default'])
                for area_tuple in self._sketch.get_areas():
                    draw_area(area_tuple[1], qp, scale, offset, half_height, half_width, True, QBrush(QColor(150, 150, 150, 80)))
                for area in self._selected_areas:
                    draw_area(area, qp, scale, offset, half_height, half_width, True, QBrush(QColor(150, 150, 200, 150)))
                if self._area_hover is not None:
                    draw_area(self._area_hover, qp, scale, offset, half_height, half_width, True, QBrush(QColor(150, 150, 200, 80)))
        qp.end()

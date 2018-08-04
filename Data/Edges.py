from math import *

import numpy as np

from enum import Enum
from Data.Events import ChangeEvent
from Data.Nurbs import Nurbs
from Data.Objects import IdObject
from Data.Objects import NamedObservableObject
from Data.Plane import Plane
from Data.Vertex import Vertex

class EdgeType(Enum):
  LineEdge = 1
  ArcEdge = 2
  EllipseEdge = 3
  PolyLineEdge = 4
  FilletLineEdge = 5
  CircleEdge = 6
  SplineEdge = 7
  NurbsEdge = 8

class Edge(IdObject, NamedObservableObject):
  def __init__(self, geometry, type=EdgeType.LineEdge, name="New Edge", plane=Plane()):
    IdObject.__init__(self)
    NamedObservableObject.__init__(self, name)
    self._type = type
    self._geometry = geometry
    self._key_points = []
    self._meta_data = {}
    self._meta_data_parameters = {}
    self._style = geometry.document.get_styles().get_edge_style_by_name('default')
    self._plane = plane

    self._draw_data = None

  @property
  def style(self):
    return self._style

  @property
  def type_name(self):
    return self._type.name

  @property
  def style_name(self):
    if self._style is None:
      return "No style"
    else:
      return self._style.name

  @style_name.setter
  def style_name(self, value):
    styles = self._geometry.document.get_styles()
    edge_style = styles.get_edge_style_by_name(value)
    self._style = edge_style

  @property
  def plane(self):
    return self._plane

  def delete(self):
    self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

  def set_meta_data(self, name, value):
    for param_tuple in self._meta_data_parameters.items():
      if param_tuple[1] == name:
        param = self._geometry.get_parameter_by_uid(param_tuple[0])
        param.value = value
        return
    self._meta_data[name] = value


  def get_meta_data(self, name):
    return self._meta_data[name]

  def get_meta_data_parameter(self, name):
    doc = self._geometry.document()
    for param_tuple in self._meta_data_parameters.items():
      if param_tuple[1] == name:
        return doc.get_parameters().get_parameter_by_uid(param_tuple[0])
    return None

  def set_meta_data_parameter(self, name, parameter):
    self._meta_data_parameters[parameter.uid] = name
    param = self._geometry.get_parameter_by_uid(parameter.uid)
    self._meta_data[name] = param.value
    param.add_change_handler(self.on_parameter_change)

  def on_parameter_change(self, event):
    param = event.sender
    uid = param.uid
    meta_name = self._meta_data_parameters[uid]
    self._meta_data[meta_name] = param.value
    if self._type == EdgeType.ArcEdge:
      ckp = self._geometry.get_key_point(self._key_points[0])
      self.update_linked_kps(ckp)

  def get_key_points(self):
    kps = []
    for uid in self._key_points:
      kps.append(self._geometry.get_key_point(uid))
    return kps

  def get_key_point_uids(self):
    kps = []
    for uid in self._key_points:
      kps.append(uid)
    return kps

  def get_end_key_points(self):
    if self._type == EdgeType.LineEdge:
      return self.get_key_points()
    if self._type == EdgeType.NurbsEdge:
      key_points = self.get_key_points()
      kps = [key_points[0]]
      if len(key_points) > 1:
        kps.append(key_points[len(key_points) - 1])
      else:
        kps.append(key_points[0])
      return kps
    elif self._type == EdgeType.ArcEdge:
      ckp = self._geometry.get_key_point(self._key_points[0])
      if 'start_kp' in self._meta_data:
        start_kp = self._geometry.get_key_point(self._meta_data['start_kp'])
      else:
        pm = self._plane.get_global_projection_matrix()
        x = cos(self._meta_data['sa']) * self._meta_data['r']
        y = sin(self._meta_data['sa']) * self._meta_data['r']
        z = 0
        pc1 = ckp.xyz + pm.dot(np.array([x, y, z]))
        start_kp = self._geometry.create_key_point(pc1[0], pc1[1], pc1[2], 0)
        start_kp.add_edge(self)
        start_kp.add_change_handler(self.on_key_point_changed)
        start_kp.editable = False
        self._meta_data['start_kp'] = start_kp.uid
      if 'end_kp' in self._meta_data:
        end_kp = self._geometry.get_key_point(self._meta_data['end_kp'])
      else:
        pm = self._plane.get_global_projection_matrix()
        x = cos(self._meta_data['ea']) * self._meta_data['r']
        y = sin(self._meta_data['ea']) * self._meta_data['r']
        z = 0
        pc1 = ckp.xyz + pm.dot(np.array([x, y, z]))
        end_kp = self._geometry.create_key_point(pc1[0], pc1[1], pc1[2], 0)
        end_kp.add_edge(self)
        end_kp.add_change_handler(self.on_key_point_changed)
        end_kp.editable = False
        self._meta_data['end_kp'] = end_kp.uid
      return [start_kp, end_kp]
    elif self.type == EdgeType.CircleEdge:
      return self.get_key_points()
    elif self.type == EdgeType.PolyLineEdge:
      return self.get_key_points()
    elif self.type == EdgeType.FilletLineEdge:
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
    self._draw_data = None

  def on_key_point_changed(self, event):
    if event.type == ChangeEvent.Deleted:
      event.object.remove_edge(self)
      self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))
      event.object.remove_change_handler(self.on_key_point_changed)
    self.changed(event)
    if self._type == EdgeType.ArcEdge:
      ckp = self._geometry.get_key_point(self._key_points[0])
      if event.sender == ckp:
        self.update_linked_kps(ckp)
    if self._type == EdgeType.NurbsEdge:
      self._draw_data = None

  def update_linked_kps(self, ckp):
    if self._type == EdgeType.ArcEdge:
      pm = self._plane.get_global_projection_matrix()
      x = cos(self._meta_data['ea']) * self._meta_data['r']
      y = sin(self._meta_data['ea']) * self._meta_data['r']
      z = 0
      end_kp = self._geometry.get_key_point(self._meta_data['end_kp'])
      pc1 = ckp.xyz + pm.dot(np.array([x, y, z]))
      end_kp.x = pc1[0]
      end_kp.y = pc1[1]
      end_kp.z = pc1[2]
      start_kp = self._geometry.get_key_point(self._meta_data['start_kp'])
      x = cos(self._meta_data['sa']) * self._meta_data['r']
      y = sin(self._meta_data['sa']) * self._meta_data['r']
      z = 0
      pc1 = ckp.xyz + pm.dot(np.array([x, y, z]))
      start_kp.x = pc1[0]
      start_kp.y = pc1[1]
      start_kp.z = pc1[2]

  def distance(self, point):
    kps = self.get_key_points()
    if self.type == EdgeType.LineEdge:
      kp1 = kps[0]
      kp2 = kps[1]
      alpha1 = kp1.angle_between(kp2, point)
      alpha2 = kp2.angle_between(kp1, point)
      if alpha1 > pi:
        alpha1 = 2 * pi - alpha1
      if alpha2 > pi:
        alpha2 = 2 * pi - alpha2
      if alpha1 < pi / 2 and alpha2 < pi / 2:
        distance = kp1.distance(point) * sin(alpha1)
        return distance
      else:
        return min(kp1.distance(point), kp2.distance(point))
    elif self.type == EdgeType.NurbsEdge:
      dist = 1e12
      for i in range(1, len(kps)):
        kp1 = kps[i - 1]
        kp2 = kps[i]
        alpha1 = kp1.angle_between(kp2, point)
        alpha2 = kp2.angle_between(kp1, point)
        if alpha1 > pi:
          alpha1 = 2 * pi - alpha1
        if alpha2 > pi:
          alpha2 = 2 * pi - alpha2
        if alpha1 < pi / 2 and alpha2 < pi / 2:
          distance = kp1.distance(point) * sin(alpha1)
        else:
          distance = min(kp1.distance(point), kp2.distance(point))
        if distance < dist:
          dist = distance
      return dist
    elif self.type == EdgeType.ArcEdge:
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
        dist = abs(center.distance(point) - radius)
      return dist
    elif self.type == EdgeType.CircleEdge:
      center = kps[0]
      radius = self._meta_data['r']

      dist = abs(center.distance(point) - radius)
      return dist
    elif self.type == EdgeType.FilletLineEdge:
      kp = kps[0]
      radius = self._meta_data['r']
      edges = kp.get_edges()
      edges.remove(self)
      draw_data = self.get_draw_data()
      if 'rect' in draw_data:
        rect = draw_data['rect']
        center = Vertex(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)
        dist = abs(center.distance(point) - radius)
      else:
        dist = kp.distance(point)
      return dist

  def get_draw_data(self):
    edge_data = {}

    key_points = self.get_key_points()
    if self.type == EdgeType.LineEdge:
      edges_list = key_points[0].get_edges()
      fillet1 = None
      other_edge1 = None
      for edge_item in edges_list:
        if edge_item.type == EdgeType.FilletLineEdge:
          fillet1 = edge_item
        elif edge_item is not self:
          other_edge1 = edge_item
      edges_list = key_points[1].get_edges()
      fillet2 = None
      other_edge2 = None
      for edge_item in edges_list:
        if edge_item.type == EdgeType.FilletLineEdge:
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
        dist = -tan(abtw / 2 + pi / 2) * r
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
        dist = -tan(abtw / 2 + pi / 2) * r
        fillet_offset_x = dist * cos(a1)
        fillet_offset_y = dist * sin(a1)

      x2 = key_points[1].x + fillet_offset_x
      y2 = key_points[1].y + fillet_offset_y
      edge_data["type"] = 1
      edge_data["coords"] = [Vertex(x1, y1), Vertex(x2, y2)]
    elif self.type == EdgeType.ArcEdge:
      cx = key_points[0].x
      cy = key_points[0].y
      cz = key_points[0].z
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
      edge_data["r"] = radius
      edge_data["c"] = Vertex(cx, cy, cz)
    elif self.type == EdgeType.FilletLineEdge:
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
        dist = radius / sin(angle_between / 2)
        angle_larger = False
        while angle_between < -2 * pi:
          angle_between += 2 * pi
        while angle_between > 2 * pi:
          angle_between -= 2 * pi
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
            end_angle = (edge1.angle(kp) - pi / 2) * 180 * 16 / pi
            start_angle = (edge2.angle(kp) + pi / 2) * 180 * 16 / pi
          else:
            end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
            start_angle = (edge2.angle(kp) + 3 * pi / 2) * 180 * 16 / pi
        else:
          if angle_larger:
            start_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
            end_angle = (edge2.angle(kp) - pi / 2) * 180 * 16 / pi
          else:
            end_angle = (edge1.angle(kp) + pi / 2) * 180 * 16 / pi
            start_angle = (edge2.angle(kp) - pi / 2) * 180 * 16 / pi
            end_angle += pi * 180 * 16 / pi
            start_angle += pi * 180 * 16 / pi
        span = end_angle - start_angle
        edge_data["type"] = 2
        edge_data["rect"] = rect
        edge_data["sa"] = start_angle
        edge_data["span"] = span
        edge_data["r"] = radius
        edge_data["c"] = Vertex(cx, cy)
    elif self.type == EdgeType.CircleEdge:
      kp = key_points[0]
      cx = key_points[0].x
      cy = key_points[0].y
      radius = self.get_meta_data("r")
      rect = [cx - radius, cy - radius, radius * 2, radius * 2]
      edge_data["type"] = 3
      edge_data["rect"] = rect
      edge_data["r"] = radius
      edge_data["c"] = Vertex(cx, cy)
    elif self.type == EdgeType.NurbsEdge:
      if self._draw_data is None:
        kps = self.get_key_points()
        nurbs = Nurbs()
        controls = []
        coords = []
        for i in range(0, len(kps)):
          controls.append(kps[i].xyz)

        if len(controls) > 2:
          nurbs.set_controls(controls)
          divs = len(controls) * 20
          for i in range(0, divs):
            p = nurbs.C(i / divs)
            coords.append(Vertex.from_xyz(p))
          p = controls[len(controls) - 1]
          coords.append(Vertex.from_xyz(p))
        else:
          for kp in kps:
            coords.append(kp)
        edge_data["type"] = 4
        edge_data["coords"] = coords
        self._draw_data = edge_data
      else:
        edge_data = self._draw_data
    return edge_data

  def angle(self, kp=None):
    kps = self.get_end_key_points()
    if self.type == EdgeType.LineEdge:
      if kp is None:
        return kps[0].angle2d(kps[1])
      else:
        if kp == kps[0]:
          return kps[0].angle2d(kps[1])
        elif kp == kps[1]:
          return kps[1].angle2d(kps[0])
        else:
          return kps[0].angle2d(kps[1])
    if self.type == EdgeType.ArcEdge:
      if kp is None:
        return self._meta_data['sa'] - pi / 2
      else:
        if kp == kps[0]:
          return self._meta_data['sa'] - pi / 2
        elif kp == kps[1]:
          return self._meta_data['ea'] - pi / 2
        else:
          center_kp = self.get_key_points()[0]
          return center_kp.angle2d(kp) + pi / 2

  @property
  def length(self):
    if self.type == EdgeType.LineEdge:
      kps = self.get_end_key_points()
      return kps[0].distance(kps[1])
    elif self.type == EdgeType.ArcEdge:
      sa = self._meta_data['sa']
      ea = self._meta_data['ea']
      r = self._meta_data['r']
      diff = ea - sa
      if diff > 2 * pi:
        diff -= 2 * pi
      if diff < -2 * pi:
        diff += 2 * pi
      return abs(diff * r)

  def coincident(self, key_point, coin_thress=None):
    kps = self.get_key_points()
    if coin_thress is None:
      threshold = self._geometry.threshold
    else:
      threshold = coin_thress
    if self.type == EdgeType.LineEdge:
      kp1 = kps[0]
      kp2 = kps[1]
      alpha1 = kp1.angle_between(kp2, key_point)
      alpha2 = kp2.angle_between(kp1, key_point)
      if alpha1 > pi:
        alpha1 = 2 * pi - alpha1
      if alpha2 > pi:
        alpha2 = 2 * pi - alpha2
      if alpha1 < pi / 2 and alpha2 < pi / 2:
        distance = kp1.distance(key_point) * sin(alpha1)
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
    new_edge = self._geometry.create_line_edge(key_point, second_key_point)
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
      'no': NamedObservableObject.serialize_json(self),
      'type': self._type.value,
      'key_points': self._key_points,
      'meta_data': self._meta_data,
      'meta_data_parameters': self._meta_data_parameters,
      'plane': self._plane,
      'style': self._style.uid

    }

  def deserialize_data(self, data):
    IdObject.deserialize_data(self, data['uid'])
    NamedObservableObject.deserialize_data(self, data.get('no', None))
    self._type = EdgeType(data['type'])
    self._key_points = data['key_points']
    self._plane = Plane.deserialize(data.get('plane', None))
    self._style = self._geometry.document.get_styles().get_edge_style(data.get('style', None))
    for kp_uid in self._key_points:
      kp = self._geometry.get_key_point(kp_uid)
      kp.add_change_handler(self.on_key_point_changed)
      kp.add_edge(self)
    self._meta_data = data.get('meta_data')
    self._meta_data_parameters = data.get('meta_data_parameters')
    for parameter_uid in self._meta_data_parameters:
      param = self._geometry.get_parameter_by_uid(parameter_uid)
      if param is not None:
        param.add_change_handler(self.on_parameter_change)
      else:
        i = 20
        # self._meta_data_parameters.pop(parameter_uid)

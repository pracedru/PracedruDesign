from math import pi, cos, sin, tan

from Data.Edges import *
from Data.Events import ChangeEvent
from Data.Objects import IdObject, NamedObservableObject
from Data.Point3d import KeyPoint
from Data.Vertex import Vertex

__author__ = 'mamj'


class Area(IdObject, NamedObservableObject):
  def __init__(self):
    IdObject.__init__(self)
    NamedObservableObject.__init__(self, "New Area")
    self._edges = []
    self._key_points = None

  @property
  def hatch(self):
    return None

  def inside(self, point):
    anglesum = 0.0
    last_point = None
    if self._edges[0].type == EdgeType.CircleEdge:
      kp = self._edges[0].get_key_points()[0]
      r = self._edges[0].get_meta_data('r')
      if r > kp.distance(point):
        return True
      return False
    else:
      for pnt in self.get_inside_key_points():
        if last_point is not None:
          angle = point.angle_between(last_point, pnt)
          if angle > pi:
            angle = -(2 * pi - angle)
          anglesum += angle
        last_point = pnt
      if abs(anglesum) > pi:
        return True
      return False

  def get_intersecting_edges(self, kp, gamma):
    intersecting_edges = []
    for edge in self._edges:
      if edge.type is EdgeType.LineEdge:
        kps = edge.get_end_key_points()
        x1 = kps[0].x
        y1 = kps[0].y
        x2 = kps[1].x
        y2 = kps[1].y
        x3 = kp.x
        y3 = kp.y
        x4 = kp.x + cos(gamma)
        y4 = kp.y + sin(gamma)
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom != 0:
          px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
          py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
          int_kp = Vertex(px, py)
          if edge.distance(int_kp) < 0.001:
            intersecting_edges.append([edge, int_kp])
      elif edge.type is EdgeType.ArcEdge:
        center_kp = edge.get_key_points()[0]
        radius = edge.get_meta_data('r')
        sa = edge.get_meta_data('sa')
        ea = edge.get_meta_data('ea')
        alpha = kp.angle2d(center_kp)
        dist = kp.distance(center_kp)
        beta = alpha - gamma
        rad_ray_dist = sin(beta) * dist
        if rad_ray_dist < radius:
          omega = center_kp.angle2d(kp)
          int_kp = Vertex(center_kp.x + cos(omega) * radius, center_kp.y + sin(omega) * radius)
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

  def delete(self):
    self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

  def on_edge_changed(self, event: ChangeEvent):
    if event.type == ChangeEvent.Deleted:
      if type(event.object) is Edge:
        if event.object.type != EdgeType.FilletLineEdge:
          self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))
        else:
          fillet_edge = event.object
          self._edges.remove(fillet_edge)
          fillet_edge.remove_change_handler(self.on_edge_changed)
          self._key_points = None
      if type(event.object) is KeyPoint:
        self.changed(ChangeEvent(self, ChangeEvent.Deleted, self))

  def get_key_points(self):
    """
    This function returns the key points that control the edges of this area.
    :return:
    """
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
        if edge.type != EdgeType.FilletLineEdge:
          if next_kp == edge.get_end_key_points()[0]:
            next_kp = edge.get_end_key_points()[1]
          else:
            next_kp = edge.get_end_key_points()[0]
          self._key_points.append(next_kp)
    return self._key_points

  def get_inside_key_points(self):
    """
    This functions finds the key points used to determine if another point is inside this area
    :return: list of points describing the outside limits
    """
    key_points = []
    if self._edges[0].type == EdgeType.CircleEdge:
      key_points.append(self._edges[0].get_end_key_points()[0])
    else:
      this_kp = self._edges[0].get_end_key_points()[0]
      next_kp = self._edges[0].get_end_key_points()[1]
      if this_kp == self._edges[1].get_end_key_points()[0] or this_kp == self._edges[1].get_end_key_points()[1]:
        this_kp = self._edges[0].get_end_key_points()[1]
        next_kp = self._edges[0].get_end_key_points()[0]
      key_points.append(this_kp)
      if self._edges[0].type == EdgeType.ArcEdge:
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
        if edge.type != EdgeType.FilletLineEdge:
          if edge.type == EdgeType.ArcEdge:
            ckp = edge.get_key_points()[0]
            sa = edge.get_meta_data('sa')
            ea = edge.get_meta_data('ea')
            r = edge.get_meta_data('r')
            diff = ea - sa
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
  def deserialize(data, doc, sketch):
    area = Area()
    area.deserialize_data(data, doc, sketch)
    return area

  def serialize_json(self):
    return \
      {
        'uid': IdObject.serialize_json(self),
        'no': NamedObservableObject.serialize_json(self),
        'edges': self.get_edge_uids(),
        'name': self.name
      }

  def deserialize_data(self, data, doc, sketch):
    IdObject.deserialize_data(self, data['uid'])
    NamedObservableObject.deserialize_data(self, data.get('no', None))
    for edge_uid in data['edges']:
      edge = sketch.get_edge(edge_uid)
      self._edges.append(edge)
      edge.add_change_handler(self.on_edge_changed)
    self._name = data['name']

class CompositeArea(IdObject, NamedObservableObject):
  def __init__(self):
    IdObject.__init__(self)
    NamedObservableObject.__init__(self, "New Area")
    self._edges = []
    self._key_points = None
from math import *

import numpy as np
from PyQt5.QtCore import QPoint, QThread
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QOpenGLShaderProgram, QOpenGLShader, QMatrix4x4, QVector3D, QVector2D

from Data import read_text_from_disk
from Data.Edges import Edge

try:
  from OpenGL import GL
except:
  pass

from PyQt5.QtGui import QOpenGLVersionProfile
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QOpenGLWidget

from Business.PartAction import *
from Data.Events import ChangeEvent
from Data.Part import Part, Feature
from Data.Vertex import Vertex

from GUI.Widgets.GlDrawable import GlPlaneDrawable, GlPartDrawable
from GUI.Widgets.SimpleDialogs import SketchDialog, ExtrudeDialog, RevolveDialog


class PartViewWidget(QOpenGLWidget):
  PROGRAM_VERTEX_ATTRIBUTE = 0
  PROGRAM_NORMALS_ATTRIBUTE = 1

  def __init__(self, parent, document):
    super(PartViewWidget, self).__init__(parent)
    self._document = document
    self._part = None
    self._gen_lists_start = 0
    self._drawables = []
    self.xRot = 225 * 16
    self.yRot = 45 * 16
    self.zRot = 0
    self._scale = 0.5
    self.lastPos = QPoint()
    self._offset = Vertex()
    self._mouse_position = None
    self.part_color = QColor(100, 100, 190, 255)
    self.part_specular = 0.5
    self.part_color_edge = QColor(50, 50, 50, 255)
    self.plane_color = QColor(0, 150, 200, 25)
    self.plane_color_edge = QColor(0, 150, 200, 180)
    self.background_color = QColor(180, 180, 195, 25)
    self._gl = None
    self._show_surfaces = True
    self._show_lines = True
    self._show_planes = True
    self._program = None
    self._vertices = [[0, 0, 0]]
    self._normals = [[0, 0, 0]]
    self._plane_faces_index = 0
    self._plane_edges_index = 0
    self._part_faces_index = 0
    self._part_edges_index = 0
    self._new_verts = False
    format = QSurfaceFormat()
    format.setSamples(4)
    self.setFormat(format)

  @property
  def show_surfaces(self):
    return self._show_surfaces

  @show_surfaces.setter
  def show_surfaces(self, value):
    self._show_surfaces = value
    self.redraw_drawables()
    self.update()

  @property
  def show_lines(self):
    return self._show_lines

  @show_lines.setter
  def show_lines(self, value):
    self._show_lines = value
    self.redraw_drawables()
    self.update()

  @property
  def show_planes(self):
    return self._show_planes

  @show_planes.setter
  def show_planes(self, value):
    self._show_planes = value
    self.update()

  def set_part(self, part: Part):
    if self._part == part:
      return
    if self._part is not None:
      part.remove_change_handler(self.part_changed)
    self._part = part
    self.update_drawables()
    self.redraw_drawables()
    self.part_color = QColor(part.color[0], part.color[1], part.color[2], part.color[3])
    self.part_specular = part.specular
    part.add_change_handler(self.part_changed)
    self.scale_to_content()
    self.update()

  def update_drawables(self):
    self._drawables = []
    if self._part is not None:
      for plane_feature in self._part.get_plane_features():
        drawable = GlPlaneDrawable(len(self._drawables) + self._gen_lists_start, plane_feature)
        self._drawables.append(drawable)
      part_drawable = GlPartDrawable(len(self._drawables) + self._gen_lists_start, self._part)
      self._drawables.append(part_drawable)

  def redraw_drawables(self, show_messages=True):
    if self._part.update_needed:
      self._part.update_geometry()
      self.update_drawables()
    count = len(self._drawables) * 4
    counter = 1
    self._vertices.clear()
    self._normals.clear()
    for drawable in self._drawables:
      if type(drawable) == GlPlaneDrawable:
        drawable.on_plane_changed(None)
        self._vertices.extend(drawable.vertices)
        self._normals.extend(drawable.normals)
      if show_messages:
        self._document.set_status("Drawing planes faces %d" % counter, 100 * counter / count)
      counter += 1
    self._plane_faces_index = len(self._vertices) - 1
    for drawable in self._drawables:
      if type(drawable) == GlPlaneDrawable:
        self._vertices.extend(drawable.lines)
        self._normals.extend(drawable.lines)
      if show_messages:
        self._document.set_status("Drawing plane edges %d" % counter, 100 * counter / count)
      counter += 1
    self._plane_edges_index = len(self._vertices) - 1
    for drawable in self._drawables:
      if type(drawable) == GlPartDrawable:
        self._vertices.extend(drawable.vertices)
        self._normals.extend(drawable.normals)
      if show_messages:
        self._document.set_status("Drawing part faces %d" % counter, 100 * counter / count)
      counter += 1
    self._part_faces_index = len(self._vertices) - 1
    for drawable in self._drawables:
      if type(drawable) == GlPartDrawable:
        self._vertices.extend(drawable.lines)
        self._normals.extend(drawable.lines)
      if show_messages:
        self._document.set_status("Drawing part edges %d" % counter, 100 * counter / count)
      counter += 1
    self._part_edges_index = len(self._vertices) - 1
    self._new_verts = True

  def scale_to_content(self):
    limits = self._part.get_limits()
    size = max(limits[1].x - limits[0].x, limits[1].y - limits[0].y)
    size = max(size, limits[1].z - limits[0].z) * 0.7
    self._scale = size
    self._offset.x = 0
    self._offset.y = 0
    self._offset.z = 0

  def part_changed(self, event):
    if event.type == ChangeEvent.ObjectAdded:
      self.redraw_drawables()
      self.update()
      self.scale_to_content()
    if event.type == ChangeEvent.ValueChanged:
      self.part_color = QColor(self._part.color[0], self._part.color[1], self._part.color[2], self._part.color[3])
      self.part_specular = self._part.specular

  def on_create_add_sketch_to_part(self):
    planes = []
    for plane_feature in self._part.get_plane_features():
      planes.append(plane_feature.name)
    value = QInputDialog.getItem(self, "Select plane for sketch", "plane name:", planes, 0, False)
    if value[1] == QDialog.Accepted:
      for plane_feature in self._part.get_plane_features():
        if plane_feature.name == value[0]:
          create_add_sketch_to_part(self._document, self._part, plane_feature)

  def on_insert_sketch(self):
    sketch_dialog = SketchDialog(self, self._document, self._part)
    value = sketch_dialog.exec_()
    if value == QDialog.Accepted:
      sketch_name = sketch_dialog.sketch()
      plane_name = sketch_dialog.plane()
      sketch = self._document.get_geometries().get_sketch_by_name(sketch_name)
      for plane in self._part.get_plane_features():
        if plane.name == plane_name:
          break
      insert_sketch_in_part(self._document, self._part, sketch, plane)
      self.redraw_drawables()
      self.scale_to_content()

  def on_insert_extrude(self):
    if self._part is not None:
      extrude_dialog = ExtrudeDialog(self, self._document, self._part)
      result = extrude_dialog.exec_()
      if result == QDialog.Accepted:
        sketch_feature = extrude_dialog.sketch_feature
        area = extrude_dialog.area
        direction = extrude_dialog.direction
        if direction == Feature.Forward:
          length = [extrude_dialog.length, 0]
        elif direction == Feature.Backward:
          length = [0, -extrude_dialog.length]
        else:
          length = [extrude_dialog.length / 2, -extrude_dialog.length / 2]
        if area is not None:
          add_extrude_in_part(self._document, self._part, sketch_feature, area, length)

  def on_revolve_area(self):
    if self._part is not None:
      revolve_dialog = RevolveDialog(self, self._document, self._part)
      result = revolve_dialog.exec_()
      if result == QDialog.Accepted:
        sketch_feature = revolve_dialog.sketch_feature
        area = revolve_dialog.area
        revolve_axis = revolve_dialog.get_axis()
        direction = revolve_dialog.direction
        if direction == Feature.Forward:
          length = [revolve_dialog.length, 0]
        elif direction == Feature.Backward:
          length = [0, -revolve_dialog.length]
        else:
          length = [revolve_dialog.length / 2, -revolve_dialog.length / 2]
        if area is not None and revolve_axis is not None:
          add_revolve_in_part(self._document, self._part, sketch_feature, area, length, revolve_axis)

  def on_create_nurbs_surface(self):
    sketch_feature = None
    nurbs_edges = []
    feats = self._part.get_features_list()
    for feat in feats:
      if feat.feature_type == Feature.SketchFeature:
        sketch_feature = feat
        sketch = sketch_feature.get_objects()[0]
        for edge in sketch.get_edges():
          if edge[1].type == Edge.NurbsEdge:
            nurbs_edges.append(edge[1])
    if sketch_feature is not None and len(nurbs_edges) > 2:
      add_nurbs_surface_in_part(self._document, self._part, sketch_feature, nurbs_edges)

  def setXRotation(self, angle):
    angle = max(90 * 16, angle)
    angle = min(270 * 16, angle)
    if angle != self.xRot:
      self.xRot = angle
      # self.xRotationChanged.emit(angle)
      self.update()

  def setYRotation(self, angle):
    angle = self.normalizeAngle(angle)
    if angle != self.yRot:
      self.yRot = angle
      # self.yRotationChanged.emit(angle)
      self.update()

  def setZRotation(self, angle):
    angle = self.normalizeAngle(angle)
    if angle != self.zRot:
      self.zRot = angle
      # self.zRotationChanged.emit(angle)
      self.update()

  def initializeGL(self):
    c = self.context()
    f = QSurfaceFormat()  # The default
    vp = QOpenGLVersionProfile(f)
    self._gl = c.versionFunctions(vp)
    self._gl.initializeOpenGLFunctions()
    self._gl.glEnable(self._gl.GL_MULTISAMPLE)
    self._gl.glEnable(self._gl.GL_DEPTH_TEST)
    self._gl.glDisable(self._gl.GL_CULL_FACE)
    self._gl.glBlendFunc(self._gl.GL_SRC_ALPHA, self._gl.GL_ONE_MINUS_SRC_ALPHA)
    self._gl.glEnable(self._gl.GL_BLEND)

    vertex_shader_code = read_text_from_disk("./GUI/Shaders/vertex_shader.c")
    fragment_shader_code = read_text_from_disk("./GUI/Shaders/fragment_shader.c")

    self._program = QOpenGLShaderProgram()
    self._program.addShaderFromSourceCode(QOpenGLShader.Vertex, vertex_shader_code)
    self._program.addShaderFromSourceCode(QOpenGLShader.Fragment, fragment_shader_code)
    self._program.link()
    self._program.bind()
    self._program.enableAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE)
    self._program.enableAttributeArray(self.PROGRAM_NORMALS_ATTRIBUTE)
    self._program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE, self._vertices)
    self._program.setAttributeArray(self.PROGRAM_NORMALS_ATTRIBUTE, self._normals)

  def paintGL(self):
    gl = self._gl
    if self._part is not None:
      if self._part.update_needed:
        self.redraw_drawables(False)
    if self._new_verts:
      if len(self._vertices) > 0:
        self._program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE, self._vertices)
        self._program.setAttributeArray(self.PROGRAM_NORMALS_ATTRIBUTE, self._normals)
      self._new_verts = False
    c = self.background_color
    self._gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())
    self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
    m = QMatrix4x4()
    v = QMatrix4x4()
    p = QMatrix4x4()

    #   Gradient
    v.lookAt(QVector3D(0, 0, -10 * self._scale), QVector3D(0, 0, 0), QVector3D(0, 1, 0))
    p.ortho(-0.5, 0.5, 0.5, -0.5, 0, 15 * self._scale)
    mvp = p * v * m
    self._program.setUniformValue('mvp', mvp)
    mv = v * m
    self._program.setUniformValue('model_view_matrix', mv)
    self._program.setUniformValue('normal_matrix', mv.normalMatrix())

    self._gl.glDisable(self._gl.GL_DEPTH_TEST)
    self._program.setUniformValue('resolution', QVector2D(self.width(), self.height()))
    self._program.setUniformValue('gradient', True)
    self._program.setUniformValue('lighting', False)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(-0.5, 0.5)
    gl.glVertex2f(-0.5, -0.5)
    gl.glVertex2f(0.5, -0.5)
    gl.glVertex2f(0.5, 0.5)
    gl.glEnd()
    self._program.setUniformValue('gradient', False)
    #    End Gradient

    v.rotate(self.xRot / 16.0, 1.0, 0.0, 0.0)
    v.rotate(self.yRot / 16.0, 0.0, 1.0, 0.0)
    v.rotate(self.zRot / 16.0, 0.0, 0.0, 1.0)
    v.translate(self._offset.x, self._offset.y, self._offset.z)

    scale = self._scale
    width = self.width()
    height = self.height()
    aspect_ratio = width / height
    p = QMatrix4x4()
    if width <= height:
      p.ortho(-scale, scale, scale / aspect_ratio, -scale / aspect_ratio, min(-10 * scale, -10), max(20 * scale, 15))
    else:
      p.ortho(-scale * aspect_ratio, scale * aspect_ratio, scale, -scale, min(-10 * scale, -10), max(20 * scale, 15))

    mvp = p * v * m
    self._program.setUniformValue('mvp', mvp)
    mv = v * m
    self._program.setUniformValue('model_view_matrix', mv)
    self._program.setUniformValue('normal_matrix', mv.normalMatrix())
    self._gl.glEnable(self._gl.GL_DEPTH_TEST)
    if self._plane_faces_index + 1 < self._plane_edges_index and self._show_planes:
      self.set_color(self.plane_color_edge)
      self._gl.glLineWidth(2.0)
      count = self._plane_edges_index - self._plane_faces_index
      self._gl.glDrawArrays(self._gl.GL_LINES, self._plane_faces_index + 1, count)
    if self._part_faces_index + 1 < self._part_edges_index:
      if self._show_lines:
        self.set_color(self.part_color_edge)
        self._gl.glLineWidth(1.5)
        count = self._part_edges_index - self._part_faces_index
        self._gl.glDrawArrays(self._gl.GL_LINES, self._part_faces_index + 1, count)
    if self._plane_edges_index + 1 < self._part_faces_index:
      if self._show_surfaces:
        if self._show_lines:
          self._gl.glEnable(self._gl.GL_POLYGON_OFFSET_FILL)
          self._gl.glPolygonOffset(1.0, 1.0)
        self._program.setUniformValue('lighting', True)
        self.set_color(self.part_color)
        self.set_specular(self.part_specular)
        count = self._part_faces_index - self._plane_edges_index
        self._gl.glDrawArrays(self._gl.GL_TRIANGLES, self._plane_edges_index + 1, count)
        self._program.setUniformValue('lighting', False)
        if self._show_lines:
          self._gl.glDisable(self._gl.GL_POLYGON_OFFSET_FILL)
    if self._plane_faces_index > 0 and self._show_planes:
      self._gl.glDepthMask(self._gl.GL_FALSE)
      self.set_color(self.plane_color)
      self._gl.glDrawArrays(self._gl.GL_TRIANGLES, 0, self._plane_faces_index + 1)
      self._gl.glDepthMask(self._gl.GL_TRUE)

  def resizeGL(self, width, height):
    side = min(width, height)
    if side < 0:
      return
    self._gl.glViewport((width - side) // 2, (height - side) // 2, width, height)
    aspect_ratio = width / height
    self._gl.glMatrixMode(self._gl.GL_PROJECTION)
    self._gl.glLoadIdentity()
    if width <= height:
      self._gl.glOrtho(-0.5, +0.5, +0.5 / aspect_ratio, -0.5 / aspect_ratio, 4.0, 15.0)
    else:
      self._gl.glOrtho(-0.5 * aspect_ratio, +0.5 * aspect_ratio, +0.5, -0.5, 4.0, 15.0)
    self._gl.glMatrixMode(self._gl.GL_MODELVIEW)

  def mousePressEvent(self, event):
    self.lastPos = event.pos()

  def mouseMoveEvent(self, event):
    dx = event.x() - self.lastPos.x()
    dy = event.y() - self.lastPos.y()

    if event.buttons() & Qt.RightButton:
      self.setXRotation(self.xRot + 8 * dy)
      self.setYRotation(self.yRot - 8 * dx)
    elif event.buttons() & Qt.MiddleButton:
      yangle = self.yRot * pi / (180 * 16)
      xangle = self.xRot * pi / (180 * 16)
      dx *= self._scale * -1
      dy *= self._scale
      self._offset.x += dx * 0.002 * cos(yangle) + dy * 0.002 * sin(xangle) * sin(yangle)
      self._offset.y += dy * 0.002 * cos(xangle)
      self._offset.z += dx * 0.002 * sin(yangle) - dy * 0.002 * sin(xangle) * cos(yangle)
      self.update()

    self.lastPos = event.pos()

  def wheelEvent(self, event):
    delta = event.angleDelta().y() * 0.01 / 8
    if self._scale + self._scale * (delta * 0.01) > 0:
      self._scale *= 1 - delta
    self.update()

  def normalizeAngle(self, angle):
    while angle < 0:
      angle += 360 * 16
    while angle > 360 * 16:
      angle -= 360 * 16
    return angle

  def set_color(self, c):
    self._program.setUniformValue('color', c)

  def set_specular(self, spec):
    self._program.setUniformValue('specular', spec)

import math

import numpy as np
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from OpenGL import GL
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtGui import QOpenGLShader
from PyQt5.QtGui import QOpenGLShaderProgram
from PyQt5.QtGui import QOpenGLVersionProfile
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtWidgets import QWidget

from Business.PartAction import *
from Data import read_text_from_disk
from Data.Vertex import Vertex

PROGRAM_VERTEX_POS_ATTRIBUTE = 0
PROGRAM_UV_ATTRIBUTE = 1
PROGRAM_VERTEX_NORM_ATTRIBUTE = 2


class PartViewWidget(QOpenGLWidget):
    def __init__(self, parent, document):
        super(PartViewWidget, self).__init__(parent)
        self._document = document
        self._part = None
        self.object = 0
        self.xRot = -45*16
        self.yRot = 45*16
        self.zRot = 0
        self._scale = 0.5
        self.lastPos = QPoint()
        self._mouse_position = None
        self.part_color = QColor(180, 180, 180, 255)
        self.plane_color = QColor(0, 150, 200, 25)
        self.plane_color_edge = QColor(0, 150, 200, 180)
        self.background_color = QColor(180, 180, 180)

    def set_part(self, part):
        self._part = part
        self.object = self.makeObject()

    def on_insert_sketch(self):
        sketches = []
        for sketch in self._document.get_geometries().get_sketches():
            sketches.append(sketch.name)
        value = QInputDialog.getItem(self, "Select existing sketch or create new", "Sketch name:", sketches, 0, False)
        if value[1] == QDialog.Accepted:
            sketch = self._document.get_geometries().get_sketch_by_name(value[0])
            insert_sketch_in_part(self._document, self._part, sketch)

    def setXRotation(self, angle):

        angle = max(-90 * 16, angle)
        angle = min(90 * 16, angle)
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
        f = QSurfaceFormat()             # The default
        p = QOpenGLVersionProfile(f)
        self.gl = c.versionFunctions(p)
        self.gl.initializeOpenGLFunctions()
        self.setClearColor(self.background_color)
        self.object = self.makeObject()
        self.gl.glShadeModel(self.gl.GL_FLAT)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_CULL_FACE)
        self.gl.glDepthFunc(self.gl.GL_LEQUAL)
        self.gl.glBlendFunc(self.gl.GL_SRC_ALPHA, self.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.gl.glEnable(self.gl.GL_BLEND)
        self.gl.glEnable(self.gl.GL_NORMALIZE)
        light_diffuse = [0.5, 0.5, 0.5, 1.0]
        light_ambient = [0.5, 0.5, 0.5, 1.0]
        self.gl.glLightfv(self.gl.GL_LIGHT0, self.gl.GL_DIFFUSE, light_diffuse)
        self.gl.glLightfv(self.gl.GL_LIGHT0, self.gl.GL_AMBIENT, light_ambient)
        # return
        # vshader = read_text_from_disk("./GUI/Shaders/vertex_shader.c")
        # fshader = read_text_from_disk("./GUI/Shaders/fragment_shader.c")
        # self.program = QOpenGLShaderProgram()
        # self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, vshader)
        # self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, fshader)
        # self.program.link()
        # self.program.bind()
        # self.program.setUniformValue('texture', 0)
        # self.program.enableAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE)
        # self.program.enableAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE)
        # self.program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE, self.vertices)
        # self.program.setAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE, self.texCoords)

    def paintGL(self):
        width = self.width()
        height = self.height()
        light_position = [-0.7, 1.0, -1.0, 0.0]
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()

        self.gl.glBegin(self.gl.GL_QUADS)
        self.gl.glColor3f(1.0, 0.0, 0.0)
        self.gl.glVertex2f(-1.0, 1.0)
        self.gl.glVertex2f(-1.0, -1.0)

        self.gl.glColor3f(0.0, 0.0, 1.0)
        self.gl.glVertex2f(1.0, -1.0)
        self.gl.glVertex2f(1.0, 1.0)
        self.gl.glEnd()

        self.gl.glLightfv(self.gl.GL_LIGHT0, self.gl.GL_POSITION, light_position)
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.gl.glScalef(self._scale, self._scale, self._scale)
        self.gl.glCallList(self.object)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        self.gl.glViewport((width - side) // 2, (height - side) // 2, width, height)
        self.gl.glViewport(0, 0, 200, 400)

        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot - 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        #elif event.buttons() & Qt.RightButton:
        #    self.setXRotation(self.xRot + 8 * dy)
        #    self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() * 0.01 / 8
        if self._scale + self._scale * (delta * 0.01) > 0:
            self._scale *= 1 + delta
            self._scale *= 1 + delta
            self._scale *= 1 + delta
        self.update()

    def makeObject(self):
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)
        if self._part is not None:
            for plane in self._part.get_planes():
                p = plane.get_vertex('p')
                xd = plane.get_vertex('xd')
                yd = plane.get_vertex('yd')
                size = 1
                v1 = p.xyz * size - xd.xyz * size + yd.xyz * size
                v2 = p.xyz * size - xd.xyz * size - yd.xyz * size
                v3 = p.xyz * size + xd.xyz * size + yd.xyz * size
                v4 = p.xyz * size + xd.xyz * size - yd.xyz * size
                self.draw_feature_plane(v1, v2, v3, v4)

        self.gl.glEnable(self.gl.GL_LIGHT0)
        self.gl.glEnable(self.gl.GL_LIGHTING)
        self.draw_cube(1, Vertex())
        self.gl.glDisable(self.gl.GL_LIGHT0)
        self.gl.glDisable(self.gl.GL_LIGHTING)
        self.gl.glEndList()

        return genList

    def draw_cube(self, size, position):
        self.gl.glEnable(self.gl.GL_COLOR_MATERIAL)
        self.setColor(self.part_color)
        self.gl.glMaterialfv(self.gl.GL_FRONT, self.gl.GL_DIFFUSE, [0.5, 0.5, 0.5, 0.5])
        self.gl.glBegin(self.gl.GL_TRIANGLES)
        p = position
        s = size/2
        v1 = Vertex(p.x + s, p.y + s, p.z + s).xyz
        v2 = Vertex(p.x + s, p.y + s, p.z - s).xyz
        v3 = Vertex(p.x + s, p.y - s, p.z + s).xyz
        v4 = Vertex(p.x + s, p.y - s, p.z - s).xyz
        v5 = Vertex(p.x - s, p.y + s, p.z + s).xyz
        v6 = Vertex(p.x - s, p.y + s, p.z - s).xyz
        v7 = Vertex(p.x - s, p.y - s, p.z + s).xyz
        v8 = Vertex(p.x - s, p.y - s, p.z - s).xyz

        self.double_sided_quad(v1, v2, v3, v4)
        self.double_sided_quad(v1, v2, v5, v6)
        self.double_sided_quad(v1, v3, v5, v7)
        self.double_sided_quad(v7, v8, v3, v4)
        self.double_sided_quad(v5, v6, v7, v8)

        self.gl.glEnd()

    def draw_feature_plane(self, v1, v2, v3, v4):
        self.gl.glDisable(self.gl.GL_DEPTH_TEST)
        self.gl.glBegin(self.gl.GL_TRIANGLES)
        self.setColor(self.plane_color)

        m = 2
        for i in range(m):
            for l in range(m):
                delta_x_1 = float(i) / float(m)
                delta_x_2 = float(i+1.0) / float(m)
                delta_y_1 = float(l) / float(m)
                delta_y_2 = float(l+1.0) / float(m)
                ul = v1 + (v2 - v1) * delta_x_1 + (v3 - v1) * delta_y_1
                ll = v1 + (v2 - v1) * delta_x_1 + (v3 - v1) * delta_y_2
                ur = v1 + (v2 - v1) * delta_x_2 + (v3 - v1) * delta_y_1
                lr = v1 + (v2 - v1) * delta_x_2 + (v3 - v1) * delta_y_2
                self.double_sided_triangle(ul, ll, ur)
                self.double_sided_triangle(ur, lr, ll)

        self.gl.glEnable(self.gl.GL_DEPTH_TEST)

        self.gl.glEnd()
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glLineWidth(2.0)
        self.gl.glBegin(self.gl.GL_LINES)
        self.setColor(self.plane_color_edge)
        self.gl.glVertex3d(v1[0], v1[1], v1[2])
        self.gl.glVertex3d(v2[0], v2[1], v2[2])
        self.gl.glVertex3d(v2[0], v2[1], v2[2])
        self.gl.glVertex3d(v4[0], v4[1], v4[2])
        self.gl.glVertex3d(v4[0], v4[1], v4[2])
        self.gl.glVertex3d(v3[0], v3[1], v3[2])
        self.gl.glVertex3d(v3[0], v3[1], v3[2])
        self.gl.glVertex3d(v1[0], v1[1], v1[2])
        self.gl.glEnd()

    def double_sided_quad(self, v1, v2, v3, v4):
        self.double_sided_triangle(v1, v2, v3)
        self.double_sided_triangle(v4, v2, v3)

    def double_sided_triangle(self, v1, v2, v3):
        cp = np.cross(v2-v1, v3-v1)
        n = cp/np.linalg.norm(cp)
        self.gl.glVertex3d(v1[0], v1[1], v1[2])
        self.gl.glNormal3d(n[0], n[1], n[2])
        self.gl.glVertex3d(v2[0], v2[1], v2[2])
        self.gl.glNormal3d(n[0], n[1], n[2])
        self.gl.glVertex3d(v3[0], v3[1], v3[2])
        self.gl.glNormal3d(n[0], n[1], n[2])

        n = -n
        self.gl.glVertex3d(v3[0], v3[1], v3[2])
        self.gl.glNormal3d(n[0], n[1], n[2])
        self.gl.glVertex3d(v2[0], v2[1], v2[2])
        self.gl.glNormal3d(n[0], n[1], n[2])
        self.gl.glVertex3d(v1[0], v1[1], v1[2])
        self.gl.glNormal3d(n[0], n[1], n[2])

    def revolve_edges(self, edges, angle, axis_position, axis_orientation):
        pass

    def extrude(self, x1, y1, x2, y2):
        self.setColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        self.gl.glVertex3d(x1, y1, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        self.gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        self.gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())



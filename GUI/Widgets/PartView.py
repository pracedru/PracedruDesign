import math

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
from Data.Vertex import Vertex

PROGRAM_VERTEX_ATTRIBUTE = 0
PROGRAM_TEXCOORD_ATTRIBUTE = 1


class PartViewWidget(QOpenGLWidget):
    def __init__(self, parent, document):
        super(PartViewWidget, self).__init__(parent)
        self._document = document
        self._part = None
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self._scale = 1.0
        self.lastPos = QPoint()
        self._mouse_position = None
        self.part_color = QColor(150, 150, 150)
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
        angle = self.normalizeAngle(angle)
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
        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        light_position = [2.0, 2.0, 2.0, 0.0]

        self.gl.glLightfv(self.gl.GL_LIGHT0, self.gl.GL_DIFFUSE, light_diffuse)
        self.gl.glLightfv(self.gl.GL_LIGHT0, self.gl.GL_POSITION, light_position)
        return
        vshader = QOpenGLShader(QOpenGLShader.Vertex, self)
        vshader.compileSourceFile("./GUI/Shaders/vertex_shader.c")
        fshader = QOpenGLShader(QOpenGLShader.Fragment, self)
        fshader.compileSourceFile("./GUI/Shaders/fragment_shader.c")
        program = QOpenGLShaderProgram()
        program.addShader(vshader)
        program.addShader(fshader)
        program.bindAttributeLocation("vertex", PROGRAM_VERTEX_ATTRIBUTE)
        program.bindAttributeLocation("texCoord", PROGRAM_TEXCOORD_ATTRIBUTE)
        program.link()
        program.bind()
        program.setUniformValue("texture", 0)

    def paintGL(self):
        width = self.width()
        height = self.height()

        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()
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
        #self.gl.glViewport(0, 0, 200, 400)

        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot - 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

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

        # self.gl.glEnable(self.gl.GL_LIGHT0)
        # self.gl.glEnable(self.gl.GL_LIGHTING)
        self.draw_cube(0.5)
        # self.gl.glDisable(self.gl.GL_LIGHT0)
        # self.gl.glDisable(self.gl.GL_LIGHTING)
        self.gl.glEndList()

        return genList

    def draw_cube(self, s):
        self.setColor(self.part_color)
        self.gl.glBegin(self.gl.GL_TRIANGLES)
        v1 = Vertex(s, s, s).xyz
        v2 = Vertex(s, s, 0).xyz
        v3 = Vertex(s, 0, s).xyz
        v4 = Vertex(s, 0, 0).xyz
        v5 = Vertex(0, s, s).xyz
        v6 = Vertex(0, s, 0).xyz
        v7 = Vertex(0, 0, s).xyz
        v8 = Vertex(0, 0, 0).xyz

        self.double_sided_quad(v1, v2, v3, v4)
        self.double_sided_quad(v1, v2, v5, v6)
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
        self.gl.glVertex3d(v1[0], v1[1], v1[2])
        self.gl.glVertex3d(v2[0], v2[1], v2[2])
        self.gl.glVertex3d(v3[0], v3[1], v3[2])

        self.gl.glVertex3d(v3[0], v3[1], v3[2])
        self.gl.glVertex3d(v2[0], v2[1], v2[2])
        self.gl.glVertex3d(v1[0], v1[1], v1[2])

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


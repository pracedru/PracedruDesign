from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from OpenGL import GL

from PyQt5.QtGui import QOpenGLVersionProfile
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QOpenGLWidget

from Business.PartAction import *

from GUI.Widgets.GlDrawable import GlPlaneDrawable, GlPartDrawable

PROGRAM_VERTEX_POS_ATTRIBUTE = 0
PROGRAM_UV_ATTRIBUTE = 1
PROGRAM_VERTEX_NORM_ATTRIBUTE = 2


class PartViewWidget(QOpenGLWidget):
    def __init__(self, parent, document):
        super(PartViewWidget, self).__init__(parent)
        self._document = document
        self._part = None
        self._gen_lists_start = 0
        self._drawables = []
        self.xRot = -45*16
        self.yRot = 45*16
        self.zRot = 0
        self._scale = 0.5
        self.lastPos = QPoint()
        self._mouse_position = None
        self.part_color = QColor(180, 180, 180, 255)
        self.plane_color = QColor(0, 150, 200, 25)
        self.plane_color_edge = QColor(0, 150, 200, 180)
        self.background_color = QColor(180, 180, 195, 25)
        self._gl = None

    def set_part(self, part):
        if self._part is not None:
            part.remove_change_handler(self.part_changed)
        self._part = part
        self._drawables = []

        for plane_feature in part.get_planes():
            drawable = GlPlaneDrawable(len(self._drawables)+self._gen_lists_start, plane_feature)
            self._drawables.append(drawable)
            drawable.redraw(self._gl)
        part_drawable = GlPartDrawable(len(self._drawables)+self._gen_lists_start, part)
        part_drawable.redraw(self._gl)
        self._drawables.append(part_drawable)
        part.add_change_handler(self.part_changed)

    def part_changed(self, event):
        pass

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
        self._gl = c.versionFunctions(p)
        self._gl.initializeOpenGLFunctions()
        self.setClearColor(self.background_color)
        self._gl.glShadeModel(self._gl.GL_FLAT)
        self._gl.glEnable(self._gl.GL_DEPTH_TEST)
        self._gl.glEnable(self._gl.GL_CULL_FACE)
        self._gl.glDepthFunc(self._gl.GL_LEQUAL)
        self._gl.glBlendFunc(self._gl.GL_SRC_ALPHA, self._gl.GL_ONE_MINUS_SRC_ALPHA)
        self._gl.glEnable(self._gl.GL_BLEND)
        self._gl.glEnable(self._gl.GL_NORMALIZE)
        light_diffuse = [0.5, 0.5, 0.5, 1.0]
        light_ambient = [0.5, 0.5, 0.5, 1.0]
        self._gl.glLightfv(self._gl.GL_LIGHT0, self._gl.GL_DIFFUSE, light_diffuse)
        self._gl.glLightfv(self._gl.GL_LIGHT0, self._gl.GL_AMBIENT, light_ambient)
        self._gen_lists_start = self._gl.glGenLists(100)

        # return
        # vshader = read_text_from_disk("./GUI/Shaders/vertex_shader.c")
        # fshader = read_text_from_disk("./GUI/Shaders/fragment_shader.c")
        # self.program = QOpenGLShaderProgram()
        # self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, vshader)
        # self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, fshader)
        # self.program.link()
        # self.program.bind()self.gl.glEnable(self.gl.GL_COLOR_MATERIAL)

        # self.program.setUniformValue('texture', 0)
        # self.program.enableAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE)
        # self.program.enableAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE)
        # self.program.setAttributeArray(self.PROGRAM_VERTEX_ATTRIBUTE, self.vertices)
        # self.program.setAttributeArray(self.PROGRAM_TEXCOORD_ATTRIBUTE, self.texCoords)

    def paintGL(self):
        light_position = [-0.7, 1.0, -1.0, 0.0]
        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT | self._gl.GL_DEPTH_BUFFER_BIT)
        self._gl.glLoadIdentity()

        self._gl.glLightfv(self._gl.GL_LIGHT0, self._gl.GL_POSITION, light_position)
        self._gl.glTranslated(0.0, 0.0, -10.0)
        self._gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self._gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self._gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self._gl.glScalef(self._scale, self._scale, self._scale)
        for drawable in self._drawables:
            self._gl.glCallList(drawable.get_gen_list)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        self._gl.glViewport((width - side) // 2, (height - side) // 2, width, height)
        self._gl.glViewport(0, 0, 200, 400)

        self._gl.glMatrixMode(self._gl.GL_PROJECTION)
        self._gl.glLoadIdentity()
        self._gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        self._gl.glMatrixMode(self._gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot - 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)

        self.lastPos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() * 0.01 / 8
        if self._scale + self._scale * (delta * 0.01) > 0:
            self._scale *= 1 + delta

        self.update()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        self._gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        self._gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())



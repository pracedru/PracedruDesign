import numpy as np
from PyQt5.QtGui import QColor

from Data.Part import Feature
from Data.Vertex import Vertex


def double_sided_triangle(gl, v1, v2, v3):
	cp = np.cross(v2 - v1, v3 - v1)
	n = cp / np.linalg.norm(cp)
	gl.glNormal3f(n[0], n[1], n[2])
	gl.glVertex3f(v1[0], v1[1], v1[2])
	gl.glVertex3f(v2[0], v2[1], v2[2])
	gl.glVertex3f(v3[0], v3[1], v3[2])

	n = -n
	gl.glNormal3f(n[0], n[1], n[2])
	gl.glVertex3f(v3[0], v3[1], v3[2])
	gl.glVertex3f(v2[0], v2[1], v2[2])
	gl.glVertex3f(v1[0], v1[1], v1[2])


def double_sided_quad(gl, v1, v2, v3, v4):
	double_sided_triangle(gl, v1, v2, v3)
	double_sided_triangle(gl, v4, v2, v3)


def set_color(gl, c):
	gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())


def set_glsl_color(program, c):
	program.setUniformValue('color', c)


def draw_surfaces(gl, surfaces):
	gl.glBegin(gl.GL_TRIANGLES)
	for surface in surfaces:
		for triangle in surface.get_faces_normals():
			double_sided_triangle(gl, triangle[0], triangle[1], triangle[2])
	gl.glEnd()


def draw_cube(gl, size, position):
	gl.glBegin(gl.GL_TRIANGLES)
	p = position
	s = size / 2
	v1 = Vertex(p.x + s, p.y + s, p.z + s).xyz
	v2 = Vertex(p.x + s, p.y + s, p.z - s).xyz
	v3 = Vertex(p.x + s, p.y - s, p.z + s).xyz
	v4 = Vertex(p.x + s, p.y - s, p.z - s).xyz
	v5 = Vertex(p.x - s, p.y + s, p.z + s).xyz
	v6 = Vertex(p.x - s, p.y + s, p.z - s).xyz
	v7 = Vertex(p.x - s, p.y - s, p.z + s).xyz
	v8 = Vertex(p.x - s, p.y - s, p.z - s).xyz
	double_sided_quad(gl, v1, v2, v3, v4)
	double_sided_quad(gl, v1, v2, v5, v6)
	double_sided_quad(gl, v1, v3, v5, v7)
	double_sided_quad(gl, v2, v4, v6, v8)
	double_sided_quad(gl, v7, v8, v3, v4)
	double_sided_quad(gl, v5, v6, v7, v8)
	gl.glEnd()


class GlDrawable(object):
	def __init__(self, gen_list_index):
		self._gen_list_index = gen_list_index

	def feature_changed(self, event):
		self.redraw()

	def redraw(self, gl, show_surfaces):
		pass

	@property
	def get_gen_list(self):
		return self._gen_list_index

	@property
	def vertices(self):
		return []

	@property
	def normals(self):
		return []

	@property
	def color(self):
		return QColor(180, 180, 180, 255)

	@property
	def edge_color(self):
		return QColor(180, 180, 180, 255)


class GlPlaneDrawable(GlDrawable):
	def __init__(self, gen_list_index, plane_feature: Feature):
		GlDrawable.__init__(self, gen_list_index)
		self._plane_feature = plane_feature
		self._plane_color = QColor(0, 150, 200, 15)
		self._plane_color_edge = QColor(0, 150, 200, 180)
		self._vertices = []
		self._normals = []
		plane_feature.add_change_handler(self.on_plane_changed)

	def on_plane_changed(self, event):
		self._vertices = []
		self._normals = []

	def redraw(self, gl, show_surfaces):
		self._vertices = []
		self._normals = []
		gl.glNewList(self._gen_list_index, gl.GL_COMPILE)
		gl.glDisable(gl.GL_LIGHT0)
		gl.glDisable(gl.GL_LIGHTING)
		p = self._plane_feature.get_vertex('p')
		xd = self._plane_feature.get_vertex('xd')
		yd = self._plane_feature.get_vertex('yd')
		parent = self._plane_feature.get_feature_parent()
		limits = parent.get_limits()
		size1 = max(np.absolute(limits[0].xyz))
		size2 = max(np.absolute(limits[1].xyz))
		size = max(size1, size2) * 1.2
		v1 = p.xyz * size - xd.xyz * size + yd.xyz * size
		v2 = p.xyz * size - xd.xyz * size - yd.xyz * size
		v3 = p.xyz * size + xd.xyz * size + yd.xyz * size
		v4 = p.xyz * size + xd.xyz * size - yd.xyz * size
		self.draw_feature_plane(gl, v1, v2, v3, v4)
		gl.glEndList()

	@property
	def color(self):
		return self._plane_color

	@property
	def edge_color(self):
		return self._plane_color_edge

	def draw_feature_plane(self, gl, v1, v2, v3, v4):
		gl.glDisable(gl.GL_DEPTH_TEST)
		gl.glBegin(gl.GL_TRIANGLES)
		set_color(gl, self._plane_color)

		m = 2
		for i in range(m):
			for l in range(m):
				delta_x_1 = float(i) / float(m)
				delta_x_2 = float(i + 1.0) / float(m)
				delta_y_1 = float(l) / float(m)
				delta_y_2 = float(l + 1.0) / float(m)
				ul = v1 + (v2 - v1) * delta_x_1 + (v3 - v1) * delta_y_1
				ll = v1 + (v2 - v1) * delta_x_1 + (v3 - v1) * delta_y_2
				ur = v1 + (v2 - v1) * delta_x_2 + (v3 - v1) * delta_y_1
				lr = v1 + (v2 - v1) * delta_x_2 + (v3 - v1) * delta_y_2
				double_sided_triangle(gl, ul, ll, ur)
				double_sided_triangle(gl, ur, lr, ll)
		gl.glEnd()
		gl.glEnable(gl.GL_DEPTH_TEST)
		gl.glLineWidth(2.0)
		gl.glBegin(gl.GL_LINES)
		set_color(gl, self._plane_color_edge)
		gl.glVertex3d(v1[0], v1[1], v1[2])
		gl.glVertex3d(v2[0], v2[1], v2[2])
		gl.glVertex3d(v2[0], v2[1], v2[2])
		gl.glVertex3d(v4[0], v4[1], v4[2])
		gl.glVertex3d(v4[0], v4[1], v4[2])
		gl.glVertex3d(v3[0], v3[1], v3[2])
		gl.glVertex3d(v3[0], v3[1], v3[2])
		gl.glVertex3d(v1[0], v1[1], v1[2])
		gl.glEnd()

	@property
	def vertices(self):
		if len(self._vertices) == 0:
			p = self._plane_feature.get_vertex('p')
			xd = self._plane_feature.get_vertex('xd')
			yd = self._plane_feature.get_vertex('yd')
			parent = self._plane_feature.get_feature_parent()
			limits = parent.get_limits()
			size1 = max(np.absolute(limits[0].xyz))
			size2 = max(np.absolute(limits[1].xyz))
			size = max(size1, size2) * 1.2
			v1 = p.xyz * size - xd.xyz * size + yd.xyz * size
			v2 = p.xyz * size - xd.xyz * size - yd.xyz * size
			v3 = p.xyz * size + xd.xyz * size + yd.xyz * size
			v4 = p.xyz * size + xd.xyz * size - yd.xyz * size
			self._vertices.append(v1)
			self._vertices.append(v2)
			self._vertices.append(v3)
			self._vertices.append(v3)
			self._vertices.append(v2)
			self._vertices.append(v4)
		return self._vertices

	@property
	def normals(self):
		if len(self._normals) == 0:
			for vert in self._vertices:
				self._normals.append([0, 0, 0])
		return self._normals

	@property
	def lines(self):
		lines = []
		verts = self.vertices
		lines.append(verts[0])
		lines.append(verts[1])
		lines.append(verts[1])
		lines.append(verts[5])
		lines.append(verts[5])
		lines.append(verts[2])
		lines.append(verts[2])
		lines.append(verts[0])
		return lines


def draw_lines(gl, lines):
	gl.glLineWidth(2.0)
	gl.glBegin(gl.GL_LINES)
	for line in lines:
		gl.glVertex3d(line[0], line[1], line[2])
	gl.glEnd()


class GlPartDrawable(GlDrawable):
	def __init__(self, gen_list_index, part):
		GlDrawable.__init__(self, gen_list_index)
		self._part = part
		self._part_color = QColor(160, 160, 160, 255)
		self._part_color_edge = QColor(140, 140, 140, 255)
		# self._part_color_edge = QColor(10, 10, 10, 255)
		self._lines = []
		self._vertices = []
		self._normals = []

	def redraw(self, gl, show_surfaces):
		gl.glNewList(self._gen_list_index, gl.GL_COMPILE)
		gl.glEnable(gl.GL_COLOR_MATERIAL)
		set_color(gl, self._part_color)
		gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, [0.5, 0.5, 0.5, 0.5])
		lines = self._part.get_lines()

		if show_surfaces:
			set_color(gl, self._part_color)
			gl.glEnable(gl.GL_LIGHT0)
			gl.glEnable(gl.GL_LIGHTING)
			surfaces = self._part.get_surfaces()
		# draw_surfaces(gl, surfaces)

		# draw_cube(gl, 1, Vertex(3, 0, 0))

		set_color(gl, self._part_color_edge)
		gl.glDisable(gl.GL_LIGHT0)
		gl.glDisable(gl.GL_LIGHTING)
		draw_lines(gl, lines)

		gl.glEndList()

	@property
	def vertices(self):
		if len(self._vertices) == 0:
			surfaces = self._part.get_surfaces()
			for surface in surfaces:
				faces, norms = surface.get_faces_normals()
				self._vertices.extend(faces)
				self._normals.extend(norms)
		return self._vertices

	@property
	def normals(self):
		return self._normals

	@property
	def lines(self):
		if len(self._lines) == 0:
			self._lines = self._part.get_lines()
		return self._lines

from io import StringIO

from PyPDF2 import PdfFileWriter

from reportlab.lib.pagesizes import letter, A0
from reportlab.pdfgen import canvas

from Business.Undo import DoObject
from Data.Sketch import Sketch, Text, Alignment


class CreateDrawingDoObject(DoObject):
	def __init__(self):
		DoObject.__init__(self)

	def undo(self):
		pass

	def redo(self):
		pass


def print_drawing(document, drawing):
	output = PdfFileWriter()
	page = output.addBlankPage(drawing.size[0], drawing.size[1])
	packet = StringIO()
	cv = canvas.Canvas(packet, pagesize=A0)

	cv.circle(50, 250, 20, stroke=1, fill=0)
	output_stream = open("document-output.pdf", "wb")
	output.write(output_stream)
	output_stream.close()


def create_empty_header(document):
	header = document.get_drawings().create_header()
	width = 0.15
	height = 0.12
	ts = 0.001
	pnt1 = header.create_keypoint(0, 0, 0)
	pnt2 = header.create_keypoint(width, 0, 0)
	pnt3 = header.create_keypoint(width, height, 0)
	pnt4 = header.create_keypoint(0, height, 0)

	header.create_line_edge(pnt1, pnt2).style_name = "border"
	header.create_line_edge(pnt2, pnt3).style_name = "border"
	header.create_line_edge(pnt3, pnt4).style_name = "border"
	header.create_line_edge(pnt4, pnt1).style_name = "border"
	return header


def create_default_header(document):
	header = document.get_drawings().create_header()
	header.name = "Default header"
	width = 0.15
	height = 0.12
	titleHeight = 0.02
	ts = 0.001
	widthRevision = 0.010
	valueTextHeight = 0.003
	textDist = valueTextHeight * 2
	rev_height = 0.01
	document.styles.get_edge_style_by_name("thin").thickness = 0.00018
	document.styles.get_edge_style_by_name("border").thickness = 0.0005

	captionTextHeight = 0.002
	pnt1 = header.create_keypoint(0, 0, 0)
	pnt2 = header.create_keypoint(width, 0, 0)
	pnt3 = header.create_keypoint(width, height + titleHeight, 0)
	pnt4 = header.create_keypoint(0, height + titleHeight, 0)
	pnt5 = header.create_keypoint(0, height / 2, 0)
	pnt6 = header.create_keypoint(width, height / 2, 0)
	pnt7 = header.create_keypoint(width / 2, height, 0)
	pnt8 = header.create_keypoint(width / 2, 0.0, 0)
	pnt9 = header.create_keypoint(width / 2, height / 4, 0)
	pnt10 = header.create_keypoint(width, height / 4, 0)
	pnt11 = header.create_keypoint(width, 3 * height / 8, 0)
	pnt12 = header.create_keypoint(width / 2, 3 * height / 8, 0)
	pnt13 = header.create_keypoint(3 * width / 4, 1 * height / 4, 0)
	pnt14 = header.create_keypoint(3 * width / 4, height / 2, 0)
	pnt15 = header.create_keypoint(widthRevision, height, 0)
	pnt16 = header.create_keypoint(widthRevision, height / 2, 0)
	pnt17 = header.create_keypoint(width, height, 0)
	pnt18 = header.create_keypoint(0, height, 0)
	pnt19 = header.create_keypoint(5 * width / 8, 1 * height / 2, 0)
	pnt20 = header.create_keypoint(5 * width / 8, height, 0)
	pnt21 = header.create_keypoint(6 * width / 8, 1 * height / 2, 0)
	pnt22 = header.create_keypoint(6 * width / 8, height, 0)
	pnt23 = header.create_keypoint(7 * width / 8, 1 * height / 2, 0)
	pnt24 = header.create_keypoint(7 * width / 8, height, 0)
	pnt25 = header.create_keypoint(width / 2 + textDist / 2, textDist * 2, 0)
	pnt26 = header.create_keypoint(4 * width / 5 + textDist / 2, textDist * 2, 0)

	pnt27 = header.create_keypoint(9 * width / 10, textDist, 0)
	pnt28 = header.create_keypoint(9 * width / 10 - textDist*1.5, textDist*4.5, 0)
	pnt29 = header.create_keypoint(9 * width / 10 + textDist*1.5, textDist*4.5, 0)

	# pnt26 = header.create_keypoint(4 * width / 5 + textDist / 2, textDist * 2, 0)
	header.create_line_edge(pnt1, pnt2).style_name = "border"
	header.create_line_edge(pnt2, pnt3).style_name = "border"
	header.create_line_edge(pnt3, pnt4).style_name = "border"
	header.create_line_edge(pnt4, pnt1).style_name = "border"
	header.create_line_edge(pnt5, pnt6)
	header.create_line_edge(pnt7, pnt8)
	header.create_line_edge(pnt9, pnt10)
	header.create_line_edge(pnt12, pnt11)
	header.create_line_edge(pnt13, pnt14)
	header.create_line_edge(pnt15, pnt16)
	header.create_line_edge(pnt17, pnt18)
	header.create_line_edge(pnt19, pnt20)
	header.create_line_edge(pnt21, pnt22)
	header.create_line_edge(pnt23, pnt24)
	header.create_line_edge(pnt25, pnt26).style_name = "thin"
	header.create_line_edge(pnt27, pnt28).style_name = "thin"
	header.create_line_edge(pnt28, pnt29).style_name = "thin"
	header.create_line_edge(pnt27, pnt29).style_name = "thin"

	for i in range(6):
		pnta = header.create_keypoint(width, height / 2 + i * rev_height, 0)
		pntb = header.create_keypoint(0, height / 2 + i * rev_height, 0)
		pntrev = header.create_keypoint(widthRevision / 2, height / 2 + rev_height / 2 + i * rev_height, 0)
		pntrtit = header.create_keypoint(widthRevision + textDist / 2, height / 2 + rev_height / 2 + i * rev_height, 0)
		pntdt = header.create_keypoint(9 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0)
		pntmk = header.create_keypoint(11 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0)
		pntchk = header.create_keypoint(13 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0)
		pntapp = header.create_keypoint(15 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0)
		if (i == 0):
			header.create_text(pntrev, "Rev", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_text(pntrtit, "Revision Title", valueTextHeight).horizontal_alignment = Alignment.Right
			header.create_text(pntdt, "Date", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_text(pntmk, "Maker", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_text(pntchk, "Checker", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_text(pntapp, "Approver", valueTextHeight).horizontal_alignment = Alignment.Center
		else:
			revtext = ""
			if (i == 1):
				revtext = "First issue"
			header.create_attribute(pntrev, "Rev" + str(i), str(i - 1), valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_attribute(pntrtit, "RevText" + str(i), revtext, valueTextHeight).horizontal_alignment = Alignment.Right
			header.create_attribute(pntdt, "RevDate" + str(i), "", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_attribute(pntmk, "RevMaker" + str(i), "", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_attribute(pntchk, "RevChecker" + str(i), "", valueTextHeight).horizontal_alignment = Alignment.Center
			header.create_attribute(pntapp, "RevApprover" + str(i), "", valueTextHeight).horizontal_alignment = Alignment.Center
		header.create_line_edge(pnta, pntb)

	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 1, 0), "DocTitle4", "Document Title 4",
													valueTextHeight).horizontal_alignment = Alignment.Right
	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 2, 0), "DocTitle3", "Document Title 3",
													valueTextHeight).horizontal_alignment = Alignment.Right
	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 3, 0), "DocTitle2", "Document Title 2",
													valueTextHeight).horizontal_alignment = Alignment.Right
	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 4, 0), "DocTitle1", "Document Title 1",
													valueTextHeight).horizontal_alignment = Alignment.Right

	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 7, 0), "JobTitle3", "Job Title 3",
													valueTextHeight).horizontal_alignment = Alignment.Right
	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 8, 0), "JobTitle2", "Job Title 2",
													valueTextHeight).horizontal_alignment = Alignment.Right
	header.create_attribute(header.create_keypoint(textDist / 2, textDist * 9, 0), "JobTitle1", "Job Title 1",
													valueTextHeight).horizontal_alignment = Alignment.Right

	header.create_text(header.create_keypoint(width / 2 + textDist / 2, textDist * 1, 0), "Document number",
										 valueTextHeight).horizontal_alignment = Alignment.Right
	header.create_attribute(header.create_keypoint(width / 2 + textDist / 2, textDist * 3, 0), "DocNumber", "123456",
													valueTextHeight * 1.5).horizontal_alignment = Alignment.Right

	header.create_attribute(header.create_keypoint(width * 5 / 8, height * 5/16, 0), "Scale", "1 : 1",
													valueTextHeight).horizontal_alignment = Alignment.Center

	scale_text = header.create_text(header.create_keypoint(width * 1 / 2 + textDist / 2, height / 4 + textDist /2,  0), "Scale",
										 valueTextHeight/2).horizontal_alignment = Alignment.Right
	size_text = header.create_text(header.create_keypoint(width * 1 / 2 + textDist / 2, height * 3 / 8+ textDist / 2, 0), "Size",
																	valueTextHeight / 2).horizontal_alignment = Alignment.Right

	item_text = header.create_text(header.create_keypoint(width * 3 / 4 + textDist / 2, height * 3 / 8 + textDist / 2, 0), "Item",
																	valueTextHeight / 2).horizontal_alignment = Alignment.Right

	return header


def add_field_to_drawing(doc, drawing):
	counter = 1
	name = "New Field %d" % counter
	while drawing.get_field(name) is not None:
		counter += 1
		name = "New Field %d" % counter
	drawing.add_field(name, "Field value")


def add_sketch_to_drawing(document, drawing, sketch, scale, offset):
	return drawing.create_sketch_view(sketch, scale, offset)


def create_add_sketch_to_drawing(document, drawing, sketch, scale, offset):
	pass


def add_part_to_drawing(doc, drawing, part, scale, offset):
	return drawing.create_part_view(part, scale, offset)

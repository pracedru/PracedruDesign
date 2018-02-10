from io import StringIO

from PyPDF2 import PdfFileWriter

from reportlab.lib.pagesizes import letter, A0
from reportlab.pdfgen import canvas

from Data.Sketch import Sketch, Text


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
  pnt1 = header.create_key_point(0, 0, 0, ts)
  pnt2 = header.create_key_point(width, 0, 0, ts)
  pnt3 = header.create_key_point(width, height, 0, ts)
  pnt4 = header.create_key_point(0, height, 0, ts)

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

  captionTextHeight = 0.002
  pnt1 = header.create_key_point(0, 0, 0, ts)
  pnt2 = header.create_key_point(width, 0, 0, ts)
  pnt3 = header.create_key_point(width, height + titleHeight, 0, ts)
  pnt4 = header.create_key_point(0, height + titleHeight, 0, ts)
  pnt5 = header.create_key_point(0, height / 2, 0, ts)
  pnt6 = header.create_key_point(width, height / 2, 0, ts)
  pnt7 = header.create_key_point(width / 2, height, 0, ts)
  pnt8 = header.create_key_point(width / 2, 0.0, 0, ts)
  pnt9 = header.create_key_point(width / 2, height / 4, 0, ts)
  pnt10 = header.create_key_point(width, height / 4, 0, ts)
  pnt11 = header.create_key_point(width, 3 * height / 8, 0, ts)
  pnt12 = header.create_key_point(width / 2, 3 * height / 8, 0, ts)
  pnt13 = header.create_key_point(3 * width / 4, 1 * height / 4, 0, ts)
  pnt14 = header.create_key_point(3 * width / 4, height / 2, 0, ts)
  pnt15 = header.create_key_point(widthRevision, height, 0, ts)
  pnt16 = header.create_key_point(widthRevision, height / 2, 0, ts)
  pnt17 = header.create_key_point(width, height, 0, ts)
  pnt18 = header.create_key_point(0, height, 0, ts)
  pnt19 = header.create_key_point(5 * width / 8, 1 * height / 2, 0, ts)
  pnt20 = header.create_key_point(5 * width / 8, height, 0, ts)
  pnt21 = header.create_key_point(6 * width / 8, 1 * height / 2, 0, ts)
  pnt22 = header.create_key_point(6 * width / 8, height, 0, ts)
  pnt23 = header.create_key_point(7 * width / 8, 1 * height / 2, 0, ts)
  pnt24 = header.create_key_point(7 * width / 8, height, 0, ts)
  pnt25 = header.create_key_point(width / 2 + textDist / 2, textDist * 2, 0, ts)
  pnt26 = header.create_key_point(4 * width / 5 + textDist / 2, textDist * 2, 0, ts)
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
  header.create_line_edge(pnt25, pnt26)
  for i in range(6):
    pnta = header.create_key_point(width, height / 2 + i * rev_height, 0, ts)
    pntb = header.create_key_point(0, height / 2 + i * rev_height, 0, ts)
    pntrev = header.create_key_point(widthRevision / 2, height / 2 + rev_height / 2 + i * rev_height, 0, ts)
    pntrtit = header.create_key_point(widthRevision + textDist / 2, height / 2 + rev_height / 2 + i * rev_height, 0, ts)
    pntdt = header.create_key_point(9 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0, ts)
    pntmk = header.create_key_point(11 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0, ts)
    pntchk = header.create_key_point(13 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0, ts)
    pntapp = header.create_key_point(15 * width / 16, height / 2 + rev_height / 2 + i * rev_height, 0, ts)
    if (i == 0):
      header.create_text(pntrev, "Rev", valueTextHeight).horizontal_alignment = Text.Center
      header.create_text(pntrtit, "Revision Title", valueTextHeight).horizontal_alignment = Text.Right
      header.create_text(pntdt, "Date", valueTextHeight).horizontal_alignment = Text.Center
      header.create_text(pntmk, "Maker", valueTextHeight).horizontal_alignment = Text.Center
      header.create_text(pntchk, "Checker", valueTextHeight).horizontal_alignment = Text.Center
      header.create_text(pntapp, "Approver", valueTextHeight).horizontal_alignment = Text.Center
    else:
      revtext = ""
      if (i == 1):
        revtext = "First issue"
      header.create_attribute(pntrev, "Rev" + str(i), str(i - 1), valueTextHeight).horizontal_alignment = Text.Center
      header.create_attribute(pntrtit, "RevText" + str(i), revtext, valueTextHeight).horizontal_alignment = Text.Right
      header.create_attribute(pntdt, "RevDate" + str(i), "", valueTextHeight).horizontal_alignment = Text.Center
      header.create_attribute(pntmk, "RevMaker" + str(i), "", valueTextHeight).horizontal_alignment = Text.Center
      header.create_attribute(pntchk, "RevChecker" + str(i), "", valueTextHeight).horizontal_alignment = Text.Center
      header.create_attribute(pntapp, "RevApprover" + str(i), "", valueTextHeight).horizontal_alignment = Text.Center
    header.create_line_edge(pnta, pntb)

  header.create_attribute(header.create_key_point(textDist / 2, textDist * 1, 0, ts), "DocTitle3", "Document Title 3",
                          valueTextHeight).horizontal_alignment = Text.Right
  header.create_attribute(header.create_key_point(textDist / 2, textDist * 2, 0, ts), "DocTitle2", "Document Title 2",
                          valueTextHeight).horizontal_alignment = Text.Right
  header.create_attribute(header.create_key_point(textDist / 2, textDist * 3, 0, ts), "DocTitle1", "Document Title 1",
                          valueTextHeight).horizontal_alignment = Text.Right

  header.create_text(header.create_key_point(width / 2 + textDist / 2, textDist * 1, 0, ts), "Document number",
                     valueTextHeight).horizontal_alignment = Text.Right

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

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
    width = 0.18
    height = 0.12
    titleHeight = 0.02
    ts = 0.001
    widthRevision = 0.012
    valueTextHeight = 0.003
    textDist = valueTextHeight*2

    captionTextHeight = 0.002
    pnt1 = header.create_key_point(0, 0, 0, ts)
    pnt2 = header.create_key_point(width, 0, 0, ts)
    pnt3 = header.create_key_point(width, height + titleHeight, 0, ts)
    pnt4 = header.create_key_point(0,height + titleHeight, 0, ts)
    pnt5 = header.create_key_point(0, height/2, 0, ts)
    pnt6 = header.create_key_point(width, height/2, 0, ts)
    pnt7 = header.create_key_point(width/2, height, 0, ts)
    pnt8 = header.create_key_point(width/2, 0.0, 0, ts)
    pnt9 = header.create_key_point(width/2, height/4, 0, ts)
    pnt10 = header.create_key_point(width, height/4, 0, ts)
    pnt11 = header.create_key_point(width, 3 * height / 8, 0, ts)
    pnt12 = header.create_key_point(width/2, 3 * height / 8, 0, ts)
    pnt13 = header.create_key_point(3 * width / 4, 1 * height / 4, 0, ts)
    pnt14 = header.create_key_point(3 * width / 4, height / 2 , 0, ts)
    pnt15 = header.create_key_point(widthRevision, height, 0, ts)
    pnt16 = header.create_key_point(widthRevision, height/2, 0, ts)
    pnt17 = header.create_key_point(width, height, 0, ts)
    pnt18 = header.create_key_point(0, height, 0, ts)
    pnt19 = header.create_key_point(4 * width / 6, 1 * height / 2, 0, ts)
    pnt20 = header.create_key_point(4 * width / 6, height, 0, ts)
    pnt21 = header.create_key_point(5 * width / 6, 1 * height / 2, 0, ts)
    pnt22 = header.create_key_point(5 * width / 6, height, 0, ts)
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
    for i in range(6):
        pnta = header.create_key_point(width, height / 2 + i * 0.01, 0, ts)
        pntb = header.create_key_point(0, height / 2 + i * 0.01, 0, ts)
        header.create_line_edge(pnta, pntb)

    header.create_attribute(header.create_key_point(textDist, textDist, 0, ts), "DocTitle3", "Document Title 3", valueTextHeight).horizontal_alignment = Text.Right
    header.create_attribute(header.create_key_point(textDist, textDist * 2, 0, ts), "DocTitle2", "Document Title 2", valueTextHeight).horizontal_alignment = Text.Right
    header.create_attribute(header.create_key_point(textDist, textDist * 3, 0, ts), "DocTitle1", "Document Title 1", valueTextHeight).horizontal_alignment = Text.Right


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

from io import StringIO

from PyPDF2 import PdfFileWriter

from reportlab.lib.pagesizes import letter, A0
from reportlab.pdfgen import canvas

from Data.Sketch import Sketch


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
    pnt4 = header.create_key_point(0,height, 0, ts)
    pnt5 = header.create_key_point(0, height/2, 0, ts)
    pnt6 = header.create_key_point(width, height/2, 0, ts)
    pnt7 = header.create_key_point(width/2, height, 0, ts)
    pnt8 = header.create_key_point(width/2, 0.0, 0, ts)
    pnt9 = header.create_key_point(width/2, height/4, 0, ts)
    pnt10 = header.create_key_point(width, height/4, 0, ts)
    pnt11 = header.create_key_point(width, 3 * height / 8, 0, ts)
    pnt12 = header.create_key_point(width/2, 3 * height / 8, 0, ts)
    pnt13 = header.create_key_point(3 * width / 4, 1 * height / 4, 0, ts)
    pnt14 = header.create_key_point(3 * width / 4, height , 0, ts)
    header.create_line_edge(pnt1, pnt2).style_name = "border"
    header.create_line_edge(pnt2, pnt3).style_name = "border"
    header.create_line_edge(pnt3, pnt4).style_name = "border"
    header.create_line_edge(pnt4, pnt1).style_name = "border"
    header.create_line_edge(pnt5, pnt6)
    header.create_line_edge(pnt7, pnt8)
    header.create_line_edge(pnt9, pnt10)
    header.create_line_edge(pnt12, pnt11)
    header.create_line_edge(pnt13, pnt14)
    for i in range(6):
        pnta = header.create_key_point(width, height / 2 + i * 0.01, 0, ts)
        pntb = header.create_key_point(0, height / 2 + i * 0.01, 0, ts)
        header.create_line_edge(pnta, pntb)




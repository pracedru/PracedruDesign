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
    pnt1 = header.create_key_point(0, 0, 0)
    pnt2 = header.create_key_point(0.2, 0, 0)
    pnt3 = header.create_key_point(0.2, 0.15, 0)
    pnt4 = header.create_key_point(0, 0.15, 0)
    header.create_line_edge(pnt1, pnt2)
    header.create_line_edge(pnt2, pnt3)
    header.create_line_edge(pnt3, pnt4)
    header.create_line_edge(pnt4, pnt1)

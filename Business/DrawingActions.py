from io import StringIO

from PyPDF2 import PdfFileWriter

from reportlab.lib.pagesizes import letter, A0
from reportlab.pdfgen import canvas


def print_drawing(document, drawing):
    output = PdfFileWriter()
    page = output.addBlankPage(drawing.size[0], drawing.size[1])
    packet = StringIO()
    cv = canvas.Canvas(packet, pagesize=A0)

    cv.circle(50, 250, 20, stroke=1, fill=0)
    output_stream = open("document-output.pdf", "wb")
    output.write(output_stream)
    output_stream.close()
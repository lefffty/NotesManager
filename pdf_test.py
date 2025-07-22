from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


canv = canvas.Canvas('test.pdf', pagesize=A4)

canv.drawString(50, 500, 'Some string')
canv.drawString(50, 100, 'Another string')

canv.save()

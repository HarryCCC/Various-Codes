import PyPDF2
import os

pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]
merger = PyPDF2.PdfFileMerger()

for pdf in pdfs:
    merger.append(pdf)

merger.write("combined.pdf")
merger.close()

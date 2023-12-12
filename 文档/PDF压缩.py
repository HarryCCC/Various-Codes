import PyPDF2
import os

pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]

for pdf_file in pdfs:
    input_pdf = PyPDF2.PdfFileReader(pdf_file)
    output_pdf = PyPDF2.PdfFileWriter()

    for i in range(input_pdf.getNumPages()):
        output_pdf.addPage(input_pdf.getPage(i))

    with open(f"{pdf_file[:-4]}_compressed.pdf", "wb") as output_stream:
        output_pdf.write(output_stream)

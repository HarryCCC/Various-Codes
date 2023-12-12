import PyPDF2

# Open the PDF file in read-binary mode
with open('sample.pdf', 'rb') as pdf_file:
    # Create a PdfReader object
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Get the number of pages in the PDF document
    num_pages = len(pdf_reader.pages)

    # Initialize the page counter and the word counter
    page_count = 1
    word_count = 0

    # Create the first output file
    output_file = open(f"output_{page_count}.txt", "w")

    # Loop through each page and write its contents to the output files
    for i in range(num_pages):
        # Get the page object
        page = pdf_reader.pages[i]

        # Extract the text from the page
        text = page.extract_text()

        # Split the text into words
        words = text.split()

        # Loop through each word and write it to the output file
        for word in words:
            # If the word count exceeds 2000, close the current output file
            # and create a new one
            if word_count >= 2000:
                output_file.close()
                page_count += 1
                output_file = open(f"output_{page_count}.txt", "w")
                word_count = 0

            # Write the word to the output file
            output_file.write(word + " ")
            word_count += 1

    # Close the last output file
    output_file.close()

# Close the PDF file
pdf_file.close()

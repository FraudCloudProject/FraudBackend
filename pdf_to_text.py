import fitz  # PyMuPDF

def pdf_to_text(file_path):
    # Open the PDF file
    doc = fitz.open(file_path)
    text = ""

    # Iterate through the pages and extract text
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()

    # Close the document
    doc.close()
    return text

if __name__ == "__main__":
    # Replace 'your_file.pdf' with the path to your PDF file
    pdf_path = 'your_file.pdf'
    extracted_text = pdf_to_text(pdf_path)
    
    # Print the extracted text or save it to a file
    print(extracted_text)
    # You could also write the text to a .txt file if needed
    with open("output.txt", "w", encoding="utf-8") as text_file:
        text_file.write(extracted_text)

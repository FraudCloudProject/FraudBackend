import pdfplumber

def pdf_to_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
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

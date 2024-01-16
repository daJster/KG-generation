import PyPDF2
import io
from params import PATH_TO_PDF_FILES

def get_text(file):
    """
    Extracts text from a PDF file.

    Args:
        file (UploadedFile): The PDF file to extract text from.

    Returns:
        str: The extracted text from the PDF file.
    """
    text = ""
    with io.BytesIO(file.read()) as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    return text


import fitz
from params import PATH_TO_PDF_FILES

def get_text(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:  # open document
        text = chr(12).join([page.get_text() for page in doc])
    return text


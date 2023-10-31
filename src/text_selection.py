import fitz

def get_text(files):
    text = []
    for file in files:
        with fitz.open(file) as doc:  # open document
            text = chr(12).join([page.get_text() for page in doc])
    return text
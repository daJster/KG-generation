import os
from params import PATH_TO_PDF_FILES

def get_files():
    files = []
    for file in os.listdir(PATH_TO_PDF_FILES):
        if file.endswith(".pdf") :
            files.append(file)
    return files
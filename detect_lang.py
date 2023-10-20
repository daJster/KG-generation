import os
import fitz
from langdetect import detect
import csv

def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        return "unknown"
    
def generate_file_lang(pdf_directory, csv_file, fieldnames) :
    if not os.path.exists(csv_file):
        # Create the CSV file with headers if it doesn't exist
        with open(csv_file, 'w', newline='') as csvfile :
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    count = 0
    for filename in os.listdir(pdf_directory) :
        count += 1
        print(f"files : {count}/{len(os.listdir(pdf_directory))}", end="\r")
        if filename.endswith('.pdf'):
            full_path = os.path.join(pdf_directory, filename)
            pdf_document = fitz.open(full_path)
            
            # take 3rd page to avoid abstract and title
            if len(pdf_document) > 2:
                page = pdf_document.load_page(2)
                text = page.get_text()
                language = detect_language(text)
                
                # Append the results to the CSV file
                with open(csv_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'Filename': filename, 'Language': language})
                    
    print(f"\nSaved to {csv_file}")

if __name__ == "__main__" :
    pdf_directory = './KG-100Mo/'
    csv_file = 'file_lang.csv'
    fieldnames = ['Filename', 'Language']
    generate_file_lang(pdf_directory=pdf_directory, csv_file=csv_file, fieldnames=fieldnames)
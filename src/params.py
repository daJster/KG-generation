from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from sentence_transformers import SentenceTransformer

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
rdf_model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")
merge_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


PATH_TO_PDF_FILES = "."
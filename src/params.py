from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer,util
import os 

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
rdf_model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")
merge_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


PATH_TO_PDF_FILES = os.path.abspath(".")+'/'
PATH_TO_RDF_FILES = os.path.abspath("../RDFs/")+'/'
PATH_TO_GRAPH_FILES = os.path.abspath("../graphs/")+'/'
ACTIVATE_SIMILARITY = True
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer,util
import torch
import os 


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
rdf_model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large").to(DEVICE)
merge_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2').to(DEVICE)


PATH_TO_PDF_FILES = os.path.abspath("./pdf-files/")+'/'
PATH_TO_RDF_FILES = os.path.abspath("../RDFs/")+'/'
PATH_TO_GRAPH_FILES = os.path.abspath("../graphs/")+'/'
ACTIVATE_SIMILARITY = False
from sentence_transformers import SentenceTransformer
from sentence_transformers import util


model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def compare_with_all_mini(str1, str2):
    """
    Calculate the similarity score between two strings.

    Parameters:
    str1 (str): The first string.
    str2 (str): The second string.

    Returns:
    float: The similarity score between the two strings.
    """
    embeddings = model.encode([str1, str2])
    cosine_scores = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
    return cosine_scores

# print(compare_with_all_mini("I like to drink apple juice.", "I like to eat apples."))
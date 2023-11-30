from params import merge_model
from sentence_transformers import util

def similarity_score(trp1, trp2) :
    """
    Calculate the similarity score between two triples.

    Parameters:
    trp1 (dict): The first triple containing 'head', 'type', and 'tail' fields.
    trp2 (dict): The second triple containing 'head', 'type', and 'tail' fields.

    Returns:
    float: The similarity score between the two triples.
    """
    fields = ['head', 'type', 'tail']
    
    # Encode the elements for each field
    embeddings = [merge_model.encode([trp1[field], trp2[field]]) for field in fields]

    # Calculate cosine similarity for each field
    cosine_scores = [util.pytorch_cos_sim(emb[0], emb[1]).item() for emb in embeddings]

    # Define weights for each field (you can adjust these weights as needed)
    weights = {'head': 1.0, 'type': 1.0, 'tail': 1.0}

    # Calculate the weighted average of the cosine similarity scores
    weighted_sum = sum(weights[field] * score for field, score in zip(fields, cosine_scores))
    total_weight = sum(weights[field] for field in fields)
    similarity = weighted_sum / total_weight

    return similarity

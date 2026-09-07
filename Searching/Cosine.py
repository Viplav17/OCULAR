import numpy as np
from Searching.API_tk import token

SERPAPI_API_KEY = token
MATCH_THRESHOLD = 0.6

def cosine_distance(vec_a, vec_b):
    """Calculates cosine distance between two numerical vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return 1.0 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

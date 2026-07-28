import math
from typing import List, Dict, Any, Tuple

class SimilarityEngine:
    """
    Computes cosine similarity between vectors.
    Designed to run entirely locally in standard Python without heavy dependencies.
    """
    
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """
        Calculates the cosine similarity between two vectors.
        Assumes both vectors are of the same length and are pre-normalized to unit length.
        """
        if len(v1) != len(v2):
            raise ValueError("Vectors must be of the same dimension.")
            
        dot_product = sum(a * b for a, b in zip(v1, v2))
        return round(dot_product, 6)

    @classmethod
    def search(cls, query_vector: List[float], db_vectors: List[Dict[str, Any]], top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Performs a brute-force similarity search against the local vector db.
        Returns the top_k matching records and their scores.
        """
        results = []
        for record in db_vectors:
            score = cls.cosine_similarity(query_vector, record["vector"])
            results.append((record, score))
            
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

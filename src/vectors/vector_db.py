import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any, Tuple

class VectorDB:
    """
    A FAISS-based vector storage and retrieval system for scalable similarity search.
    """
    
    def __init__(self, db_path: str):
        # db_path is maintained for backward compatibility with older callers
        self.db_dir = os.path.dirname(db_path) or "."
        self.index_path = os.path.join(self.db_dir, "index.faiss")
        self.meta_path = os.path.join(self.db_dir, "metadata.json")
        self.dimension = 768  # Gemini embedding-001 dimension
        self.metadata = []
        
        # FAISS index for inner product (equivalent to cosine similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self._load()
        
    def _load(self):
        """Loads FAISS index and metadata from disk if they exist."""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        if os.path.exists(self.meta_path):
            with open(self.meta_path, 'r', encoding='utf-8') as f:
                try:
                    self.metadata = json.load(f)
                except json.JSONDecodeError:
                    self.metadata = []
                    
    def _save(self):
        """Saves FAISS index and metadata to disk."""
        os.makedirs(self.db_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=4)
            
    def add_vector(self, issue_id: str, vector: List[float], metadata: Dict[str, Any] = None):
        """
        Adds a normalized vector and its metadata to the FAISS index.
        """
        vec_np = np.array([vector], dtype=np.float32)
        faiss.normalize_L2(vec_np)
        self.index.add(vec_np)
        
        record = {
            "issue_id": issue_id,
            "metadata": metadata or {}
        }
        self.metadata.append(record)
        self._save()
        
    def get_all_vectors(self) -> List[Dict[str, Any]]:
        """Returns all metadata (kept for compatibility)."""
        return self.metadata

    def search(self, query_vector: List[float], top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the FAISS index for the most similar vectors.
        Returns a list of tuples containing (metadata_record, similarity_score).
        """
        if self.index.ntotal == 0:
            return []
            
        vec_np = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(vec_np)
        
        distances, indices = self.index.search(vec_np, min(top_k, self.index.ntotal))
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:
                score = float(distances[0][i])
                results.append((self.metadata[idx], score))
                
        return results

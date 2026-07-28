import os
import json
from typing import List, Dict, Any

class VectorDB:
    """
    A lightweight, file-based vector storage system requiring NO external database.
    Stores vectors and their associated metadata in a JSON format.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.vectors = []
        self._load()
        
    def _load(self):
        """Loads vectors from disk if the file exists."""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                try:
                    self.vectors = json.load(f)
                except json.JSONDecodeError:
                    self.vectors = []
                    
    def _save(self):
        """Saves current vectors to disk."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.vectors, f, indent=4)
            
    def add_vector(self, issue_id: str, vector: List[float], metadata: Dict[str, Any] = None):
        """
        Adds a vector and its metadata to the store.
        """
        record = {
            "issue_id": issue_id,
            "vector": vector,
            "metadata": metadata or {}
        }
        self.vectors.append(record)
        self._save()
        
    def get_all_vectors(self) -> List[Dict[str, Any]]:
        return self.vectors

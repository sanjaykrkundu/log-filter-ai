import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vectors.vector_db import VectorDB
from src.vectors.embedding_gen import EmbeddingGenerator
from src.vectors.similarity import SimilarityEngine

def main():
    parser = argparse.ArgumentParser(description="Inspect vectors and test similarity search.")
    parser.add_argument("db_path", help="Path to the local vectors.json file")
    parser.add_argument("--query", "-q", help="Text to search for against the DB", type=str)
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db_path):
        print(f"Error: Vector DB not found at {args.db_path}")
        sys.exit(1)
        
    db = VectorDB(args.db_path)
    records = db.get_all_vectors()
    
    print(f"Loaded {len(records)} vectors from DB.")
    
    if args.query:
        print(f"\nSearching for: '{args.query}'")
        generator = EmbeddingGenerator()
        query_vec = generator.generate_embedding(args.query)
        
        results = SimilarityEngine.search(query_vec, records, top_k=3)
        
        print("\n--- Top Matches ---")
        for i, (record, score) in enumerate(results):
            issue_id = record.get("issue_id", "Unknown")
            print(f"[{i+1}] Score: {score:.4f} | Issue: {issue_id}")
    else:
        print("\n--- Stored Issues ---")
        for r in records:
            print(f"- {r.get('issue_id')}")

if __name__ == "__main__":
    main()

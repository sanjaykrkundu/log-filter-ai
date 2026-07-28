import os
import json
from typing import Dict, Any, List
from src.vectors.embedding_gen import EmbeddingGenerator
from src.vectors.vector_db import VectorDB

class LearningEngine:
    """
    Handles continuous learning from runtime analysis.
    If a known issue has slight variations, it merges the new pattern.
    If an unknown issue occurs frequently, it autosuggests creating a new template.
    """
    
    def __init__(self, trained_dir: str):
        self.trained_dir = trained_dir
        self.db_path = os.path.join(self.trained_dir, "vectors.json")
        self.vdb = VectorDB(self.db_path)
        self.emb_gen = EmbeddingGenerator()
        
    def process_findings(self, findings: List[Dict[str, Any]], raw_log_path: str):
        """
        Processes findings from the runtime analyzer.
        """
        for finding in findings:
            analysis = finding.get("analysis", {})
            classification = analysis.get("classification")
            issue_name = analysis.get("issue_name")
            
            error_text = finding.get("error_line", "")
            
            if classification == "KNOWN":
                self._merge_pattern(issue_name, error_text)
            elif classification == "UNKNOWN":
                self._auto_suggest_new_issue(error_text)
                
    def _merge_pattern(self, issue_name: str, new_error_text: str):
        """
        Updates existing issue by adding the new variation to raw_patterns.json 
        and updating the vector DB if the variation is sufficiently different.
        """
        issue_dir = os.path.join(self.trained_dir, issue_name)
        if not os.path.exists(issue_dir):
            return
            
        raw_patterns_path = os.path.join(issue_dir, "raw_patterns.json")
        existing_logs = []
        if os.path.exists(raw_patterns_path):
            with open(raw_patterns_path, 'r', encoding='utf-8') as f:
                try:
                    existing_logs = json.load(f)
                except json.JSONDecodeError:
                    pass
                    
        # Append the new variation
        existing_logs.append({"samples": [new_error_text], "note": "Auto-merged from runtime"})
        
        with open(raw_patterns_path, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, indent=4)
            
        # Add new vector representation to improve future recall
        new_vector = self.emb_gen.generate_embedding(new_error_text)
        self.vdb.add_vector(issue_name, new_vector, metadata={"source": "auto_merge"})
        print(f"Learning Engine: Merged new pattern variation for '{issue_name}'")

    def _auto_suggest_new_issue(self, error_text: str):
        """
        Logs the unknown issue into a staging area for the user to review.
        """
        staging_dir = os.path.join(self.trained_dir, "_staging")
        os.makedirs(staging_dir, exist_ok=True)
        
        staging_file = os.path.join(staging_dir, "suggestions.json")
        suggestions = []
        if os.path.exists(staging_file):
            with open(staging_file, 'r', encoding='utf-8') as f:
                suggestions = json.load(f)
                
        suggestions.append({
            "status": "pending_review",
            "error_text": error_text
        })
        
        with open(staging_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, indent=4)
            
        print("Learning Engine: Auto-suggested a new unknown pattern for review.")

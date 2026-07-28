import os
import json
from typing import List, Dict

class KnowledgeRetriever:
    """
    Manages the Domain Knowledge Base and retrieves meanings for known log snippets.
    """
    
    def __init__(self, trained_dir: str):
        self.kb_path = os.path.join(trained_dir, "knowledge_base.json")
        self.knowledge = self._load_kb()
        
    def _load_kb(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.kb_path):
            return []
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
            
    def _save_kb(self):
        os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=4)
            
    def add_entry(self, log_pattern: str, meaning: str):
        # Check if exists, update if so
        for entry in self.knowledge:
            if entry["log_pattern"] == log_pattern:
                entry["meaning"] = meaning
                self._save_kb()
                return
        
        self.knowledge.append({
            "log_pattern": log_pattern,
            "meaning": meaning
        })
        self._save_kb()
        
    def remove_entry(self, log_pattern: str):
        self.knowledge = [entry for entry in self.knowledge if entry["log_pattern"] != log_pattern]
        self._save_kb()
        
    def get_all(self) -> List[Dict[str, str]]:
        return self.knowledge

    def get_context_for_window(self, error_window: str) -> str:
        """
        Scans the error window for any known log patterns.
        Returns a formatted string containing the meanings of found patterns.
        """
        found_meanings = []
        error_lower = error_window.lower()
        
        for entry in self.knowledge:
            # Exact substring match (case insensitive)
            if entry["log_pattern"].lower() in error_lower:
                found_meanings.append(f"- '{entry['log_pattern']}': {entry['meaning']}")
                
        if not found_meanings:
            return ""
            
        return "### Domain Knowledge\nThe following proprietary logs were detected in the snippet:\n" + "\n".join(found_meanings) + "\n"

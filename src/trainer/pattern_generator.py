import os
import json
from typing import Dict, Any, List

class PatternGenerator:
    """
    Handles saving the LLM generated templates and raw log patterns 
    to the local 'trained/' directory structure.
    """
    
    def __init__(self, trained_dir_base: str):
        self.trained_dir_base = trained_dir_base
        
    def save_pattern(self, issue_name: str, template: Dict[str, Any], raw_logs: List[str]):
        """
        Saves the template and raw logs into the trained issue folder.
        """
        issue_dir = os.path.join(self.trained_dir_base, issue_name)
        os.makedirs(issue_dir, exist_ok=True)
        
        # 1. Save template.json
        template_path = os.path.join(issue_dir, "template.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4)
            
        # 2. Save raw_patterns.json (the raw logs that triggered this)
        raw_patterns_path = os.path.join(issue_dir, "raw_patterns.json")
        # Load existing if present, append to it
        existing_logs = []
        if os.path.exists(raw_patterns_path):
            with open(raw_patterns_path, 'r', encoding='utf-8') as f:
                try:
                    existing_logs = json.load(f)
                except json.JSONDecodeError:
                    pass
                    
        existing_logs.append({
            "samples": raw_logs
        })
        
        with open(raw_patterns_path, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, indent=4)
            
        return issue_dir

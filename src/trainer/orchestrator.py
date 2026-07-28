import os
from typing import Dict, Any

from src.trainer.llm_template_gen import LLMTemplateGenerator
from src.trainer.pattern_generator import PatternGenerator
from src.trainer.summary_generator import SummaryGenerator
from src.vectors.embedding_gen import EmbeddingGenerator
from src.vectors.vector_db import VectorDB

class TrainerOrchestrator:
    def __init__(self, trained_dir: str):
        self.trained_dir = trained_dir
        self.db_path = os.path.join(self.trained_dir, "vectors.json")
        
        self.llm_gen = LLMTemplateGenerator()
        self.pat_gen = PatternGenerator(self.trained_dir)
        self.sum_gen = SummaryGenerator()
        self.emb_gen = EmbeddingGenerator()
        self.vdb = VectorDB(self.db_path)
        
    def train_issue(self, issue_id: str, title: str, component: str, snippet: str, meaning: str) -> Dict[str, Any]:
        """
        Executes the full training pipeline.
        """
        # 1. Generate Template via LLM
        hint = f"Title: {title}\nComponent: {component}\nMeaning: {meaning}"
        template = self.llm_gen.generate_template(raw_logs=snippet, explanation_hint=hint)
        
        if title:
            template["issue_name"] = title
            
        # 2. Save Pattern
        issue_dir = self.pat_gen.save_pattern(issue_id, template, [snippet])
        
        # 3. Generate Summary
        summary_path = self.sum_gen.generate_summary(issue_dir, template)
        
        # 4. Generate Embedding
        # Embed the raw snippet so that incoming similar raw errors match strongly
        text_to_embed = f"{title}\n{snippet}\n{meaning}"
        vector = self.emb_gen.generate_embedding(text_to_embed)
        
        # 5. Save to VectorDB
        metadata = {
            "title": template.get("issue_name", title),
            "component": component
        }
        self.vdb.add_vector(issue_id, vector, metadata)
        
        return {
            "status": "success",
            "issue_id": issue_id,
            "template": template,
            "summary_path": summary_path
        }

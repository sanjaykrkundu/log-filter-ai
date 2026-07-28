import os
import json
from src.parser.camera_extractor import CameraExtractor
from src.parser.error_extractor import ErrorExtractor
from src.vectors.embedding_gen import EmbeddingGenerator
from src.vectors.vector_db import VectorDB
from src.analyzer.root_cause import RootCauseAnalyzer
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RuntimeAnalyzer:
    """
    Orchestrates the entire runtime analysis pipeline for a new dumpstate.
    """
    
    def __init__(self, trained_dir: str, workspace_dir: str):
        self.trained_dir = trained_dir
        self.workspace_dir = workspace_dir
        self.db_path = os.path.join(self.trained_dir, "vectors.json")
        
    def _load_template(self, issue_id: str):
        template_path = os.path.join(self.trained_dir, issue_id, "template.json")
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def analyze_dumpstate(self, dumpstate_path: str) -> dict:
        """
        Executes the analysis pipeline and returns a structured result.
        """
        logger.debug(f"Starting analysis for dumpstate: {dumpstate_path}")
        # 1. Extract Camera Logs
        base_name = os.path.basename(dumpstate_path)
        logcat_path = os.path.join(self.workspace_dir, "extracted_logs", f"{base_name}_camera_logcat.txt")
        
        extractor = CameraExtractor(dumpstate_path)
        extractor.extract_camera_logs(logcat_path)
        
        # 2. Extract Error Windows
        error_extractor = ErrorExtractor(logcat_path)
        errors = error_extractor.extract_errors(context_lines=5)
        
        logger.debug(f"Extracted {len(errors)} error windows from {logcat_path}")
        
        if not errors:
            logger.info(f"No obvious camera errors found in {dumpstate_path}")
            return {"status": "success", "message": "No obvious camera errors found.", "findings": []}
            
        # 3. Vector Similarity & Context Building
        vdb = VectorDB(self.db_path)
        emb_gen = EmbeddingGenerator()
        rc_analyzer = RootCauseAnalyzer(self.trained_dir)
        
        findings = []
        for error in errors:
            error_text = error["context"]
            error_vec = emb_gen.generate_embedding(error_text)
            
            # Find top matches using FAISS
            matches = vdb.search(error_vec, top_k=2)
            
            # Load actual JSON templates for the LLM
            matching_templates = []
            for record, score in matches:
                logger.debug(f"FAISS match: {record['issue_id']} (score: {score:.4f})")
                # We only pass templates with a decent similarity score to save tokens
                if score > 0.1: 
                    template = self._load_template(record["issue_id"])
                    if template:
                        matching_templates.append(template)
                        
            # 4. LLM Classification (Agentic RAG)
            analysis = rc_analyzer.analyze(
                error_window=error_text, 
                matching_templates=matching_templates, 
                logcat_path=logcat_path
            )
            
            findings.append({
                "line_number": error["line_number"],
                "error_line": error["error_line"],
                "analysis": analysis
            })
            
        return {
            "status": "success",
            "findings": findings
        }

import sys
import os
import argparse
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.trainer.llm_template_gen import LLMTemplateGenerator
from src.trainer.pattern_generator import PatternGenerator
from src.trainer.summary_generator import SummaryGenerator
from src.vectors.embedding_gen import EmbeddingGenerator
from src.vectors.vector_db import VectorDB

def main():
    parser = argparse.ArgumentParser(description="Train the AI on a new camera issue pattern.")
    parser.add_argument("training_dir", help="Path to the specific issue training directory (e.g. training/Camera_Open_Failure)")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.training_dir):
        print(f"Error: Training directory '{args.training_dir}' not found.")
        sys.exit(1)
        
    issue_name = os.path.basename(os.path.normpath(args.training_dir))
    trained_base = os.path.abspath(os.path.join(args.training_dir, '../../trained'))
    
    # Paths
    logs_dir = os.path.join(args.training_dir, "logs")
    hint_file = os.path.join(args.training_dir, "hint.md")
    
    # 1. Read hint if exists
    hint = ""
    if os.path.exists(hint_file):
        with open(hint_file, 'r', encoding='utf-8') as f:
            hint = f.read()
            
    # 2. Read first log file as a sample (in reality, loop through all)
    if not os.path.exists(logs_dir):
        print(f"Error: logs directory missing in {args.training_dir}")
        sys.exit(1)
        
    log_files = os.listdir(logs_dir)
    if not log_files:
        print(f"Error: No logs found in {logs_dir}")
        sys.exit(1)
        
    sample_log = os.path.join(logs_dir, log_files[0])
    with open(sample_log, 'r', encoding='utf-8') as f:
        raw_logs = f.readlines()
        
    error_window_str = "".join(raw_logs)
    
    print(f"Training on issue: {issue_name}...")
    
    # 3. Generate Template via LLM
    print("Generating template via LLM...")
    llm_gen = LLMTemplateGenerator(trained_base)
    template = llm_gen.generate_template(error_window=error_window_str, hint=hint)
    
    # For now, we force the folder name to keep it organized
    template["issue_name"] = issue_name
    
    # 4. Save Pattern
    print("Saving patterns locally...")
    pat_gen = PatternGenerator(trained_dir_base=trained_base)
    issue_dir = pat_gen.save_pattern(issue_name, template, raw_logs)
    
    # 4.5 Generate and Save Vector
    print("Generating vector embedding...")
    emb_gen = EmbeddingGenerator()
    vector = emb_gen.generate_embedding(error_window_str)
    
    db_path = os.path.join(trained_base, "vectors.json")
    vdb = VectorDB(db_path)
    vdb.add_vector(issue_name, vector, metadata={"issue_name": issue_name})
    
    # 5. Generate Summary
    print("Generating human-readable summary...")
    sum_gen = SummaryGenerator()
    summary_path = sum_gen.generate_summary(issue_dir, template)
    
    print(f"Successfully trained issue '{issue_name}'.")
    print(f"Results saved to: {issue_dir}")

if __name__ == "__main__":
    main()

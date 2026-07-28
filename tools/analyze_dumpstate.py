import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzer.runtime_analyzer import RuntimeAnalyzer
from src.report.report_gen import ReportGenerator
from src.analyzer.learning_engine import LearningEngine

def main():
    parser = argparse.ArgumentParser(description="Analyze a new dumpstate for camera issues.")
    parser.add_argument("dumpstate", help="Path to the new dumpstate file to analyze")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dumpstate):
        print(f"Error: File '{args.dumpstate}' not found.")
        sys.exit(1)
        
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    trained_dir = os.path.join(project_root, "trained")
    workspace_dir = os.path.join(project_root, "workspace")
    output_dir = os.path.join(project_root, "output")
    
    print(f"Starting analysis on {args.dumpstate}...")
    
    analyzer = RuntimeAnalyzer(trained_dir, workspace_dir)
    results = analyzer.analyze_dumpstate(args.dumpstate)
    
    print("Generating reports...")
    base_name = os.path.splitext(os.path.basename(args.dumpstate))[0]
    
    report_gen = ReportGenerator(output_dir)
    json_path = report_gen.generate_json_report(base_name, results)
    html_path = report_gen.generate_html_report(base_name, results)
    
    print(f"Done! Reports saved to:")
    print(f"  - {json_path}")
    print(f"  - {html_path}")
    
    print("\nTriggering continuous learning engine...")
    learner = LearningEngine(trained_dir)
    learner.process_findings(results.get("findings", []), args.dumpstate)
    print("Done!")

if __name__ == "__main__":
    main()

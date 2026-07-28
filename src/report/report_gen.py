import json
import os
from typing import Dict, Any

class ReportGenerator:
    """
    Generates human-readable HTML and machine-readable JSON reports 
    from the runtime analyzer's findings.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_json_report(self, base_name: str, analysis_results: Dict[str, Any]) -> str:
        out_path = os.path.join(self.output_dir, f"{base_name}_report.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=4)
        return out_path
        
    def generate_html_report(self, base_name: str, analysis_results: Dict[str, Any]) -> str:
        out_path = os.path.join(self.output_dir, f"{base_name}_report.html")
        
        findings_html = ""
        for f in analysis_results.get("findings", []):
            analysis = f.get("analysis", {})
            findings_html += f"""
            <div class="finding">
                <h2>Line {f.get('line_number')}: {analysis.get('issue_name', 'Unknown')}</h2>
                <p><strong>Classification:</strong> {analysis.get('classification', 'N/A')} (Confidence: {analysis.get('confidence_score', 0):.2f})</p>
                <p><strong>Root Cause:</strong> {analysis.get('root_cause', 'N/A')}</p>
                <p><strong>Suggested Fix:</strong> {analysis.get('suggested_fix', 'N/A')}</p>
                <pre class="error-line">{f.get('error_line', '')}</pre>
            </div>
            """
            
        html = f"""
        <html>
        <head>
            <title>Camera Analyzer Report: {base_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f9f9f9; }}
                h1 {{ color: #333; }}
                .finding {{ background: white; padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .error-line {{ background: #fee; color: #c00; padding: 0.5rem; border-radius: 4px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Analysis Report for {base_name}</h1>
            {findings_html if findings_html else "<p>No camera errors detected.</p>"}
        </body>
        </html>
        """
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return out_path

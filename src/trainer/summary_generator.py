import os
from typing import Dict, Any

class SummaryGenerator:
    """
    Generates a human-readable markdown summary of a trained issue.
    """
    
    def generate_summary(self, issue_dir: str, template: Dict[str, Any]) -> str:
        """
        Creates a summary.md file in the issue_dir based on the template.
        """
        summary_path = os.path.join(issue_dir, "summary.md")
        
        issue_name = template.get("issue_name", "Unknown Issue")
        root_cause = template.get("root_cause_summary", "No description provided.")
        indicators = template.get("key_indicators", [])
        suggested_fix = template.get("suggested_fix", "No fix suggested.")
        
        md_content = f"# Issue: {issue_name}\n\n"
        md_content += f"## Root Cause\n{root_cause}\n\n"
        
        md_content += "## Key Indicators\n"
        for ind in indicators:
            md_content += f"- `{ind}`\n"
        md_content += "\n"
        
        md_content += f"## Suggested Fix\n{suggested_fix}\n"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        return summary_path

import os
import json
import google.generativeai as genai
from typing import Dict, Any, List

class RootCauseAnalyzer:
    """
    Uses the Google Gemini API to classify an error based on similar historical templates,
    and returns a confidence score.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        
    def _build_context(self, error_window: str, matching_templates: List[Dict[str, Any]]) -> str:
        context = "### Known Issue Templates\n"
        for i, t in enumerate(matching_templates):
            context += f"Template {i+1}:\n"
            context += json.dumps(t, indent=2) + "\n\n"
            
        context += f"### New Error Window to Analyze\n{error_window}\n"
        return context

    def analyze(self, error_window: str, matching_templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calls the Gemini API to classify the issue and provide a root cause and confidence.
        """
        context = self._build_context(error_window, matching_templates)
        
        prompt = f"""
You are an expert Android system debugger.
Analyze the following context, which includes known issue templates and a new error window.
Classify the new error. If it matches a template closely, classify it as 'KNOWN'. Otherwise, 'UNKNOWN'.

{context}

Respond ONLY with a JSON object in this format:
{{
    "classification": "KNOWN" or "UNKNOWN",
    "issue_name": "Name of the issue (use the template name if known, else invent one)",
    "root_cause": "A short description of what failed",
    "confidence_score": 0.95,
    "suggested_fix": "Potential mitigation"
}}
Do not include any markdown code blocks around the JSON output.
"""
        response = self.model.generate_content(prompt)
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())

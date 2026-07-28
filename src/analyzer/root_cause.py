import os
import json
import google.generativeai as genai
from typing import Dict, Any, List

class RootCauseAnalyzer:
    """
    Uses the Google Gemini API to classify an error based on similar historical templates,
    and returns a confidence score. Uses Agentic RAG via Function Calling to retrieve more context.
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
            
        context += f"### Initial Error Window\n{error_window}\n"
        return context

    def analyze(self, error_window: str, matching_templates: List[Dict[str, Any]], logcat_path: str = None) -> Dict[str, Any]:
        """
        Calls the Gemini API to classify the issue, optionally using RAG to fetch more logs.
        """
        context = self._build_context(error_window, matching_templates)
        
        def fetch_log_context(target_line_number: int, lines_before: int = 20, lines_after: int = 20) -> str:
            """
            Fetches extra lines of context from the logcat file around a specific line number.
            Useful for finding the root cause if the initial error window doesn't have enough information.
            """
            if not logcat_path or not os.path.exists(logcat_path):
                return "Error: Logcat file not available for fetching."
                
            try:
                with open(logcat_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                start_idx = max(0, target_line_number - lines_before - 1)
                end_idx = min(len(lines), target_line_number + lines_after)
                
                return "".join(lines[start_idx:end_idx])
            except Exception as e:
                return f"Error reading logcat: {str(e)}"
                
        prompt = f"""
You are an expert Android system debugger.
Analyze the following context, which includes known issue templates and an initial error window.
If you need more context (e.g., to see what happened 50 lines before the error), use the `fetch_log_context` tool!
Classify the new error. If it matches a template closely, classify it as 'KNOWN'. Otherwise, 'UNKNOWN'.

{context}

Respond ONLY with a JSON object in this format (even if you used tools, the final output must be this JSON):
{{
    "classification": "KNOWN" or "UNKNOWN",
    "issue_name": "Name of the issue (use the template name if known, else invent one)",
    "root_cause": "A short description of what failed",
    "confidence_score": 0.95,
    "suggested_fix": "Potential mitigation"
}}
Do not include any markdown code blocks around the JSON output.
"""
        chat = self.model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt, tools=[fetch_log_context])
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        try:
            return json.loads(text.strip())
        except Exception:
            return {
                "classification": "UNKNOWN",
                "issue_name": "Parsing_Error",
                "root_cause": "The LLM returned invalid JSON. Raw output: " + text[:100],
                "confidence_score": 0.0,
                "suggested_fix": "N/A"
            }

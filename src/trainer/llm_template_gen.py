import os
import json
import google.generativeai as genai
from typing import Dict, Any

class LLMTemplateGenerator:
    """
    Generates structured JSON templates describing a specific camera issue.
    This class handles the prompt generation and interfaces with the Google Gemini API.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def _build_prompt(self, error_window: str, hint: str) -> str:
        """
        Constructs the prompt for the LLM to generate the pattern template.
        """
        prompt = f"""
You are an expert Android Camera system debugger.
Analyze the following error window from an Android logcat and create a structured JSON template representing this issue.

### Error Window:
```
{error_window}
```

### Manual Hint / Context:
{hint if hint else "No manual hint provided. Infer the issue strictly from the logs."}

### Instructions:
Generate a JSON object with the following schema:
{{
    "issue_name": "Short descriptive name (e.g., Camera_Open_Failure)",
    "root_cause_summary": "A 1-2 sentence description of what failed",
    "key_indicators": ["List of critical log lines or tags that identify this issue"],
    "suggested_fix": "Potential mitigation or fix if known, else 'Unknown'"
}}
Return ONLY valid JSON. Do not include markdown formatting around the output.
"""
        return prompt

    def generate_template(self, error_window: str, hint: str = "") -> Dict[str, Any]:
        """
        Calls the Gemini API and returns the parsed JSON template.
        """
        prompt = self._build_prompt(error_window, hint)
        response = self.model.generate_content(prompt)
        
        text = response.text.strip()
        # Clean markdown code block if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())

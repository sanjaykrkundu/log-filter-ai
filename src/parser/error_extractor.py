import os
import re
from typing import Iterator

class ErrorExtractor:
    """
    Scans through an extracted camera logcat file and identifies potential errors.
    """
    
    ERROR_KEYWORDS = [
        "Exception",
        "Error",
        "FATAL EXCEPTION",
        "died",
        "E/Camera",
        "F/Camera",
        "timeout",
        "failed",
        "disconnect"
    ]
    
    def __init__(self, logcat_path: str):
        if not os.path.exists(logcat_path):
            raise FileNotFoundError(f"Logcat file not found: {logcat_path}")
        self.logcat_path = logcat_path

    def extract_errors(self, context_lines: int = 10) -> list[dict]:
        """
        Returns a list of dictionaries containing the error and surrounding context.
        This provides a narrow window of logs where the issue likely occurred.
        """
        # Read all lines for context windowing (since extracted logs are much smaller)
        with open(self.logcat_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        error_windows = []
        for i, line in enumerate(lines):
            if any(kw.lower() in line.lower() for kw in self.ERROR_KEYWORDS):
                # Extract context window
                start_idx = max(0, i - context_lines)
                end_idx = min(len(lines), i + context_lines + 1)
                window = lines[start_idx:end_idx]
                
                error_windows.append({
                    "line_number": i + 1,
                    "error_line": line.strip(),
                    "context": "".join(window).strip()
                })
                
        # 2. Check for behavioral anomalies (e.g., unclosed sessions)
        try:
            from src.parser.timeline_builder import TimelineBuilder
            tb = TimelineBuilder(self.logcat_path)
            sessions = tb.build_sessions()
            for session in sessions:
                if session["end_event"] is None:
                    start_line = session["start_event"]["line_number"]
                    error_msg = f"Behavioral Anomaly: Session started at line {start_line} but never closed."
                    
                    events = session["events"]
                    context_events = events[-20:] # Last 20 lines of the stuck session
                    context_str = "\n".join([e["raw_line"] for e in context_events])
                    
                    error_windows.append({
                        "line_number": events[-1]["line_number"],
                        "error_line": error_msg,
                        "context": context_str
                    })
        except Exception:
            pass # Fallback if timeline parsing fails
            
        return error_windows

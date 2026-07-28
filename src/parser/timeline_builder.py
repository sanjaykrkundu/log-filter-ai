import re
import os

class TimelineBuilder:
    """
    Parses Android logcat files to construct a chronological timeline of events.
    """
    
    # Regex to match typical Android logcat timestamp: e.g., '01-23 14:55:01.123'
    # Format: MM-DD HH:MM:SS.mmm
    TIMESTAMP_REGEX = re.compile(r"^(\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)\s+(\d+)\s+([VDIWEF])\s+(.*?):(.*)")
    
    def __init__(self, logcat_path: str):
        if not os.path.exists(logcat_path):
            raise FileNotFoundError(f"Logcat file not found: {logcat_path}")
        self.logcat_path = logcat_path

    def build_timeline(self) -> list[dict]:
        """
        Parses the logcat file and returns a structured list of events.
        """
        timeline = []
        with open(self.logcat_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                match = self.TIMESTAMP_REGEX.match(line.strip())
                if match:
                    timestamp, pid, tid, level, tag, message = match.groups()
                    timeline.append({
                        "line_number": i + 1,
                        "timestamp": timestamp,
                        "pid": pid,
                        "tid": tid,
                        "level": level,
                        "tag": tag.strip(),
                        "message": message.strip(),
                        "raw_line": line.strip()
                    })
        return timeline

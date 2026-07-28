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

    def build_sessions(self) -> list[dict]:
        """
        Groups the timeline into logical sessions based on start and end markers.
        """
        timeline = self.build_timeline()
        sessions = []
        current_session = None
        
        # Simple heuristic for camera sessions
        start_markers = ["opening camera", "starting", "connect"]
        end_markers = ["closing camera", "disconnect", "release"]
        
        for event in timeline:
            msg = event["message"].lower()
            
            if any(m in msg for m in start_markers):
                if current_session is None:
                    current_session = {
                        "start_event": event,
                        "end_event": None,
                        "events": [event]
                    }
                else:
                    current_session["events"].append(event)
            elif any(m in msg for m in end_markers):
                if current_session is not None:
                    current_session["events"].append(event)
                    current_session["end_event"] = event
                    sessions.append(current_session)
                    current_session = None
            else:
                if current_session is not None:
                    current_session["events"].append(event)
                    
        # If a session never closed, it might be a silent crash or stuck state
        if current_session is not None:
            sessions.append(current_session)
            
        return sessions

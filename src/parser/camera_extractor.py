import os
import re
from typing import Iterator
from src.parser.log_parser import LogParser

class CameraExtractor(LogParser):
    """
    Extracts camera-specific logs from a general dumpstate file.
    Filters logs based on common camera tags and components.
    """
    
    CAMERA_KEYWORDS = [
        "CameraService",
        "CameraProvider",
        "CameraDevice",
        "CamX",
        "ChiUseCases",
        "CameraHal",
        "Camera3",
        "media.camera",
        "Camera",
        "cameraserver"
    ]
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        
    def extract_camera_logs(self, output_path: str) -> None:
        """
        Reads the dumpstate and writes lines containing camera keywords to the output file.
        This significantly reduces the file size for further processing.
        """
        # Regular expression for matching timestamp format in android logs (e.g., 01-23 14:55:01.123)
        # We try to keep only lines with timestamps if possible to avoid noise, but dumpstate has blocks.
        
        # We will use extract_between_markers to optionally extract specific dumpsys blocks,
        # but for now, we just filter line-by-line based on tags for logcat sections.
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as out_f:
            for line in self.filter_by_keyword(self.CAMERA_KEYWORDS):
                out_f.write(line)

    def extract_camera_dumpsys(self, output_path: str) -> None:
        """
        Extracts the 'DUMP OF SERVICE media.camera' block.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            for line in self.extract_between_markers("DUMP OF SERVICE media.camera", "---------"):
                out_f.write(line)

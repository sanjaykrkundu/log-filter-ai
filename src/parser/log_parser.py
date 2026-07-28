import os
from typing import Iterator

class LogParser:
    """
    Base parser to handle large dumpstate or logcat files efficiently.
    It reads files line-by-line to avoid loading massive files into memory.
    """
    
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Log file not found: {file_path}")
        self.file_path = file_path

    def read_lines(self) -> Iterator[str]:
        """
        Yields lines from the log file one by one.
        Handles potentially different encodings (utf-8, latin-1 fallback).
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line
        except UnicodeDecodeError:
            # Fallback for logs that might have weird characters
            with open(self.file_path, 'r', encoding='latin-1') as f:
                for line in f:
                    yield line

    def filter_by_keyword(self, keywords: list[str]) -> Iterator[str]:
        """
        Yields lines that contain any of the specified keywords.
        """
        for line in self.read_lines():
            if any(kw in line for kw in keywords):
                yield line
                
    def extract_between_markers(self, start_marker: str, end_marker: str) -> Iterator[str]:
        """
        Yields lines that are between a start marker and an end marker.
        Useful for extracting specific blocks from dumpstate (e.g. 'DUMP OF SERVICE media.camera').
        """
        in_block = False
        for line in self.read_lines():
            if not in_block:
                if start_marker in line:
                    in_block = True
                    yield line
            else:
                yield line
                if end_marker in line:
                    break

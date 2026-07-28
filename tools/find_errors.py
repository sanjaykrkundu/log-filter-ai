import sys
import os
import json
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser.error_extractor import ErrorExtractor
from src.parser.timeline_builder import TimelineBuilder

def main():
    parser = argparse.ArgumentParser(description="Find errors and build timeline from a camera logcat file.")
    parser.add_argument("logcat_file", help="Path to the extracted camera logcat file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.logcat_file):
        print(f"Error: Logcat file '{args.logcat_file}' not found.")
        sys.exit(1)
        
    print(f"Analyzing {args.logcat_file}...")
    
    # 1. Build Timeline
    tb = TimelineBuilder(args.logcat_file)
    timeline = tb.build_timeline()
    print(f"Built timeline with {len(timeline)} parsable events.")
    
    # 2. Extract Errors
    extractor = ErrorExtractor(args.logcat_file)
    errors = extractor.extract_errors(context_lines=5)
    
    print(f"Found {len(errors)} potential error windows.")
    
    # Save output for review
    base_name = os.path.basename(args.logcat_file)
    name, _ = os.path.splitext(base_name)
    output_json = os.path.join(os.path.dirname(args.logcat_file), f"{name}_analysis.json")
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            "total_events_parsed": len(timeline),
            "errors": errors
        }, f, indent=4)
        
    print(f"Analysis saved to: {output_json}")

if __name__ == "__main__":
    main()

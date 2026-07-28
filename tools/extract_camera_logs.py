import sys
import os
import argparse

# Add the project root to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parser.camera_extractor import CameraExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract camera-related logs from a dumpstate file.")
    parser.add_argument("input_file", help="Path to the dumpstate file")
    parser.add_argument("output_dir", help="Directory to save the extracted logs")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    base_name = os.path.basename(args.input_file)
    name, ext = os.path.splitext(base_name)
    
    logcat_out = os.path.join(args.output_dir, f"{name}_camera_logcat{ext}")
    dumpsys_out = os.path.join(args.output_dir, f"{name}_camera_dumpsys{ext}")
    
    print(f"Extracting camera logs from {args.input_file}...")
    extractor = CameraExtractor(args.input_file)
    
    print("Extracting logcat lines...")
    extractor.extract_camera_logs(logcat_out)
    
    print("Extracting dumpsys block...")
    extractor.extract_camera_dumpsys(dumpsys_out)
    
    print(f"Done! Logcat saved to: {logcat_out}")
    print(f"Done! Dumpsys saved to: {dumpsys_out}")

if __name__ == "__main__":
    main()

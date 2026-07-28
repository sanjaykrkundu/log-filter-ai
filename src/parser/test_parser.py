import unittest
import os
import tempfile
from src.parser.camera_extractor import CameraExtractor
from src.parser.timeline_builder import TimelineBuilder
from src.parser.error_extractor import ErrorExtractor

class TestParserLogic(unittest.TestCase):
    def setUp(self):
        # Create a temporary mock logcat file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_dumpstate = os.path.join(self.temp_dir.name, "mock_dumpstate.txt")
        self.mock_logcat = os.path.join(self.temp_dir.name, "mock_camera_logcat.txt")
        
        with open(self.mock_dumpstate, 'w', encoding='utf-8') as f:
            f.write("01-23 14:55:01.123  1000  2000 I SystemServer: starting\n")
            f.write("01-23 14:55:01.200  1050  2050 D CameraService: starting camera server\n")
            f.write("01-23 14:55:01.250  1050  2050 I CamX: opening camera 0\n")
            f.write("01-23 14:55:01.300  1050  2050 E Camera: FATAL EXCEPTION in camera hal\n")
            f.write("01-23 14:55:01.350  1050  2050 I CamX: closing camera 0\n")
            f.write("DUMP OF SERVICE media.camera\n")
            f.write("Camera 0 properties:\n")
            f.write("---------\n")
            f.write("01-23 14:55:01.400  1000  2000 I ActivityManager: display changed\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_camera_extractor(self):
        extractor = CameraExtractor(self.mock_dumpstate)
        extractor.extract_camera_logs(self.mock_logcat)
        
        with open(self.mock_logcat, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        self.assertEqual(len(lines), 6) # 6 lines contain camera keywords
        self.assertIn("CameraService", lines[0])
        
    def test_timeline_builder(self):
        extractor = CameraExtractor(self.mock_dumpstate)
        extractor.extract_camera_logs(self.mock_logcat)
        
        tb = TimelineBuilder(self.mock_logcat)
        timeline = tb.build_timeline()
        
        self.assertEqual(len(timeline), 4)
        self.assertEqual(timeline[0]["timestamp"], "01-23 14:55:01.200")
        self.assertEqual(timeline[3]["level"], "I")
        self.assertEqual(timeline[3]["tag"], "CamX")

    def test_error_extractor(self):
        extractor = CameraExtractor(self.mock_dumpstate)
        extractor.extract_camera_logs(self.mock_logcat)
        
        error_ext = ErrorExtractor(self.mock_logcat)
        errors = error_ext.extract_errors(context_lines=1)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("FATAL EXCEPTION", errors[0]["error_line"])
        self.assertIn("opening camera", errors[0]["context"]) # Context before
        self.assertIn("closing camera", errors[0]["context"]) # Context after

if __name__ == '__main__':
    unittest.main()

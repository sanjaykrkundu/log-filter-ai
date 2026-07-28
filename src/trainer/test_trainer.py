import unittest
import os
import tempfile
import json
from src.trainer.llm_template_gen import LLMTemplateGenerator
from src.trainer.pattern_generator import PatternGenerator
from src.trainer.summary_generator import SummaryGenerator

class TestTrainerPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.trained_dir = os.path.join(self.temp_dir.name, "trained")
        os.makedirs(self.trained_dir, exist_ok=True)
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_llm_template_gen(self):
        llm = LLMTemplateGenerator()
        res = llm.generate_template("some error log", "hint")
        self.assertIn("issue_name", res)
        self.assertEqual(res["issue_name"], "Mock_Camera_Failure")
        
    def test_pattern_generator(self):
        pat_gen = PatternGenerator(self.trained_dir)
        template = {"issue_name": "Test_Issue", "root_cause_summary": "Failed"}
        raw_logs = ["FATAL EXCEPTION", "died"]
        
        issue_dir = pat_gen.save_pattern("Test_Issue", template, raw_logs)
        
        self.assertTrue(os.path.exists(os.path.join(issue_dir, "template.json")))
        self.assertTrue(os.path.exists(os.path.join(issue_dir, "raw_patterns.json")))
        
        with open(os.path.join(issue_dir, "raw_patterns.json"), 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["samples"][0], "FATAL EXCEPTION")

    def test_summary_generator(self):
        issue_dir = os.path.join(self.trained_dir, "Test_Issue")
        os.makedirs(issue_dir, exist_ok=True)
        
        template = {
            "issue_name": "Test_Issue", 
            "root_cause_summary": "Failed",
            "key_indicators": ["FATAL"]
        }
        
        sum_gen = SummaryGenerator()
        summary_path = sum_gen.generate_summary(issue_dir, template)
        
        self.assertTrue(os.path.exists(summary_path))
        with open(summary_path, 'r') as f:
            content = f.read()
            self.assertIn("# Issue: Test_Issue", content)
            self.assertIn("`FATAL`", content)

if __name__ == '__main__':
    unittest.main()

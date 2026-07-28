import unittest
import os
import tempfile
from src.vectors.embedding_gen import EmbeddingGenerator
from src.vectors.vector_db import VectorDB
from src.vectors.similarity import SimilarityEngine

class TestVectorLogic(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "vectors.json")
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_embedding_generator(self):
        gen = EmbeddingGenerator()
        vec1 = gen.generate_embedding("FATAL EXCEPTION in camera hal")
        vec2 = gen.generate_embedding("FATAL EXCEPTION in camera hal")
        vec3 = gen.generate_embedding("Some other completely different error")
        
        self.assertEqual(len(vec1), 128)
        self.assertEqual(vec1, vec2) # Deterministic
        self.assertNotEqual(vec1, vec3) # Different hashes
        
    def test_vector_db_and_similarity(self):
        db = VectorDB(self.db_path)
        gen = EmbeddingGenerator()
        
        vec_cam = gen.generate_embedding("camera open failed timeout")
        vec_mem = gen.generate_embedding("out of memory error")
        
        db.add_vector("Camera_Timeout", vec_cam)
        db.add_vector("OOM_Error", vec_mem)
        
        # Reload DB to test persistence
        db2 = VectorDB(self.db_path)
        records = db2.get_all_vectors()
        self.assertEqual(len(records), 2)
        
        # Test similarity
        query_vec = gen.generate_embedding("camera open failed timeout") # Exact match
        results = SimilarityEngine.search(query_vec, records)
        
        self.assertEqual(results[0][0]["issue_id"], "Camera_Timeout")
        self.assertAlmostEqual(results[0][1], 1.0, places=4)
        
        # Test distinct similarity
        sim = SimilarityEngine.cosine_similarity(vec_cam, vec_mem)
        self.assertTrue(sim < 0.9) # Should not be perfectly similar

if __name__ == '__main__':
    unittest.main()

import os
import google.generativeai as genai
from typing import List

class EmbeddingGenerator:
    """
    Generates vector embeddings for a given text using the Google Gemini API.
    """
    
    def __init__(self, api_key: str = None, model: str = "models/embedding-001"):
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to your Gemini API key.")
            
        genai.configure(api_key=api_key)
        self.model = model
        
    def generate_embedding(self, text: str) -> List[float]:
        """
        Calls the Gemini API to get the embedding for the provided text.
        """
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

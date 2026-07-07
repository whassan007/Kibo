import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class ControlRecommender:
    def __init__(self, embeddings_model, cached_embeddings_path: str = None):
        """
        Takes an instance of a SentenceTransformer (or similar) embeddings model.
        """
        self.embeddings = embeddings_model
        self.historical_controls = []
        self.control_embeddings = []
        
        if cached_embeddings_path and os.path.exists(cached_embeddings_path):
            self.load_cache(cached_embeddings_path)
    
    def cache_historical_controls(self, controls_data: list):
        """
        Pre-computes embeddings for historical controls to save inference time.
        controls_data should be a list of dicts with 'id' and 'description'.
        """
        self.historical_controls = controls_data
        texts = [c.get('description', '') for c in controls_data]
        self.control_embeddings = self.embeddings.encode(texts)
        
    def save_cache(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump({
                'controls': self.historical_controls,
                'embeddings': self.control_embeddings
            }, f)
            
    def load_cache(self, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.historical_controls = data['controls']
            self.control_embeddings = data['embeddings']

    def recommend(self, assessment_findings: str, top_k: int = 10) -> list:
        if not self.historical_controls or len(self.control_embeddings) == 0:
            return []

        # Embed the new assessment findings
        findings_embedding = self.embeddings.encode([assessment_findings])
        
        # Calculate cosine similarity against all cached controls
        similarities = cosine_similarity(findings_embedding, self.control_embeddings)[0]
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for i in top_indices:
            results.append({
                'control': self.historical_controls[i],
                'similarity': float(similarities[i])
            })
            
        return results

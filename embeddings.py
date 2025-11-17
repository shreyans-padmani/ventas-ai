import requests
import numpy as np
from config import GOOGLE_API_KEY

class ExampleRetriever:
    """
    Simple in-memory retriever using Google Gemini Embedding API.
    Examples must be a list of dicts: {'user': <user text>, 'sql': <sql text>}.
    
    """
    def __init__(self, examples=None, embedding_model="text-embedding-004"):
        self.embedding_model = embedding_model
        self.api_key = GOOGLE_API_KEY
        self.examples = examples or []
        self.embeddings = None
        if self.examples:
            self.build_index(self.examples)

    def _get_embedding(self, text):
        """Get embedding for a single text using Google Gemini Embedding API."""
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.embedding_model}:embedContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "content": {
                "parts": [{"text": text}]
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print("❌ Gemini Embedding Error:", response.text)
            raise Exception(f"Gemini Embedding API Error: {response.status_code}")
        
        result = response.json()
        # Handle both response formats: {"embedding": {"values": [...]}} or {"embedding": [...]}
        if "embedding" in result:
            embedding_data = result["embedding"]
            if "values" in embedding_data:
                return np.array(embedding_data["values"])
            else:
                return np.array(embedding_data)
        else:
            raise Exception("Unexpected response format from Gemini Embedding API")

    def _get_embeddings_batch(self, texts):
        """Get embeddings for multiple texts using Gemini Embedding API."""
        embeddings = []
        for text in texts:
            emb = self._get_embedding(text)
            embeddings.append(emb)
        return np.array(embeddings)

    def build_index(self, examples):
        self.examples = examples
        texts = [e["user"] for e in examples]
        # normalized embeddings for cosine similarity via dot product
        embs = self._get_embeddings_batch(texts)
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        self.embeddings = embs / (norms + 1e-12)

    def get_top_k(self, query, k=3):
        if self.embeddings is None or len(self.examples) == 0:
            return []
        q_emb = self._get_embedding(query)
        q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-12)
        sims = self.embeddings @ q_emb
        idx = np.argsort(sims)[::-1][:k]
        return [self.examples[i] for i in idx]
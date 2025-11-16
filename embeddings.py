from sentence_transformers import SentenceTransformer
import numpy as np

class ExampleRetriever:
    """
    Simple in-memory retriever using a small embedding model (all-MiniLM-L6-v2).
    Examples must be a list of dicts: {'user': <user text>, 'sql': <sql text>}.
    
    """
    def __init__(self, examples=None, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.examples = examples or []
        self.embeddings = None
        if self.examples:
            self.build_index(self.examples)

    def build_index(self, examples):
        self.examples = examples
        texts = [e["user"] for e in examples]
        # normalized embeddings for cosine similarity via dot product
        embs = self.model.encode(texts, convert_to_numpy=True)
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        self.embeddings = embs / (norms + 1e-12)

    def get_top_k(self, query, k=3):
        if self.embeddings is None or len(self.examples) == 0:
            return []
        q_emb = self.model.encode([query], convert_to_numpy=True)[0]
        q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-12)
        sims = self.embeddings @ q_emb
        idx = np.argsort(sims)[::-1][:k]
        return [self.examples[i] for i in idx]
import faiss
import numpy as np
from pathlib import Path

class FaissIndexer:
    def __init__(self, dim: int, index_path: str = None):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.index_path = Path(index_path) if index_path else None

    def add(self, vectors: np.ndarray):
        self.index.add(vectors)

    def search(self, query: np.ndarray, k: int = 5):
        D, I = self.index.search(query, k)
        return D, I

    def save(self, path: str):
        faiss.write_index(self.index, path)

    def load(self, path: str):
        self.index = faiss.read_index(path)

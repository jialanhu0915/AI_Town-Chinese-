import numpy as np
from pathlib import Path
import faiss
from ai_town.config import DATA_DIR


def build_faiss_index(vectors: np.ndarray, index_name: str):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    path = DATA_DIR / f"{index_name}.index"
    faiss.write_index(index, str(path))
    return str(path)


def load_faiss_index(index_path: str):
    path = Path(index_path)
    if not path.exists():
        raise FileNotFoundError(index_path)
    return faiss.read_index(str(path))


def search_index(index, query_vector: np.ndarray, k: int = 5):
    D, I = index.search(query_vector, k)
    return D, I

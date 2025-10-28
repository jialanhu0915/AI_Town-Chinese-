import numpy as np

from ai_town.retrieval.faiss_utils import build_faiss_index, load_faiss_index, search_index


def test_faiss_build_and_search(tmp_path):
    # 创建假向量
    dims = 8
    vectors = np.random.rand(10, dims).astype("float32")
    idx_path = build_faiss_index(vectors, index_name="test_idx")
    idx = load_faiss_index(idx_path)
    q = vectors[0:1]
    D, I = search_index(idx, q, k=3)
    assert I.shape[0] == 1
    assert I.shape[1] == 3

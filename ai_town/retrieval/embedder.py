from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    """嵌入封装：支持 sentence-transformers（hf）和本地 Ollama（ollama）。

    参数:
      method: 'hf' | 'ollama' | 'auto'（默认 auto，优先 Ollama，失败回退 HF）
      model_name: 用于 HF 的模型名，或作为 Ollama 的 model 字段
    """

    def __init__(self, method: str = 'auto', model_name: str = 'all-MiniLM-L6-v2', ollama_client=None):
        self.method = method
        self.model_name = model_name
        self._hf_model = None
        self._ollama_client = ollama_client

    def _ensure_hf(self):
        if self._hf_model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise RuntimeError(f"无法导入 sentence-transformers: {e}")
            self._hf_model = SentenceTransformer(self.model_name)

    def _ensure_ollama(self):
        if self._ollama_client is None:
            try:
                from ai_town.core.ollama_client import OllamaClient
            except Exception as e:
                raise RuntimeError(f"无法导入 OllamaClient: {e}")
            self._ollama_client = OllamaClient(model=self.model_name)

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """返回 numpy.ndarray，shape=(n, dim) 或 (1, dim) 对于单个文本。

        当 method='auto' 时优先尝试 Ollama（HTTP/CLI），若失败则回退到 HF。
        """
        single = False
        if isinstance(texts, str):
            texts = [texts]
            single = True

        if self.method == 'ollama':
            self._ensure_ollama()
            vecs = self._ollama_client.embeddings(texts)
            arr = np.array(vecs, dtype='float32')
            return arr[0] if single else arr

        if self.method == 'hf':
            self._ensure_hf()
            emb = self._hf_model.encode(texts, convert_to_numpy=True)
            return emb[0] if single else emb

        # auto: try Ollama first, then HF
        try:
            self._ensure_ollama()
            vecs = self._ollama_client.embeddings(texts)
            arr = np.array(vecs, dtype='float32')
            return arr[0] if single else arr
        except Exception:
            # 回退 HF
            self._ensure_hf()
            emb = self._hf_model.encode(texts, convert_to_numpy=True)
            return emb[0] if single else emb


__all__ = ['Embedder']

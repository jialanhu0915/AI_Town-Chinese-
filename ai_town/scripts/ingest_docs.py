import os
from pathlib import Path

from ai_town.retrieval.embedder import Embedder

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)


def ingest_txt(path: str):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    # 简单按换行分段
    chunks = [seg.strip() for seg in text.split('\n\n') if seg.strip()]
    emb = Embedder()
    vectors = emb.embed(chunks)
    # 这里仅示例：保存为 npy
    import numpy as np
    np.save(DATA_DIR / (p.stem + "_chunks.npy"), vectors)
    print(f"ingested {len(chunks)} chunks")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: ingest_docs.py <path-to-txt>")
    else:
        ingest_txt(sys.argv[1])

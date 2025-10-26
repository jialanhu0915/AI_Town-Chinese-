import os
from pathlib import Path
import json

from ai_town.retrieval.embedder import Embedder
from ai_town.retrieval.splitter import extract_text_from_pdf, extract_text_from_txt, split_text_into_chunks
from ai_town.config import DATA_DIR

import numpy as np

MANIFEST = DATA_DIR / "index_manifest.json"


def ingest(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    if p.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(str(p))
    else:
        text = extract_text_from_txt(str(p))
    chunks = split_text_into_chunks(text, chunk_size=200, overlap=50)
    emb = Embedder()
    vectors = emb.embed(chunks)
    # 保存 vectors 和 metadata
    vec_file = DATA_DIR / (p.stem + "_vectors.npy")
    np.save(vec_file, vectors)
    meta = []
    for i, c in enumerate(chunks):
        meta.append({
            'source': str(p.name),
            'chunk_id': i,
            'text': c[:1000]
        })
    # 更新 manifest
    manifest = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    manifest[p.stem] = {
        'vectors': str(vec_file.name),
        'meta': meta
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"ingested {p.name}: {len(chunks)} chunks saved to {vec_file}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: ingest_docs.py <path-to-file>")
    else:
        ingest(sys.argv[1])

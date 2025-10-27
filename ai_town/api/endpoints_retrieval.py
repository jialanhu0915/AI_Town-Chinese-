from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ai_town.retrieval.storage import load_manifest, get_index_path
from ai_town.retrieval.faiss_utils import load_faiss_index, search_index
from ai_town.retrieval.embedder import Embedder
from ai_town.config import DATA_DIR, DEFAULT_EMBED_METHOD, EMBED_MODEL_PATH

router = APIRouter()


class RetrieveRequest(BaseModel):
    query: str
    dataset: Optional[str] = None
    embed_method: Optional[str] = None  # auto | ollama | hf
    model: Optional[str] = None
    topk: int = 3


class RetrieveItem(BaseModel):
    idx: int
    distance: float
    similarity: float
    source: str
    text: str


class RetrieveResponse(BaseModel):
    dataset: str
    results: List[RetrieveItem]


@router.post('/retrieve', response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest):
    manifest = load_manifest()
    if not manifest:
        raise HTTPException(status_code=404, detail='No datasets found. Run ingest first')

    dataset = req.dataset
    if dataset is None:
        if len(manifest) == 1:
            dataset = list(manifest.keys())[0]
        else:
            raise HTTPException(status_code=400, detail=f'Multiple datasets available. Specify one. Available: {list(manifest.keys())}')

    entry = manifest.get(dataset)
    if not entry:
        raise HTTPException(status_code=404, detail=f'Dataset {dataset} not found')

    # 使用统一的索引路径访问 API
    try:
        index_path = get_index_path(dataset)
        meta = entry.get('meta', [])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    index = load_faiss_index(str(index_path))

    nb = getattr(index, 'ntotal', None)
    topk = req.topk
    if nb is not None and topk > nb:
        topk = int(nb)

    embed_method = req.embed_method or DEFAULT_EMBED_METHOD
    model = req.model or EMBED_MODEL_PATH

    emb = Embedder(method=embed_method, model_name=model)
    try:
        qv = emb.embed(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Embedding failed: {e}')

    if qv.ndim == 1:
        qv = qv.reshape(1, -1)

    D, I = search_index(index, qv.astype('float32'), k=topk)

    results = []
    for dist, idx in zip(D[0], I[0]):
        if int(idx) < 0:
            continue
        try:
            item = meta[int(idx)]
            text = item.get('text', '')
            source = item.get('source', '')
        except Exception:
            text = ''
            source = ''
        similarity = 1.0 / (1.0 + float(dist))
        results.append({
            'idx': int(idx),
            'distance': float(dist),
            'similarity': similarity,
            'source': source,
            'text': text,
        })

    return {'dataset': dataset, 'results': results}

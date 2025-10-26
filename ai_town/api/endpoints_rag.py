from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ai_town.retrieval.storage import load_manifest
from ai_town.retrieval.faiss_utils import load_faiss_index, search_index
from ai_town.retrieval.embedder import Embedder
from ai_town.config import DATA_DIR, DEFAULT_EMBED_METHOD, EMBED_MODEL_PATH, DEFAULT_GEN_MODEL, DEFAULT_ENABLE_OLLAMA

router = APIRouter()


class RAGRequest(BaseModel):
    query: str
    dataset: Optional[str] = None
    embed_method: Optional[str] = None
    model: Optional[str] = None
    topk: int = 3
    # generation model when Ollama not used
    gen_model: Optional[str] = None


class RAGResponse(BaseModel):
    answer: str
    evidence: list


@router.post('/rag')
def rag(req: RAGRequest):
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

    index_file = entry.get('index')
    meta = entry.get('meta', [])
    if not index_file:
        raise HTTPException(status_code=400, detail=f'Dataset {dataset} has no index')

    index_path = DATA_DIR / index_file
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f'Index file not found: {index_path}')

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

    evidence = []
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
        evidence.append({'idx': int(idx), 'distance': float(dist), 'source': source, 'text': text})

    # 构建 prompt：简单拼接 evidence
    prompt_parts = ["You are a helpful assistant. Answer the question using only the provided evidence."]
    prompt_parts.append("Evidence:")
    for i, e in enumerate(evidence, start=1):
        prompt_parts.append(f"[{i}] {e['text']}")
    prompt_parts.append(f"Question: {req.query}")
    prompt = "\n\n".join(prompt_parts)

    # 尝试使用 Ollama（若配置允许），否则回退到本地 transformers 模型生成
    use_ollama = DEFAULT_ENABLE_OLLAMA
    try:
        from ai_town.core.ollama_client import OllamaClient
    except Exception:
        OllamaClient = None

    answer = None
    if use_ollama and OllamaClient is not None:
        client = OllamaClient(model=req.model or 'llama2')
        try:
            answer = client.chat(prompt)
        except Exception:
            answer = None

    if answer is None:
        # 回退到本地 transformers text-generation
        try:
            from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'transformers not available for generation: {e}')
        gen_model = req.gen_model or DEFAULT_GEN_MODEL
        # 若 gen_model 是本地路径，直接加载
        try:
            generator = pipeline('text-generation', model=gen_model, device=0)
        except Exception:
            # 回退到默认 device
            generator = pipeline('text-generation', model=gen_model)
        # 限制生成长度
        out = generator(prompt, max_length=200, do_sample=False)
        if isinstance(out, list) and len(out) > 0 and 'generated_text' in out[0]:
            answer = out[0]['generated_text']
        else:
            answer = str(out)

    return {'answer': answer, 'evidence': evidence}

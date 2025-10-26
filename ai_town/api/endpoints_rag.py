from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os

from ai_town.retrieval.storage import load_manifest
from ai_town.retrieval.faiss_utils import load_faiss_index, search_index
from ai_town.retrieval.embedder import Embedder
from ai_town.config import DATA_DIR, DEFAULT_EMBED_METHOD, EMBED_MODEL_PATH, DEFAULT_GEN_MODEL, DEFAULT_ENABLE_OLLAMA, AI_TOWN_ALLOW_ONLINE_GEN

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


def _dedupe_evidence(evidence, max_chars=2000):
    seen_texts = set()
    out = []
    total = 0
    for e in evidence:
        txt = e.get('text', '').strip()
        if not txt:
            continue
        if txt in seen_texts:
            continue
        seen_texts.add(txt)
        # respect max total chars to keep prompt size reasonable
        if total + len(txt) > max_chars:
            break
        out.append(e)
        total += len(txt)
    return out


def _postprocess_generated_text(generated: str, prompt: str) -> str:
    """尝试从生成文本中剥离原始 prompt 并返回首个合理答复段落。"""
    if not generated:
        return generated
    # 如果模型把 prompt 原样回显，尝试删除 prompt
    if prompt and prompt in generated:
        generated = generated.split(prompt, 1)[-1]
    # 分为段落，返回第一个非空段落
    parts = [p.strip() for p in generated.split('\n') if p.strip()]
    if parts:
        # 有时生成会把问题再次重复，保守选择最后一段或第一段
        return parts[0]
    return generated


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

    # 去重并限制证据长度
    evidence = _dedupe_evidence(evidence, max_chars=2000)

    # 构建更严格的 prompt：明确指令、简洁回答、不复述证据
    prompt_parts = [
        "你是一个基于提供证据的助理。请仅根据下面的证据回答问题。",
        "要求：直接给出简洁答案（1-3 句），不要复述证据内容或重复问题；如果证据不足，请明确说明。",
        "证据：",
    ]
    for i, e in enumerate(evidence, start=1):
        snippet = e['text'].strip()
        prompt_parts.append(f"[{i}] {snippet}")
    prompt_parts.append(f"问题：{req.query}")
    prompt_parts.append("只返回最终答案，不要包含额外的说明。")
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
        # 回退到本地 transformers text-generation/text2text-generation
        try:
            from transformers import pipeline
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'transformers not available for generation: {e}')
        gen_model = req.gen_model or DEFAULT_GEN_MODEL

        # 如果不允许在线下载，确保本地模型路径存在
        if not AI_TOWN_ALLOW_ONLINE_GEN:
            # 当 gen_model 看起来像本地路径时，检查其存在性
            try:
                gm_path = Path(gen_model)
                if not gm_path.exists():
                    raise HTTPException(status_code=400, detail=f'Local generation model not found at {gen_model}. Set AI_TOWN_ALLOW_ONLINE_GEN=true to allow online download or save the model to this path.')
            except HTTPException:
                raise
            except Exception:
                # 若 gen_model 不是路径格式，允许继续（可能是 HF name but online disabled）
                raise HTTPException(status_code=400, detail=f'Generation model {gen_model} not found locally and online download is disabled.')

        # 选择 pipeline 任务：若是 encoder-decoder（t5/flan）使用 text2text-generation
        task = 'text-generation'
        low_name = str(gen_model).lower()
        if any(x in low_name for x in ('t5', 'flan', 'bart', 'pegasus')):
            task = 'text2text-generation'
        # 尝试使用 GPU device 0，否则默认
        try:
            generator = pipeline(task, model=gen_model, device=0)
            out = generator(prompt, max_new_tokens=64, do_sample=False, temperature=0.0)
        except Exception:
            generator = pipeline(task, model=gen_model)
            out = generator(prompt, max_new_tokens=64, do_sample=False, temperature=0.0)
        # 提取生成结果
        if isinstance(out, list) and len(out) > 0:
            # text2text returns 'generated_text' or 'summary_text' depending on pipeline
            first = out[0]
            if isinstance(first, dict):
                raw = first.get('generated_text') or first.get('summary_text') or str(first)
            else:
                raw = str(first)
        else:
            raw = str(out)

        # 后处理：剥离 prompt 并提取首个合理答案段
        answer = _postprocess_generated_text(raw, prompt)

    return {'answer': answer, 'evidence': evidence}

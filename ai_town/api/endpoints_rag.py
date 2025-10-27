from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os

from ai_town.retrieval.storage import load_manifest, get_index_path
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
    """去重证据并限制总字符长度"""
    seen_texts = set()
    deduped = []
    total_chars = 0
    
    for e in evidence:
        text = e['text'][:400]  # 每个证据最多400字符
        text_hash = hash(text)
        if text_hash not in seen_texts and total_chars + len(text) <= max_chars:
            seen_texts.add(text_hash)
            deduped.append(e)
            total_chars += len(text)
    
    return deduped


def _build_optimized_prompt(query: str, evidence: list, gen_model: str) -> str:
    """
    根据生成模型类型构建优化的 prompt
    
    Args:
        query: 用户查询
        evidence: 检索到的证据列表
        gen_model: 生成模型名称或路径
    
    Returns:
        str: 优化的 prompt 字符串
    """
    low_name = str(gen_model).lower()
    is_flan_t5 = any(x in low_name for x in ('flan-t5', 'flan_t5'))
    is_t5 = 't5' in low_name
    is_seq2seq = any(x in low_name for x in ('t5', 'flan', 'bart', 'pegasus'))
    
    # 简化证据文本
    evidence_texts = []
    for i, e in enumerate(evidence[:3], 1):  # 只使用前3个证据
        text = e['text'].strip()
        # 清理数学公式和特殊符号
        text = _clean_evidence_text(text)
        if len(text) > 50:  # 过滤太短的片段
            evidence_texts.append(text[:300])  # 每个证据最多300字符
    
    if not evidence_texts:
        return f"请回答问题：{query}"
    
    if is_flan_t5:
        # FLAN-T5 专门优化的 prompt 格式 - 更简洁直接
        evidence_str = " ".join(evidence_texts)[:600]  # 进一步限制长度
        # 移除所有数学符号
        evidence_str = _clean_generated_text(evidence_str)
        
        # 使用更简单的 prompt 格式
        prompt = f"根据材料回答：{query}\n材料：{evidence_str}\n答案："
        
    elif is_t5:
        # 普通 T5 的简化格式
        evidence_str = " ".join(evidence_texts)[:600]
        prompt = f"材料：{evidence_str}\n问题：{query}\n答案："
        
    elif is_seq2seq:
        # 其他 seq2seq 模型
        evidence_str = "\n".join([f"- {text[:200]}" for text in evidence_texts])
        prompt = f"""基于以下信息回答问题：

{evidence_str}

问题：{query}
答案："""
        
    else:
        # 自回归模型（GPT 类）的格式
        evidence_str = "\n".join([f"[{i}] {text[:250]}" for i, text in enumerate(evidence_texts, 1)])
        prompt = f"""你是一个基于提供材料回答问题的助理。请根据以下材料简洁地回答问题。

材料：
{evidence_str}

问题：{query}

请用1-3句话回答："""
    
    return prompt


def _clean_evidence_text(text: str) -> str:
    """
    清理证据文本，移除数学公式和不完整的符号，保留中文描述
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    import re
    
    # 移除单独的数学符号和公式片段
    text = re.sub(r'[𝜶𝒊𝒎𝝎𝒙𝒃𝒚𝑱𝝏෍𝒂𝒌𝒏𝒇]+', ' ', text)
    text = re.sub(r'[αβγδεζηθικλμνξοπρστυφχψωΩ]+', ' ', text)
    
    # 移除数学表达式
    text = re.sub(r'[𝑓𝑧𝑥𝑦𝑤𝑏]+\s*[=+\-*/]\s*[𝑓𝑧𝑥𝑦𝑤𝑏]+', ' ', text)
    text = re.sub(r'\b[a-zA-Z]\d*\s*[=+\-*/]\s*[a-zA-Z]\d*\b', ' ', text)
    text = re.sub(r'[=+\-*/]{2,}', ' ', text)
    
    # 移除单独的符号和数学结构
    text = re.sub(r'[{}()[\]]+', ' ', text)
    text = re.sub(r'[•·▪▫■□●○]+', ' ', text)
    text = re.sub(r'Σ\|𝑓', ' ', text)
    text = re.sub(r'෍\s*𝒊=𝟏', ' ', text)
    
    # 移除纯数字行
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # 保留包含中文的行，或包含完整英文单词的行
        if any('\u4e00' <= char <= '\u9fff' for char in line) or \
           (len([w for w in line.split() if w.isalpha() and len(w) > 2]) > 0):
            # 进一步清理该行的数学符号
            line = re.sub(r'[𝜶𝒊𝒎𝝎𝒙𝒃𝒚𝑱𝝏෍𝒂𝒌𝒏𝒟𝒇]+', ' ', line)
            if len(line.strip()) > 10:  # 只保留有意义长度的行
                cleaned_lines.append(line.strip())
    
    text = ' '.join(cleaned_lines)
    
    # 清理多余空格
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def _postprocess_generated_text(generated: str, prompt: str) -> str:
    """
    优化后的生成文本后处理函数，专门处理 FLAN-T5 等模型的输出
    """
    import re
    
    if not generated:
        return "无法生成答案"
    
    # 清理生成文本
    generated = generated.strip()
    
    # 清理数学符号和不完整的公式
    generated = _clean_generated_text(generated)
    
    # 对于 text2text-generation 模型（如 T5），通常不会包含 prompt
    # 但可能包含一些格式标记或重复内容
    
    # 如果模型把 prompt 原样回显，尝试删除 prompt（主要针对 causal LM）
    if prompt and prompt in generated:
        generated = generated.split(prompt, 1)[-1].strip()
    
    # 删除常见的开头标记
    prefixes_to_remove = [
        "答案:", "回答:", "Answer:", "Response:", "答:", "A:", 
        "根据材料", "根据以上", "基于材料", "材料显示", "文中提到"
    ]
    for prefix in prefixes_to_remove:
        if generated.startswith(prefix):
            generated = generated[len(prefix):].strip()
            # 删除可能的冒号或逗号
            if generated.startswith((':', '：', '，', ',')):
                generated = generated[1:].strip()
    
    # 删除重复的问题
    if "问题" in generated or "Question" in generated:
        parts = generated.split('\n')
        cleaned_parts = []
        for part in parts:
            if not any(marker in part.lower() for marker in ['问题', 'question', '证据', 'evidence']):
                cleaned_parts.append(part.strip())
        if cleaned_parts:
            generated = ' '.join(cleaned_parts)
    
    # 分为句子，处理不完整的句子
    sentences = re.split(r'[.。!！?？;；]', generated)
    meaningful_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 5 and not _is_incomplete_formula(sentence):
            meaningful_sentences.append(sentence)
    
    if meaningful_sentences:
        # 取前1-2个完整的句子
        result = '。'.join(meaningful_sentences[:2])
        if not result.endswith(('。', '.', '！', '!', '？', '?')):
            result += '。'
        return result
    
    # 如果没有找到完整句子，返回清理后的原文（如果足够长）
    if len(generated) > 10:
        # 确保以标点结尾
        if not generated.endswith(('。', '.', '！', '!', '？', '?')):
            generated += '。'
        return generated
    
    return "无法根据提供的材料生成答案。"


def _clean_generated_text(text: str) -> str:
    """
    激进清理生成文本中的数学符号和不完整片段
    """
    import re
    
    # 移除所有数学符号
    text = re.sub(r'[𝜶𝒊𝒎𝝎𝒙𝒃𝒚𝑱𝝏෍𝒂𝒌𝒏𝒟𝒇𝒌𝒎𝒏]+', '', text)
    text = re.sub(r'[αβγδεζηθικλμνξοπρστυφχψωΩ]+', '', text)
    
    # 移除数学表达式和公式
    text = re.sub(r'wmnk|wmn|𝑤𝑚𝑛|𝑏𝑚𝑛', '', text)
    text = re.sub(r'\b[a-zA-Z]\d*\s*[=+\-*/]\s*[a-zA-Z]\d*\b', '', text)
    text = re.sub(r'[=+\-*/]{2,}', '', text)
    text = re.sub(r'[=:+\-*/,，。：]{3,}', '', text)
    
    # 移除单独的字母和数字组合（如 k, m, n）
    text = re.sub(r'\b[a-zA-Z]\s*[,，]\s*[a-zA-Z]\s*[,，]\s*[a-zA-Z]\b', '', text)
    text = re.sub(r'\b[kmn]\s*[,，:：]', '', text)
    
    # 移除大括号、括号和其他符号
    text = re.sub(r'[{}()[\]]+', ' ', text)
    text = re.sub(r'[•·▪▫■□●○]+', ' ', text)
    text = re.sub(r'Σ\|𝑓|෍', ' ', text)
    
    # 移除纯符号行
    text = re.sub(r'^[^a-zA-Z\u4e00-\u9fff]*$', '', text, flags=re.MULTILINE)
    
    # 清理多余空格和标点
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[,，。：:]{2,}', '。', text)
    
    return text.strip()


def _is_incomplete_formula(text: str) -> bool:
    """
    判断文本是否是不完整的数学公式
    """
    # 如果包含大量数学符号，可能是公式
    math_chars = len([c for c in text if c in '+-*/=()[]{}αβγδεωπσμλτφθψ𝜶𝒊𝒎𝝎𝒙𝒃𝒚'])
    total_chars = len(text)
    
    if total_chars > 0 and math_chars / total_chars > 0.3:
        return True
    
    # 如果主要是单个字母和数字
    if len(text.split()) < 3 and any(c.isalpha() for c in text) and any(c.isdigit() for c in text):
        return True
    
    return False


def _extract_key_info_from_evidence(query: str, evidence: list) -> str:
    """
    当生成模型失败时，从证据中提取关键信息作为 fallback 答案
    
    Args:
        query: 用户查询
        evidence: 证据列表
        
    Returns:
        str: 提取的关键信息
    """
    if not evidence:
        return "抱歉，没有找到相关信息。"
    
    # 根据查询类型提取不同的关键信息
    query_lower = query.lower()
    
    key_sentences = []
    for e in evidence[:2]:  # 只看前两个最相关的证据
        text = e['text']
        text = _clean_evidence_text(text)  # 清理数学符号
        
        # 按句子分割
        import re
        sentences = re.split(r'[。！？.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # 跳过太短的句子
                continue
                
            # 根据查询关键词匹配相关句子
            if any(keyword in sentence for keyword in ['人工智能', 'AI', '定义']):
                if any(q_word in query for q_word in ['什么是', '定义', '人工智能']):
                    key_sentences.append(sentence)
            
            elif any(keyword in sentence for keyword in ['神经网络', '网络', '算法', '模型']):
                if any(q_word in query for q_word in ['神经网络', '原理', '什么是']):
                    key_sentences.append(sentence)
                    
            elif any(keyword in sentence for keyword in ['深度学习', '应用', '领域', '突破']):
                if any(q_word in query for q_word in ['深度学习', '应用', '用途']):
                    key_sentences.append(sentence)
    
    if key_sentences:
        # 取最相关的1-2个句子
        result = '。'.join(key_sentences[:2])
        if not result.endswith('。'):
            result += '。'
        return result
    
    # 如果没有匹配的关键句子，返回第一个证据的简化版本
    first_evidence = evidence[0]['text']
    first_evidence = _clean_evidence_text(first_evidence)
    
    # 提取前100个字符作为摘要
    summary = first_evidence[:100].strip()
    if len(summary) > 20:
        if not summary.endswith('。'):
            summary += '。'
        return f"根据资料显示：{summary}"
    
    return "抱歉，无法从提供的材料中提取到相关信息。"


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

    # 构建针对不同模型优化的 prompt
    prompt = _build_optimized_prompt(req.query, evidence, req.gen_model or DEFAULT_GEN_MODEL)

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
        is_seq2seq = any(x in low_name for x in ('t5', 'flan', 'bart', 'pegasus'))
        if is_seq2seq:
            task = 'text2text-generation'
        
        # 使用优化后的 prompt（已经根据模型类型进行了优化）
        gen_prompt = prompt
            
        # 尝试使用 GPU device 0，否则默认
        try:
            generator = pipeline(task, model=gen_model, device=0)
            # 对于 FLAN-T5，使用更保守的生成参数
            if is_seq2seq:
                out = generator(gen_prompt, max_new_tokens=50, do_sample=False, 
                               temperature=0.0, truncation=True, 
                               no_repeat_ngram_size=3)
            else:
                out = generator(gen_prompt, max_new_tokens=128, do_sample=False, 
                               temperature=0.0, truncation=True)
        except Exception:
            generator = pipeline(task, model=gen_model)
            if is_seq2seq:
                out = generator(gen_prompt, max_new_tokens=50, do_sample=False, 
                               temperature=0.0, truncation=True,
                               no_repeat_ngram_size=3)
            else:
                out = generator(gen_prompt, max_new_tokens=128, do_sample=False, 
                               temperature=0.0, truncation=True)
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
        
        # 如果生成失败，尝试从证据中提取关键信息作为 fallback
        if not answer or answer == "无法根据提供的材料生成答案。" or len(answer) < 10:
            answer = _extract_key_info_from_evidence(req.query, evidence)

    return {'answer': answer, 'evidence': evidence}

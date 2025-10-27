"""
查询示例脚本：读取 manifest、加载 Faiss 索引、使用 Embedder 生成 query embedding 并返回 top-k 片段与相似度。

用法（Windows cmd.exe）：
  .venv\Scripts\activate
  python -m ai_town.scripts.query_demo "你的查询文本" --model B:\OllamaModels\LLM_models --embed-method hf --topk 3

参数：
  query: 待检索文本
  --dataset: 指定 manifest 中的数据集名（默认如果只有一个数据集则自动使用）
  --model: 本地 HF 模型路径或 HF 名称（用于 --embed-method hf）
  --embed-method: hf|ollama|auto
  --topk: 返回数量
"""
import argparse
import json
from pathlib import Path
import numpy as np

from ai_town.retrieval.storage import load_manifest, get_index_path
from ai_town.retrieval.faiss_utils import load_faiss_index, search_index
from ai_town.retrieval.embedder import Embedder
from ai_town.config import DATA_DIR


def _l2_to_similarity(dist: float) -> float:
    # 把 L2 距离转换为 [0,1] 的相似度评分，简单处理：similarity = 1 / (1 + dist)
    try:
        return 1.0 / (1.0 + float(dist))
    except Exception:
        return 0.0


def main():
    parser = argparse.ArgumentParser(description='Query demo: search manifest/faiss index')
    parser.add_argument('query', help='Query text')
    parser.add_argument('--dataset', type=str, default=None, help='Dataset name in manifest')
    parser.add_argument('--model', type=str, default=None, help='HF model path or name (for hf embedder)')
    parser.add_argument('--embed-method', type=str, default='hf', choices=['hf', 'ollama', 'auto'], help='Embedding backend')
    parser.add_argument('--topk', type=int, default=3, help='Top K results')
    args = parser.parse_args()

    manifest = load_manifest()
    if not manifest:
        print('No datasets found in manifest. Run ingest first.')
        return

    dataset = args.dataset
    if dataset is None:
        if len(manifest) == 1:
            dataset = list(manifest.keys())[0]
            print(f'Using dataset: {dataset}')
        else:
            print('Multiple datasets found in manifest. Please provide --dataset. Available:')
            for k in manifest.keys():
                print('  -', k)
            return

    entry = manifest.get(dataset)
    if entry is None:
        print(f'Dataset {dataset} not found in manifest')
        return

    # 使用统一的索引路径访问 API
    try:
        index_path = get_index_path(dataset)
        vectors_file = entry.get('vectors')
        meta = entry.get('meta', [])
    except ValueError as e:
        print(f'Error accessing dataset {dataset}: {e}')
        return

    print(f'Loading Faiss index from {index_path} ...')
    index = load_faiss_index(str(index_path))

    # 获取向量总数以限制 topk
    try:
        nb = index.ntotal
    except Exception:
        nb = None

    topk = args.topk
    if nb is not None and topk > nb:
        print(f'Requested topk={topk} greater than number of vectors={nb}, reducing topk to {nb}')
        topk = int(nb)

    # prepare embedder
    emb = Embedder(method=args.embed_method, model_name=args.model or 'all-MiniLM-L6-v2')
    print('Computing query embedding...')
    qv = emb.embed(args.query)
    # ensure shape (1, dim)
    if qv.ndim == 1:
        qv = qv.reshape(1, -1)

    D, I = search_index(index, qv.astype('float32'), k=topk)

    print('\nTop results:')
    found = 0
    for rank, (dist, idx) in enumerate(zip(D[0], I[0]), start=1):
        if int(idx) < 0:
            # Faiss 用 -1 填充不足的结果，跳过
            continue
        found += 1
        try:
            item = meta[int(idx)]
            text = item.get('text', '')
            source = item.get('source', '')
        except Exception:
            text = '<no-meta>'
            source = ''
        sim = _l2_to_similarity(dist)
        print(f'[{found}] idx={idx} distance={dist:.4f} similarity={sim:.4f} source={source}')
        print('    ', text[:400].replace('\n', ' '))
        print()

    if found == 0:
        print('(no valid results returned)')


if __name__ == '__main__':
    main()

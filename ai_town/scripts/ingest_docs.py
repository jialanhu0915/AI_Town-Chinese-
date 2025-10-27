import os
from pathlib import Path
import json
import argparse
import logging

from ai_town.retrieval.embedder import Embedder
from ai_town.retrieval.splitter import extract_text_from_pdf, extract_text_from_txt, split_text_into_chunks
from ai_town.config import DATA_DIR
from ai_town.retrieval.faiss_utils import build_faiss_index

import numpy as np

MANIFEST = DATA_DIR / "index_manifest.json"

logger = logging.getLogger(__name__)


def ingest(path: str, chunk_size: int = 200, overlap: int = 50, embed_model: str = None, build_index: bool = True, embed_method: str = 'auto'):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    
    # 如果是目录，处理目录中的所有支持文件
    if p.is_dir():
        logger.info(f"Processing directory: {p}")
        supported_extensions = ['.pdf', '.txt', '.md']
        files_to_process = []
        
        for ext in supported_extensions:
            files_to_process.extend(p.glob(f'*{ext}'))
            files_to_process.extend(p.glob(f'**/*{ext}'))  # 递归搜索
        
        if not files_to_process:
            logger.warning(f"No supported files found in directory: {p}")
            logger.info(f"Supported extensions: {supported_extensions}")
            return
        
        logger.info(f"Found {len(files_to_process)} files to process")
        for file_path in files_to_process:
            logger.info(f"Processing: {file_path}")
            try:
                ingest(str(file_path), chunk_size, overlap, embed_model, build_index, embed_method)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
        return
    
    # 处理单个文件
    logger.info(f"Ingesting {p} (chunk_size={chunk_size}, overlap={overlap}, embed_model={embed_model}, build_index={build_index}, embed_method={embed_method})")
    if p.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(str(p))
    else:
        text = extract_text_from_txt(str(p))
    chunks = split_text_into_chunks(text, chunk_size=chunk_size, overlap=overlap)
    if not chunks:
        logger.warning("No text chunks extracted.")
        return
    emb = Embedder(method=embed_method, model_name=embed_model or 'all-MiniLM-L6-v2')
    vectors = emb.embed(chunks)
    # 保存 vectors 和 metadata
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    vec_file = DATA_DIR / (p.stem + "_vectors.npy")
    np.save(vec_file, vectors)
    index_path = None
    index_safe_name = None
    if build_index:
        try:
            index_path = build_faiss_index(vectors, index_name=p.stem)
            # index_path 是实际保存的文件路径（通常为 ASCII-safe 名称）
            index_safe_name = Path(index_path).name
        except Exception as e:
            index_path = None
            logger.warning(f"构建 Faiss 索引失败: {e}")

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
        'index_original': f"{p.stem}.index",
        'index_safe': index_safe_name,
        'meta': meta
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info(f"Ingested {p.name}: {len(chunks)} chunks saved to {vec_file}")
    if index_path:
        logger.info(f"Faiss index saved to: {index_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description='Ingest document to vector store and build Faiss index')
    parser.add_argument('path', help='Path to document (txt or pdf)')
    parser.add_argument('--chunk-size', type=int, default=200, help='Chunk size in words')
    parser.add_argument('--overlap', type=int, default=50, help='Overlap size in words')
    parser.add_argument('--embed-model', type=str, default=None, help='HF model name or Ollama model name')
    parser.add_argument('--embed-method', type=str, default='auto', choices=['auto', 'ollama', 'hf'], help='Embedding backend to use (auto=prefer Ollama then HF)')
    parser.add_argument('--no-build-index', action='store_true', help='Do not build Faiss index after embedding')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

    ingest(args.path, chunk_size=args.chunk_size, overlap=args.overlap, embed_model=args.embed_model, build_index=not args.no_build_index, embed_method=args.embed_method)


if __name__ == '__main__':
    main()

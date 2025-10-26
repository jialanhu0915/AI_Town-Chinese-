from typing import List
from pypdf import PdfReader


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n\n".join(pages)


def extract_text_from_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def split_text_into_chunks(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """按词拆分为 chunk_size 大小，重叠 overlap（以词为单位）。返回 chunk 列表。"""
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    L = len(words)
    while start < L:
        end = min(start + chunk_size, L)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == L:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

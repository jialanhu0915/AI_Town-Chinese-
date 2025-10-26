import numpy as np
from pathlib import Path
import faiss
from ai_town.config import DATA_DIR
import tempfile
import shutil
import hashlib
from urllib.parse import quote


def _make_safe_index_filename(index_name: str) -> str:
    # percent-encode to ASCII and append short hash to avoid collisions and long names
    safe = quote(index_name, safe='')
    h = hashlib.md5(index_name.encode('utf-8')).hexdigest()[:8]
    return f"{safe}_{h}.index"


def build_faiss_index(vectors: np.ndarray, index_name: str):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    safe_filename = _make_safe_index_filename(index_name)
    final_path = DATA_DIR / safe_filename

    # 为避免临时文件名包含非 ASCII 字符（例如 index_name 中的中文），使用基于 hash 的 ASCII 前缀
    tmp_prefix = "faiss_tmp_" + hashlib.md5(index_name.encode('utf-8')).hexdigest()[:8]

    try:
        with tempfile.NamedTemporaryFile(prefix=tmp_prefix, suffix=".index", delete=False, dir=str(DATA_DIR)) as tf:
            tmp_path = Path(tf.name)
        # 使用 faiss 将索引写入临时文件（该文件名为 ASCII 前缀）
        faiss.write_index(index, str(tmp_path))

        # 尝试使用原子替换以避免编码/权限问题
        try:
            tmp_path.replace(final_path)
        except Exception:
            # fallback 到二进制复制
            with tmp_path.open('rb') as fr, final_path.open('wb') as fw:
                shutil.copyfileobj(fr, fw)
    except Exception as e:
        # 清理临时文件（如果存在）
        try:
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        raise RuntimeError(f"Failed to write faiss index to {final_path}: {e}")
    finally:
        # 移除临时文件（如果尚存在）
        try:
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass

    # 返回实际存储的文件路径（安全 ASCII 名称）
    return str(final_path)


def load_faiss_index(index_path: str):
    path = Path(index_path)
    if not path.exists():
        raise FileNotFoundError(index_path)
    return faiss.read_index(str(path))


def search_index(index, query_vector: np.ndarray, k: int = 5):
    D, I = index.search(query_vector, k)
    return D, I

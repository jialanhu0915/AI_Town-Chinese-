"""
Normalize Faiss index filenames in ai_town/data and update manifest to use ASCII-safe names.

用法（在项目根并激活 venv 下运行）:
  python ai_town\scripts\normalize_index_names.py

脚本行为：
- 读取 manifest（ai_town/data/index_manifest.json），对每个数据集计算期望的 ASCII-safe 索引名（与 faiss_utils 相同的 percent-encoding + md5 后缀策略）。
- 如果安全名已存在则跳过；否则尝试找到一个候选 .index 文件（包括原始中文名或已发生 mojibake 的名），将其重命名为安全名并更新 manifest 的 index_safe 字段。
- 若找不到任何候选文件，会在输出中报告，需要你手动处理或重新 ingest。

注意：建议先备份 ai_town/data/index_manifest.json 和 ai_town/data 目录。
"""
from pathlib import Path
import json
import hashlib
from urllib.parse import quote
import shutil

DATA_DIR = Path(__file__).resolve().parents[2] / 'ai_town' / 'data'
MANIFEST = DATA_DIR / 'index_manifest.json'


def _make_safe_index_filename(index_name: str) -> str:
    safe = quote(index_name, safe='')
    h = hashlib.md5(index_name.encode('utf-8')).hexdigest()[:8]
    return f"{safe}_{h}.index"


def find_candidate_index_files(stem: str):
    # 搜寻 data 目录中所有 .index 文件，返回可能与 stem 相关的候选
    candidates = []
    for p in DATA_DIR.glob('*.index'):
        name = p.name
        if stem in name or quote(stem, safe='') in name:
            candidates.append(p)
    return candidates


def main():
    if not MANIFEST.exists():
        print(f'Manifest not found: {MANIFEST}')
        return
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))

    changed = False
    for dataset, entry in manifest.items():
        stem = dataset
        expected_safe = _make_safe_index_filename(stem)
        expected_path = DATA_DIR / expected_safe

        # 已有安全名存在
        if expected_path.exists():
            # ensure manifest records it
            if entry.get('index_safe') != expected_safe:
                print(f'Updating manifest for {dataset}: index_safe set to {expected_safe}')
                entry['index_safe'] = expected_safe
                changed = True
            continue

        # 优先检查 manifest 中已有的 index_safe/index_original/index
        candidates = []
        for key in ('index_safe', 'index', 'index_original'):
            v = entry.get(key)
            if v:
                p = DATA_DIR / v
                if p.exists():
                    candidates.append(p)

        # 如果没有直接候选，尝试根据 stem 搜索
        if not candidates:
            found = find_candidate_index_files(stem)
            candidates.extend(found)

        if not candidates:
            print(f'[WARN] No index file found for dataset {dataset}. Expected safe name: {expected_safe}')
            continue

        # 选择第一个候选作为来源并重命名为安全名
        src = candidates[0]
        print(f'Renaming {src.name} -> {expected_safe}')
        try:
            dst = DATA_DIR / expected_safe
            # 若目标已存在，先备份目标
            if dst.exists():
                bak = DATA_DIR / (expected_safe + '.bak')
                print(f'Backing up existing target {dst} -> {bak}')
                shutil.move(str(dst), str(bak))
            shutil.move(str(src), str(dst))
            entry['index_original'] = src.name
            entry['index_safe'] = expected_safe
            changed = True
        except Exception as e:
            print(f'[ERROR] Failed to rename {src} -> {expected_safe}: {e}')

    if changed:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Manifest updated.')
    else:
        print('No changes needed.')


if __name__ == '__main__':
    main()

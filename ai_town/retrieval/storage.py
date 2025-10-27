import json
import os
from pathlib import Path
from ai_town.config import DATA_DIR

MANIFEST = DATA_DIR / 'index_manifest.json'


def load_manifest():
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def save_manifest(manifest: dict):
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')


def list_datasets():
    return list(load_manifest().keys())


def get_dataset(name: str):
    manifest = load_manifest()
    return manifest.get(name)


def get_index_path(dataset_name: str) -> str:
    """
    统一获取数据集的索引路径

    优先使用 index_safe（ASCII-safe 文件名），回退到 index 或 index_original
    返回实际存在的索引文件路径，如果都不存在则抛出异常

    Args:
        dataset_name: 数据集名称

    Returns:
        str: 索引文件的绝对路径

    Raises:
        ValueError: 如果数据集不存在或索引文件不存在
    """
    dataset = get_dataset(dataset_name)
    if not dataset:
        raise ValueError(f"Dataset '{dataset_name}' not found in manifest")

    # 尝试的索引路径候选列表（按优先级）
    index_candidates = []

    # 1. 优先使用 index_safe（新格式，ASCII-safe）
    if 'index_safe' in dataset:
        index_candidates.append(os.path.join(DATA_DIR, dataset['index_safe']))

    # 2. 回退到 index（可能是旧格式或直接路径）
    if 'index' in dataset:
        index_path = dataset['index']
        # 如果是相对路径，则相对于 DATA_DIR
        if not os.path.isabs(index_path):
            index_candidates.append(os.path.join(DATA_DIR, index_path))
        else:
            index_candidates.append(index_path)

    # 3. 最后尝试 index_original（原始名称，可能有中文）
    if 'index_original' in dataset:
        index_candidates.append(os.path.join(DATA_DIR, dataset['index_original']))

    # 查找第一个存在的索引文件
    for index_path in index_candidates:
        if os.path.exists(index_path):
            return index_path

    # 所有候选都不存在
    raise ValueError(f"No valid index file found for dataset '{dataset_name}'. Candidates tried: {index_candidates}")


def get_vectors_path(dataset_name: str) -> str:
    """
    获取数据集的向量文件路径

    Args:
        dataset_name: 数据集名称

    Returns:
        str: 向量文件的绝对路径

    Raises:
        ValueError: 如果数据集不存在或向量文件不存在
    """
    dataset = get_dataset(dataset_name)
    if not dataset:
        raise ValueError(f"Dataset '{dataset_name}' not found in manifest")

    if 'vectors' not in dataset:
        raise ValueError(f"No vectors file specified for dataset '{dataset_name}'")

    vectors_path = dataset['vectors']
    # 如果是相对路径，则相对于 DATA_DIR
    if not os.path.isabs(vectors_path):
        vectors_path = os.path.join(DATA_DIR, vectors_path)

    if not os.path.exists(vectors_path):
        raise ValueError(f"Vectors file not found: {vectors_path}")

    return vectors_path


def get_metadata_path(dataset_name: str) -> str:
    """
    获取数据集的元数据文件路径

    Args:
        dataset_name: 数据集名称

    Returns:
        str: 元数据文件的绝对路径

    Raises:
        ValueError: 如果数据集不存在或元数据文件不存在
    """
    dataset = get_dataset(dataset_name)
    if not dataset:
        raise ValueError(f"Dataset '{dataset_name}' not found in manifest")

    if 'meta' not in dataset:
        raise ValueError(f"No metadata file specified for dataset '{dataset_name}'")

    meta_path = dataset['meta']
    # 如果是相对路径，则相对于 DATA_DIR
    if not os.path.isabs(meta_path):
        meta_path = os.path.join(DATA_DIR, meta_path)

    if not os.path.exists(meta_path):
        raise ValueError(f"Metadata file not found: {meta_path}")

    return meta_path

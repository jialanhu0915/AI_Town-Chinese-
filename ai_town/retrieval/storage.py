import json
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

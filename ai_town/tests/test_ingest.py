import os
from ai_town.scripts.ingest_docs import ingest
from ai_town.retrieval.storage import load_manifest


def test_ingest_txt(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("Hello world\n\nThis is a test document.")
    ingest(str(p))
    manifest = load_manifest()
    assert p.stem in manifest

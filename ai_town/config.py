from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

for p in [DATA_DIR, LOG_DIR]:
    p.mkdir(parents=True, exist_ok=True)

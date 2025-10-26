from pathlib import Path
import os

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

for p in [DATA_DIR, LOG_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# ==== 可编辑的默认配置（把你的模型路径写在这里，或通过环境变量覆盖） ====
# 示例：将你的本地 embedding 模型路径和生成模型路径填写到下方，便于脚本默认使用。
EMBED_MODEL_PATH = os.environ.get('AI_TOWN_EMBED_MODEL', r'B:\OllamaModels\LLM_models')
GEN_MODEL_PATH = os.environ.get('AI_TOWN_GEN_MODEL', r'B:\OllamaModels\distilgpt2')

# 默认嵌入后端：'hf' | 'ollama' | 'auto'
DEFAULT_EMBED_METHOD = os.environ.get('AI_TOWN_EMBED_METHOD', 'hf')

# 默认生成模型（用于本地 transformers 回退），可以是 HF 名称或本地路径
DEFAULT_GEN_MODEL = os.environ.get('AI_TOWN_GEN_MODEL_NAME', GEN_MODEL_PATH)

# 是否默认启用 Ollama（若启用会尝试 HTTP/CLI 调用）；默认 False，按需开启
DEFAULT_ENABLE_OLLAMA = os.environ.get('AI_TOWN_ENABLE_OLLAMA', 'false').lower() in ('1', 'true', 'yes')

# 日志级别
DEFAULT_LOG_LEVEL = os.environ.get('AI_TOWN_LOG_LEVEL', 'INFO')

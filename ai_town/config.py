"""
AI Town 配置文件
"""

from pathlib import Path
import os

# 基础路径设置
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

# 创建必要目录
for directory in [DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# AI Town 模拟设置
SIMULATION_CONFIG = {
    "time_multiplier": float(os.environ.get('AI_TOWN_TIME_MULTIPLIER', '10.0')),  # 时间加速倍数
    "step_interval": float(os.environ.get('AI_TOWN_STEP_INTERVAL', '1.0')),      # 步骤间隔（秒）
    "max_agents": int(os.environ.get('AI_TOWN_MAX_AGENTS', '20')),               # 最大智能体数量
    "auto_save_interval": int(os.environ.get('AI_TOWN_AUTO_SAVE', '300')),       # 自动保存间隔（秒）
}

# 世界和地图设置
WORLD_CONFIG = {
    "map_width": int(os.environ.get('AI_TOWN_MAP_WIDTH', '100')),
    "map_height": int(os.environ.get('AI_TOWN_MAP_HEIGHT', '100')),
    "max_events": int(os.environ.get('AI_TOWN_MAX_EVENTS', '100')),
    "event_cleanup_interval": int(os.environ.get('AI_TOWN_CLEANUP_INTERVAL', '60')),
}

# 智能体默认设置
AGENT_CONFIG = {
    "default_perception_radius": float(os.environ.get('AI_TOWN_PERCEPTION_RADIUS', '5.0')),
    "default_conversation_radius": float(os.environ.get('AI_TOWN_CONVERSATION_RADIUS', '2.0')),
    "memory_reflection_threshold": int(os.environ.get('AI_TOWN_REFLECTION_THRESHOLD', '150')),
    "max_memory_items": int(os.environ.get('AI_TOWN_MAX_MEMORIES', '1000')),
}

# API 设置
API_CONFIG = {
    "host": os.environ.get('AI_TOWN_API_HOST', '0.0.0.0'),
    "port": int(os.environ.get('AI_TOWN_API_PORT', '8000')),
    "debug": os.environ.get('AI_TOWN_DEBUG', 'false').lower() in ('1', 'true', 'yes'),
}

# 日志设置
LOG_CONFIG = {
    "level": os.environ.get('AI_TOWN_LOG_LEVEL', 'INFO'),
    "file_logging": os.environ.get('AI_TOWN_FILE_LOG', 'true').lower() in ('1', 'true', 'yes'),
    "max_log_files": int(os.environ.get('AI_TOWN_MAX_LOG_FILES', '10')),
}

# Ollama 集成设置（可选）
OLLAMA_CONFIG = {
    "enabled": os.environ.get('AI_TOWN_ENABLE_OLLAMA', 'false').lower() in ('1', 'true', 'yes'),
    "base_url": os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
    "default_model": os.environ.get('OLLAMA_MODEL', 'llama2'),
}

# 数据持久化设置
PERSISTENCE_CONFIG = {
    "memories_dir": DATA_DIR / "memories",
    "world_states_dir": DATA_DIR / "world_states", 
    "agent_profiles_dir": DATA_DIR / "agent_profiles",
    "auto_save": True,
}

# 创建持久化目录
for directory in PERSISTENCE_CONFIG.values():
    if isinstance(directory, Path):
        directory.mkdir(parents=True, exist_ok=True)

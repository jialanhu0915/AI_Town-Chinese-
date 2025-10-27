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

# LLM 提供商配置
LLM_CONFIG = {
    # 默认 LLM 提供商优先级顺序
    "default_provider": os.environ.get('AI_TOWN_LLM_PROVIDER', 'ollama'),
    "fallback_chain": ["ollama", "openai", "mock"],
    
    # Ollama 配置
    "ollama": {
        "enabled": os.environ.get('AI_TOWN_OLLAMA_ENABLED', 'true').lower() in ('1', 'true', 'yes'),
        "base_url": os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
        "model_name": os.environ.get('OLLAMA_MODEL', 'deepseek-r1:1.5b'),
        "timeout": float(os.environ.get('OLLAMA_TIMEOUT', '60.0')),
        "temperature": float(os.environ.get('OLLAMA_TEMPERATURE', '0.7')),
        "max_tokens": int(os.environ.get('OLLAMA_MAX_TOKENS', '500')),
    },
    
    # OpenAI 配置
    "openai": {
        "enabled": bool(os.environ.get('OPENAI_API_KEY')),
        "api_key": os.environ.get('OPENAI_API_KEY'),
        "model_name": os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
        "timeout": float(os.environ.get('OPENAI_TIMEOUT', '60.0')),
        "temperature": float(os.environ.get('OPENAI_TEMPERATURE', '0.7')),
        "max_tokens": int(os.environ.get('OPENAI_MAX_TOKENS', '500')),
    },
    
    # Mock LLM 配置（测试用）
    "mock": {
        "enabled": True,  # 始终可用作为后备
        "delay": float(os.environ.get('MOCK_LLM_DELAY', '0.1')),
        "random_responses": os.environ.get('MOCK_LLM_RANDOM', 'true').lower() in ('1', 'true', 'yes'),
    },
}

# 智能体 LLM 配置
AGENT_LLM_CONFIG = {
    # 各角色的默认 LLM 设置
    "alice": {
        "provider": os.environ.get('ALICE_LLM_PROVIDER', LLM_CONFIG["default_provider"]),
        "use_llm_for_planning": os.environ.get('ALICE_LLM_PLANNING', 'true').lower() in ('1', 'true', 'yes'),
        "use_llm_for_conversation": os.environ.get('ALICE_LLM_CONVERSATION', 'true').lower() in ('1', 'true', 'yes'),
        "use_llm_for_reflection": os.environ.get('ALICE_LLM_REFLECTION', 'true').lower() in ('1', 'true', 'yes'),
    },
    
    "bob": {
        "provider": os.environ.get('BOB_LLM_PROVIDER', LLM_CONFIG["default_provider"]),
        "use_llm_for_planning": os.environ.get('BOB_LLM_PLANNING', 'true').lower() in ('1', 'true', 'yes'),
        "use_llm_for_conversation": os.environ.get('BOB_LLM_CONVERSATION', 'true').lower() in ('1', 'true', 'yes'),
        "use_llm_for_reflection": os.environ.get('BOB_LLM_REFLECTION', 'true').lower() in ('1', 'true', 'yes'),
    },
    
    "charlie": {
        "provider": os.environ.get('CHARLIE_LLM_PROVIDER', LLM_CONFIG["default_provider"]),
        "use_llm_for_planning": os.environ.get('CHARLIE_LLM_PLANNING', 'true').lower() in ('1', 'true', 'yes'),
        "use_llm_for_conversation": os.environ.get('CHARLIE_LLM_CONVERSATION', 'true').lower() in ('1', 'true', 'yes'),
        "use_llm_for_reflection": os.environ.get('CHARLIE_LLM_REFLECTION', 'true').lower() in ('1', 'true', 'yes'),
    },
    
    # 全局默认设置
    "default": {
        "provider": LLM_CONFIG["default_provider"],
        "use_llm_for_planning": True,
        "use_llm_for_conversation": True, 
        "use_llm_for_reflection": True,
    }
}

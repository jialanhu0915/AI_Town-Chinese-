"""
AI Town 配置加载器
自动从 .env 文件加载配置，支持运行时配置修改
"""

import os
from pathlib import Path
from typing import Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def load_env_file(env_path: Path = None) -> Dict[str, str]:
    """加载 .env 文件"""
    if env_path is None:
        env_path = PROJECT_ROOT / ".env"
    
    config = {}
    
    if not env_path.exists():
        print(f"警告: 配置文件 {env_path} 不存在，使用默认配置")
        return config
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                
                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    config[key] = value
                    
                    # 同时设置到环境变量中
                    os.environ[key] = value
                    
        print(f"✅ 成功加载配置文件: {env_path}")
        print(f"📋 加载了 {len(config)} 项配置")
        
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
    
    return config

def get_llm_config_for_agent(agent_name: str) -> Dict[str, Any]:
    """获取指定智能体的 LLM 配置"""
    try:
        from ai_town.config import LLM_CONFIG, AGENT_LLM_CONFIG
    except ImportError:
        import sys
        sys.path.append(str(PROJECT_ROOT))
        from ai_town.config import LLM_CONFIG, AGENT_LLM_CONFIG
    
    # 获取智能体特定配置，如果不存在则使用默认配置
    agent_config = AGENT_LLM_CONFIG.get(agent_name, AGENT_LLM_CONFIG["default"])
    
    return {
        "provider": agent_config["provider"],
        "use_llm_for_planning": agent_config["use_llm_for_planning"],
        "use_llm_for_conversation": agent_config["use_llm_for_conversation"],
        "use_llm_for_reflection": agent_config["use_llm_for_reflection"],
        "provider_config": LLM_CONFIG.get(agent_config["provider"], {})
    }

def get_current_llm_model() -> str:
    """获取当前配置的 LLM 模型"""
    return os.environ.get('OLLAMA_MODEL', 'deepseek-r1:1.5b')

def switch_llm_model(model_name: str):
    """快速切换 LLM 模型"""
    os.environ['OLLAMA_MODEL'] = model_name
    print(f"✅ LLM 模型已切换为: {model_name}")

def show_current_config():
    """显示当前 LLM 配置"""
    try:
        from ai_town.config import LLM_CONFIG, AGENT_LLM_CONFIG
    except ImportError:
        import sys
        sys.path.append(str(PROJECT_ROOT))
        from ai_town.config import LLM_CONFIG, AGENT_LLM_CONFIG
    
    print("🔧 当前 AI Town LLM 配置:")
    print("=" * 50)
    
    print(f"默认提供商: {LLM_CONFIG['default_provider']}")
    print(f"Ollama 模型: {get_current_llm_model()}")
    print(f"故障转移链: {' -> '.join(LLM_CONFIG['fallback_chain'])}")
    
    print("\n📋 智能体配置:")
    for agent_name, config in AGENT_LLM_CONFIG.items():
        if agent_name != "default":
            print(f"  {agent_name}: {config['provider']}")

# 自动加载配置
def initialize_config():
    """初始化配置系统"""
    print("🚀 正在初始化 AI Town 配置...")
    load_env_file()
    show_current_config()

if __name__ == "__main__":
    initialize_config()

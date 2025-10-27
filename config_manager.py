"""
AI Town 配置管理工具
快速切换 LLM 模型和配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def show_available_models():
    """显示可用的模型"""
    print("🤖 可用的 LLM 模型:")
    print("=" * 40)
    
    models = {
        "deepseek-r1:1.5b": "DeepSeek-R1 1.5B (推荐) - 平衡效果和速度",
        "tinyllama": "TinyLlama (轻量) - 最低资源消耗",
        "deepseek-r1:8b": "DeepSeek-R1 8B (高效) - 更好效果，需要更多资源",
        "qwen:7b-chat": "Qwen 7B (中文) - 阿里巴巴，中文友好",
        "phi3.5:mini": "Phi-3.5 Mini - Microsoft，轻量高效",
        "mistral:7b": "Mistral 7B - 欧洲模型，平衡性能"
    }
    
    for i, (model, desc) in enumerate(models.items(), 1):
        print(f"  {i}. {model} - {desc}")
    
    return list(models.keys())

def switch_model():
    """交互式切换模型"""
    models = show_available_models()
    
    print(f"\n当前模型: {os.environ.get('OLLAMA_MODEL', 'deepseek-r1:1.5b')}")
    
    try:
        choice = input("\n请选择模型 (输入数字 1-6): ").strip()
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(models):
            selected_model = models[choice_idx]
            
            # 更新 .env 文件
            env_path = project_root / ".env"
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换模型配置
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    if line.startswith('OLLAMA_MODEL='):
                        new_lines.append(f'OLLAMA_MODEL={selected_model}')
                    else:
                        new_lines.append(line)
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                
                print(f"✅ 已切换到模型: {selected_model}")
                print("💡 重新启动 AI Town 以应用新配置")
            else:
                print("❌ 配置文件 .env 不存在")
        else:
            print("❌ 无效选择")
    
    except (ValueError, KeyboardInterrupt):
        print("❌ 取消操作")

def show_current_config():
    """显示当前配置"""
    from ai_town.config_loader import initialize_config
    initialize_config()

def create_custom_config():
    """创建自定义配置"""
    print("🛠️  自定义 AI Town 配置")
    print("=" * 40)
    
    # 选择默认提供商
    providers = ["ollama", "openai", "mock"]
    print("LLM 提供商:")
    for i, provider in enumerate(providers, 1):
        print(f"  {i}. {provider}")
    
    try:
        provider_choice = input("选择默认提供商 (1-3): ").strip()
        provider_idx = int(provider_choice) - 1
        
        if 0 <= provider_idx < len(providers):
            selected_provider = providers[provider_idx]
            
            # 更新 .env 文件
            env_path = project_root / ".env"
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换提供商配置
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    if line.startswith('AI_TOWN_LLM_PROVIDER='):
                        new_lines.append(f'AI_TOWN_LLM_PROVIDER={selected_provider}')
                    else:
                        new_lines.append(line)
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                
                print(f"✅ 默认提供商已设置为: {selected_provider}")
        
        if selected_provider == "ollama":
            switch_model()
            
    except (ValueError, KeyboardInterrupt):
        print("❌ 取消操作")

def main():
    """主菜单"""
    while True:
        print("\n🏘️  AI Town 配置管理")
        print("=" * 30)
        print("1. 查看当前配置")
        print("2. 切换 LLM 模型")
        print("3. 自定义配置")
        print("4. 退出")
        
        try:
            choice = input("\n请选择操作 (1-4): ").strip()
            
            if choice == "1":
                show_current_config()
            elif choice == "2":
                switch_model()
            elif choice == "3":
                create_custom_config()
            elif choice == "4":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 1-4")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break

if __name__ == "__main__":
    main()

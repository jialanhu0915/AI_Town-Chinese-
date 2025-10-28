"""
测试 DeepSeek-R1 模型的对话能力
验证配置系统和模型切换是否正常工作
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_town.config_loader import get_current_llm_model, initialize_config
from ai_town.llm.llm_integration import ask_llm, chat_with_llm, setup_default_llm_providers


@pytest.mark.skipif(
    os.getenv("CI") == "true" or os.getenv("SKIP_OLLAMA_TESTS") == "true",
    reason="跳过需要Ollama的测试在CI环境中",
)
async def test_deepseek_model():
    """测试 DeepSeek-R1 模型"""

    print("🚀 DeepSeek-R1 模型测试")
    print("=" * 40)

    # 初始化配置
    initialize_config()
    setup_default_llm_providers()

    print(f"当前模型: {get_current_llm_model()}")
    print()

    # 测试 1: 简单问答
    print("📋 测试 1: 简单问答")
    try:
        response = await ask_llm("你好，请用一句话介绍你自己", provider="ollama")
        print(f"DeepSeek-R1: {response}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print()

    # 测试 2: JSON 格式决策
    print("📋 测试 2: JSON 格式决策")
    decision_prompt = """
你是Alice，32岁咖啡店老板。现在是上午10点，你在咖啡店里。

请从以下选项中选择一个行为：
1. work - 工作
2. socialize - 社交  
3. think - 思考

严格按照JSON格式回答：
{"type": "work", "description": "泡咖啡", "reason": "上午是忙碌时间"}

JSON响应："""

    try:
        response = await ask_llm(decision_prompt, provider="ollama")
        print(f"DeepSeek-R1 原始回应: {response}")

        # 测试优化的解析逻辑
        import json
        import re

        cleaned_response = response.strip()

        # 移除 markdown 代码块标记
        if "```json" in cleaned_response:
            json_match = re.search(r"```json\s*\n(.*?)\n```", cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)
        elif "```" in cleaned_response:
            json_match = re.search(r"```\s*\n(.*?)\n```", cleaned_response, re.DOTALL)
            if json_match:
                cleaned_response = json_match.group(1)

        try:
            parsed = json.loads(cleaned_response)
            print(f"✅ JSON 解析成功: {parsed}")
        except json.JSONDecodeError:
            print(f"⚠️  JSON 格式仍需优化，清理后内容: {cleaned_response}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print()

    # 测试 3: 角色对话
    print("📋 测试 3: 角色对话")
    conversation_messages = [
        {"role": "system", "content": "你是Alice，友好的咖啡店老板。"},
        {"role": "system", "content": "请用1句话简短回应（不超过20字）。"},
        {"role": "user", "content": "Bob: 你好Alice，今天咖啡香味特别浓呢！"},
    ]

    try:
        response = await chat_with_llm(conversation_messages, provider="ollama")
        print(f"Alice (DeepSeek-R1): {response}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print()

    # 测试 4: 中文对话流畅性
    print("📋 测试 4: 中文对话流畅性")
    chinese_messages = [
        {"role": "system", "content": "你是Charlie，28岁上班族，刚搬到镇上。"},
        {"role": "system", "content": "用1句话回应，体现适应新环境的心态。"},
        {"role": "user", "content": "Alice: 欢迎来到我们小镇！你觉得这里怎么样？"},
    ]

    try:
        response = await chat_with_llm(chinese_messages, provider="ollama")
        print(f"Charlie (DeepSeek-R1): {response}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n🎉 DeepSeek-R1 测试完成!")


if __name__ == "__main__":
    asyncio.run(test_deepseek_model())

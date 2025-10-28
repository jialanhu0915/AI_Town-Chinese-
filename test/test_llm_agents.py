"""
测试 LLM 增强智能体的功能
验证 Alice、Bob、Charlie 是否正确升级为 LLM 驱动的智能体
"""

import asyncio
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ai_town.agents.base_agent import Observation, Position
from ai_town.agents.characters.alice import Alice
from ai_town.agents.characters.bob import Bob
from ai_town.agents.characters.charlie import Charlie
from ai_town.core.time_manager import GameTime
from ai_town.llm.llm_integration import llm_manager, setup_default_llm_providers


@pytest.mark.asyncio
async def test_llm_agents():
    """测试 LLM 增强智能体"""

    print("🤖 测试 LLM 增强智能体系统")
    print("=" * 50)

    # 初始化时间系统
    GameTime.initialize()

    # 设置默认 LLM 提供者
    setup_default_llm_providers()

    # 创建智能体
    print("🏗️  创建智能体...")
    alice = Alice()
    bob = Bob()
    charlie = Charlie()

    agents = [alice, bob, charlie]

    # 测试 1: 验证智能体类型
    print("\n📋 测试 1: 验证智能体类型")
    for agent in agents:
        agent_type = type(agent).__name__
        base_type = type(agent).__bases__[0].__name__
        print(f"   ✅ {agent.name}: {agent_type} (继承自 {base_type})")

        # 检查 LLM 配置
        print(f"      - LLM 提供商: {agent.preferred_llm_provider}")
        print(f"      - 使用 LLM 规划: {agent.use_llm_for_planning}")
        print(f"      - 使用 LLM 对话: {agent.use_llm_for_conversation}")
        print(f"      - 使用 LLM 反思: {agent.use_llm_for_reflection}")

    # 测试 2: 测试决策能力
    print("\n🎯 测试 2: 测试 LLM 决策能力")
    for agent in agents:
        try:
            print(f"\n   测试 {agent.name} 的决策...")
            action = await agent.decide_next_action()
            print(f"   ✅ {agent.name} 决策: {action}")
        except Exception as e:
            print(f"   ❌ {agent.name} 决策失败: {e}")

    # 测试 3: 测试对话能力
    print("\n💬 测试 3: 测试对话能力")

    try:
        # Alice 和 Bob 对话
        print("\n   Alice 与 Bob 的对话:")
        alice_greeting = await alice.start_conversation("Bob", "书店")
        print(f"   Alice: {alice_greeting}")

        bob_response = await bob.respond_to_conversation("Alice", alice_greeting)
        print(f"   Bob: {bob_response}")

        # Charlie 加入对话
        print("\n   Charlie 与 Alice 的对话:")
        charlie_greeting = await charlie.start_conversation("Alice", "新环境")
        print(f"   Charlie: {charlie_greeting}")

        alice_response = await alice.respond_to_conversation("Charlie", charlie_greeting)
        print(f"   Alice: {alice_response}")

        print("   ✅ 对话测试成功")

    except Exception as e:
        print(f"   ❌ 对话测试失败: {e}")

    # 测试 4: 测试记忆和洞察
    print("\n🧠 测试 4: 测试记忆和洞察生成")

    for agent in agents:
        try:
            # 添加一些测试记忆
            test_memories = [
                Observation(
                    GameTime.now(), agent.agent_id, "social", "与朋友聊天", Position(0, 0, "test")
                ),
                Observation(
                    GameTime.now(), agent.agent_id, "work", "在咖啡店工作", Position(0, 0, "test")
                ),
                Observation(
                    GameTime.now(),
                    agent.agent_id,
                    "exploration",
                    "探索新地方",
                    Position(0, 0, "test"),
                ),
            ]

            for memory in test_memories:
                agent.memory.add_observation(memory)

            # 生成洞察
            insights = await agent._generate_insights(agent.memory.get_recent_memories(5))
            print(f"   ✅ {agent.name} 的洞察: {insights}")

        except Exception as e:
            print(f"   ❌ {agent.name} 洞察生成失败: {e}")

    # 测试 5: 验证 LLM 后端状态
    print("\n🔧 测试 5: LLM 后端状态")

    available_providers = llm_manager.get_available_providers()
    print(f"   可用的 LLM 提供商: {available_providers}")

    # 测试每个提供商
    for provider in available_providers:
        try:
            # 发送简单的测试请求
            test_response = await llm_manager.generate("hello", provider_name=provider)
            if test_response.content and not test_response.content.startswith("[LLM Error"):
                print(f"   {provider}: ✅ 正常 - '{test_response.content[:30]}...'")
            else:
                print(f"   {provider}: ⚠️  异常 - {test_response.content}")
        except Exception as e:
            print(f"   {provider}: ❌ 错误 - {e}")

    print("\n🎉 LLM 智能体测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_llm_agents())

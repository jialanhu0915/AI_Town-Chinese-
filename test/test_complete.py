#!/usr/bin/env python3
"""
AI Town 完整系统测试
测试所有智能体和核心功能
"""

import asyncio
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

print("🧪 AI 小镇完整系统测试")
print("=" * 60)


@pytest.mark.asyncio
async def test_all_agents():
    """测试所有智能体创建和基本功能"""
    print("\n📋 测试智能体系统...")

    try:
        from ai_town.agents.agent_manager import agent_manager
        from ai_town.core.time_manager import GameTime
        from ai_town.core.world import World

        # 初始化游戏时间
        GameTime.initialize(time_multiplier=5.0)
        print(f"✅ 游戏时间系统初始化成功")

        # 创建世界
        world = World()
        print(f"✅ 世界创建成功: {world.map.width}x{world.map.height}")

        # 测试所有可用智能体类型
        available_agents = agent_manager.registry.get_available_agents()
        print(f"✅ 发现 {len(available_agents)} 种智能体类型: {available_agents}")

        # 创建所有默认智能体
        created_agents = agent_manager.create_default_agents()
        print(f"✅ 成功创建 {len(created_agents)} 个智能体")

        # 添加到世界并测试
        for agent in created_agents:
            world.add_agent(agent)
            print(f"   - {agent.name} ({agent.age}岁) - {agent.occupation}")
            print(f"     位置: ({agent.position.x}, {agent.position.y}) 在 {agent.position.area}")
            print(f"     背景: {agent.background[:60]}...")

        print(f"✅ 所有智能体已添加到世界，总数: {len(world.agents)}")

        # 测试智能体行为决策
        print(f"\n🎭 测试智能体行为决策...")
        for agent_id, agent in world.agents.items():
            try:
                action = await agent._decide_next_action()
                print(
                    f'   - {agent.name}: {action.get("type", "unknown")} - {action.get("description", action.get("reason", ""))}'
                )
            except Exception as e:
                pytest.fail(f"{agent.name} 行为决策失败: {e}")

        # 运行几步模拟
        print(f"\n⏩ 运行模拟测试（3步）...")
        for step in range(3):
            step_results = await world.step()
            active_actions = sum(
                1 for result in step_results.values() if result.get("type") != "idle"
            )
            print(
                f"   第 {step + 1} 步: {active_actions} 个活跃行动，{len(world.current_events)} 个事件"
            )

        print(f"✅ 模拟系统运行正常")

    except Exception as e:
        pytest.fail(f"智能体系统测试失败: {e}")


@pytest.mark.asyncio
async def test_visualization_components():
    """测试可视化组件"""
    print(f"\n🎨 测试可视化组件...")

    try:
        # 测试可视化服务器导入
        from ai_town.ui.visualization_server import VisualizationManager

        print(f"✅ 可视化服务器组件导入成功")

        # 创建管理器并初始化世界
        manager = VisualizationManager()
        await manager.initialize_world()

        assert manager.world is not None, "可视化管理器应该有world对象"
        assert len(manager.world.agents) > 0, "世界应该有智能体"
        print(f"✅ 可视化管理器世界初始化成功，{len(manager.world.agents)} 个智能体")

        # 测试世界状态获取
        world_state = manager.world.get_world_state()
        required_keys = ["current_time", "agent_positions", "map_data"]

        for key in required_keys:
            assert key in world_state, f"世界状态应该包含 {key}"
            print(f"   ✅ 世界状态包含 {key}")

        print(f"✅ 可视化组件测试通过")

    except Exception as e:
        pytest.fail(f"可视化组件测试失败: {e}")


def test_project_structure():
    """测试项目结构完整性"""
    print(f"\n📁 测试项目结构完整性...")

    required_files = [
        "ai_town/agents/characters/alice.py",
        "ai_town/agents/characters/bob.py",
        "ai_town/agents/characters/charlie.py",
        "ai_town/agents/agent_manager.py",
        "ai_town/core/world.py",
        "ai_town/core/time_manager.py",
        "ai_town/environment/map.py",
        "ai_town/ui/visualization_server.py",
        "ai_town/ui/templates/index.html",
        "ai_town/ui/templates/visualization.js",
        "ai_town/simulation_runner.py",
        "run_ai_town.bat",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - 缺失")
            missing_files.append(file_path)

    assert len(missing_files) == 0, f"项目结构不完整，缺失 {len(missing_files)} 个文件: {missing_files}"
    print(f"✅ 项目结构完整，所有必需文件都存在")


def test_extensibility():
    """测试可扩展性"""
    print(f"\n🔧 测试系统可扩展性...")

    try:
        from ai_town.agents.agent_manager import AgentRegistry, register_custom_agent
        from ai_town.agents.base_agent import BaseAgent, Position

        # 创建一个测试智能体类
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    agent_id="test_agent",
                    name="TestAgent",
                    age=25,
                    personality={
                        "extraversion": 0.5,
                        "agreeableness": 0.5,
                        "conscientiousness": 0.5,
                        "neuroticism": 0.5,
                        "openness": 0.5,
                    },
                    background="A test agent for system validation",
                    initial_position=Position(50, 50, "park"),
                    occupation="tester",
                )

            async def _generate_insights(self, memories):
                return ["This is a test insight"]

            async def _decide_next_action(self):
                return {"type": "test", "description": "Testing action"}

        # 注册自定义智能体
        register_custom_agent("test_agent", TestAgent)

        # 验证注册成功
        available_agents = AgentRegistry.get_available_agents()
        assert "test_agent" in available_agents, "自定义智能体应该被成功注册"
        print(f"✅ 自定义智能体注册成功")

        # 测试创建自定义智能体
        from ai_town.agents.agent_manager import agent_manager

        test_agent = agent_manager.create_agent("test_agent")

        assert test_agent is not None, "自定义智能体应该能被创建"
        assert test_agent.name == "TestAgent", "自定义智能体的名字应该正确"
        print(f"✅ 自定义智能体创建成功: {test_agent.name}")

        print(f"✅ 系统可扩展性测试通过")

    except Exception as e:
        pytest.fail(f"可扩展性测试失败: {e}")


async def main():
    """主测试函数"""
    try:
        from ai_town.core.time_manager import GameTime

        GameTime.initialize()
        start_time = GameTime.format_time()
    except:
        start_time = "未初始化"

    print(f"开始时间: {start_time}")

    test_results = []

    # 运行所有测试
    test_results.append(("项目结构", test_project_structure()))
    test_results.append(("智能体系统", await test_all_agents()))
    test_results.append(("可视化组件", await test_visualization_components()))
    test_results.append(("系统扩展性", test_extensibility()))

    # 汇总结果
    print(f"\n📊 测试结果汇总")
    print("=" * 60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:.<30} {status}")
        if result:
            passed_tests += 1

    print(f"\n总体结果: {passed_tests}/{total_tests} 项测试通过")

    if passed_tests == total_tests:
        print(f"🎉 所有测试通过！AI 小镇系统运行正常。")
        print(f"\n🚀 你现在可以：")
        print(f"   1. 运行命令行模拟: python ai_town/simulation_runner.py")
        print(f"   2. 启动可视化界面: python ai_town/ui/visualization_server.py")
        print(f"   3. 使用启动脚本: run_ai_town.bat")
        print(f"   4. 扩展自定义智能体")
        return True
    else:
        print(f"⚠️  系统存在问题，请查看失败的测试项目。")
        return False


if __name__ == "__main__":
    asyncio.run(main())

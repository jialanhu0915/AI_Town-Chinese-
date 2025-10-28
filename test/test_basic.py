#!/usr/bin/env python3
"""
AI Town 基础功能测试
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_gametime_module():
    """测试GameTime模块"""
    from ai_town.core.time_manager import GameTime

    GameTime.initialize(time_multiplier=5.0)
    assert GameTime.format_time() is not None, "GameTime应该能格式化时间"
    assert GameTime.get_time_of_day() is not None, "GameTime应该能获取时段"
    print(f"✅ GameTime 初始化成功: {GameTime.format_time()}")
    print(f"   时段: {GameTime.get_time_of_day()}")


def test_world_creation():
    """测试世界创建"""
    from ai_town.core.world import World

    world = World()
    assert world.map.width > 0, "世界地图应该有宽度"
    assert world.map.height > 0, "世界地图应该有高度"
    assert len(world.map.buildings) > 0, "世界应该有建筑物"
    print(f"✅ 世界创建成功: {world.map.width}x{world.map.height} 地图")
    print(f"   建筑物: {len(world.map.buildings)}")


def test_agent_manager():
    """测试智能体管理器"""
    from ai_town.agents.agent_manager import agent_manager
    from ai_town.core.world import World

    # 测试智能体管理器
    available_agents = agent_manager.registry.get_available_agents()
    assert len(available_agents) > 0, "应该有可用的智能体类型"
    print(f"✅ 智能体管理器测试成功")
    print(f"   可用智能体类型: {available_agents}")

    # 创建测试智能体
    alice = agent_manager.create_agent("alice")
    assert alice is not None, "Alice应该能被创建"
    assert alice.name == "Alice", "Alice的名字应该正确"
    assert alice.age > 0, "Alice应该有年龄"
    print(f"✅ Alice 创建成功: {alice.name}，{alice.age}岁")
    print(f"   位置: ({alice.position.x}, {alice.position.y}) 在 {alice.position.area}")
    print(f"   能量: {alice.energy}，心情: {alice.mood}")

    # 测试添加到世界
    world = World()
    world.add_agent(alice)
    assert len(world.agents) == 1, "世界应该有一个智能体"
    print(f"✅ Alice 已添加到世界。智能体总数: {len(world.agents)}")


if __name__ == "__main__":
    print("🧪 正在测试 AI 小镇基础组件...")
    print("=" * 50)

    pytest.main([__file__, "-v"])

    print()
    print("🎯 基础功能测试完成！")

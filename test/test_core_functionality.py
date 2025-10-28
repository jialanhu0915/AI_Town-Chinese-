"""
核心功能集成测试
快速验证AI Town的主要功能模块
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_core_imports():
    """测试核心模块导入"""
    try:
        from ai_town.events.event_registry import event_registry
        from ai_town.events.event_formatter import event_formatter
        assert event_registry is not None
        assert event_formatter is not None
        print("✅ 核心事件系统导入成功")
    except ImportError as e:
        pytest.fail(f"核心模块导入失败: {e}")


def test_agent_imports():
    """测试智能体模块导入"""
    try:
        from ai_town.agents.base_agent import BaseAgent, Position, AgentState
        from ai_town.agents.characters.alice import Alice
        from ai_town.agents.characters.bob import Bob  
        from ai_town.agents.characters.charlie import Charlie
        
        assert BaseAgent is not None
        assert Position is not None
        assert AgentState is not None
        assert Alice is not None
        assert Bob is not None
        assert Charlie is not None
        print("✅ 智能体模块导入成功")
    except ImportError as e:
        pytest.fail(f"智能体模块导入失败: {e}")


def test_web_server_imports():
    """测试Web服务器模块导入"""
    try:
        from ai_town.ui.visualization_server import app, VisualizationManager
        assert app is not None
        assert VisualizationManager is not None
        print("✅ Web服务器模块导入成功")
    except ImportError as e:
        pytest.fail(f"Web服务器模块导入失败: {e}")


def test_event_system_integration():
    """测试事件系统集成"""
    from ai_town.events.event_registry import event_registry
    from ai_town.events.event_formatter import event_formatter
    
    # 测试事件注册
    all_events = event_registry.get_all_events()
    assert len(all_events) > 0, "应该有注册的事件类型"
    
    # 测试事件格式化
    test_event = {
        'event_type': 'movement',
        'description': 'test movement',
        'participants': ['alice']
    }
    
    formatted = event_formatter.format_event_display(test_event)
    assert 'icon' in formatted, "格式化后应该包含图标"
    assert 'typeLabel' in formatted, "格式化后应该包含类型标签"
    
    print("✅ 事件系统集成测试通过")


def test_agent_creation():
    """测试智能体创建"""
    from ai_town.agents.characters.alice import Alice
    from ai_town.agents.characters.bob import Bob
    from ai_town.agents.characters.charlie import Charlie
    
    # 测试创建智能体
    alice = Alice()
    bob = Bob()
    charlie = Charlie()
    
    assert alice.agent_id == "alice"
    assert bob.agent_id == "bob"  
    assert charlie.agent_id == "charlie"
    
    assert alice.occupation == "coffee_shop_owner"
    assert bob.occupation == "bookstore_owner"
    assert charlie.occupation == "office_worker"
    
    print("✅ 智能体创建测试通过")


def test_behavior_system():
    """测试行为系统"""
    from ai_town.agents.characters.alice import Alice
    from ai_town.agents.characters.bob import Bob
    
    alice = Alice()
    bob = Bob()
    
    # 测试Alice的行为配置
    alice_behaviors = alice.available_behaviors
    assert 'coffee_making' in alice_behaviors, "Alice应该有制作咖啡的行为"
    assert 'greet_customer' in alice_behaviors, "Alice应该有迎接顾客的行为"
    
    # 测试Bob的行为配置
    bob_behaviors = bob.available_behaviors
    assert 'read' in bob_behaviors, "Bob应该有阅读行为"
    assert 'organizing_books' in bob_behaviors, "Bob应该有整理书籍的行为"
    
    # 测试行为偏好
    alice_preferences = alice.behavior_preferences
    bob_preferences = bob.behavior_preferences
    
    # Alice更外向，应该更喜欢社交
    # Bob更内向，应该更喜欢阅读和反思
    assert alice_preferences.get('socialize', 0) > bob_preferences.get('socialize', 0)
    assert bob_preferences.get('read', 0) > alice_preferences.get('read', 0)
    
    print("✅ 行为系统测试通过")


if __name__ == "__main__":
    print("🚀 运行核心功能测试")
    print("=" * 50)
    
    tests = [
        test_core_imports,
        test_agent_imports, 
        test_web_server_imports,
        test_event_system_integration,
        test_agent_creation,
        test_behavior_system
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 失败: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有核心功能测试通过！")
        exit(0)
    else:
        print("💥 有测试失败，请检查问题")
        exit(1)

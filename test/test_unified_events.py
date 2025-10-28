"""
统一事件系统测试
验证事件注册表和格式化器的功能
"""

from ai_town.events.event_registry import event_registry
from ai_town.events.event_formatter import event_formatter


def test_event_registry():
    """测试事件注册表功能"""
    print("🧪 测试事件注册表...")
    
    # 测试获取事件元数据
    metadata = event_registry.get_event_metadata("coffee_making")
    assert metadata is not None, "应该能获取到咖啡制作事件元数据"
    assert metadata.icon == "☕", f"咖啡制作事件图标应该是☕，实际是{metadata.icon}"
    
    # 测试按分类获取事件
    work_events = event_registry.get_events_by_category(metadata.category)
    assert "coffee_making" in work_events, "咖啡制作应该在工作类事件中"
    
    # 测试按标签获取事件
    alice_events = event_registry.get_events_by_tags(["alice"])
    alice_event_ids = list(alice_events.keys())
    assert "coffee_making" in alice_event_ids, "咖啡制作应该有alice标签"
    
    print("✅ 事件注册表测试通过")


def test_event_formatter():
    """测试事件格式化器功能"""
    print("🧪 测试事件格式化器...")
    
    # 测试咖啡制作事件格式化
    event_data = {
        'event_type': 'coffee_making',
        'description': 'Alice is making espresso',
        'participants': ['alice'],
        'coffee_type': 'Espresso'
    }
    
    formatted = event_formatter.format_event_display(event_data)
    
    assert formatted['icon'] == "☕", f"格式化后图标应该是☕，实际是{formatted['icon']}"
    assert "Alice" in formatted['description'], "描述中应该包含Alice"
    assert "Espresso" in formatted['description'], "描述中应该包含Espresso"
    assert formatted['typeLabel'] == "制作咖啡", f"类型标签应该是'制作咖啡'，实际是{formatted['typeLabel']}"
    
    # 测试移动事件格式化
    move_event = {
        'event_type': 'movement',
        'description': 'alice moved from coffee_shop to park',
        'participants': ['alice']
    }
    
    formatted_move = event_formatter.format_event_display(move_event)
    assert "咖啡店" in formatted_move['description'], "移动描述应该包含中文地点名称"
    assert "公园" in formatted_move['description'], "移动描述应该包含中文地点名称"
    
    print("✅ 事件格式化器测试通过")


def test_frontend_metadata():
    """测试前端元数据生成"""
    print("🧪 测试前端元数据...")
    
    frontend_data = event_formatter.get_all_event_types_for_frontend()
    
    assert "coffee_making" in frontend_data, "前端数据应该包含咖啡制作事件"
    coffee_data = frontend_data["coffee_making"]
    
    assert coffee_data['icon'] == "☕", "前端数据中图标应该正确"
    assert coffee_data['displayName'] == "制作咖啡", "前端数据中显示名称应该正确"
    assert coffee_data['category'] == "work", "前端数据中分类应该正确"
    assert "alice" in coffee_data['tags'], "前端数据中标签应该包含alice"
    
    print("✅ 前端元数据测试通过")


def main():
    """运行所有测试"""
    print("🚀 开始统一事件系统测试")
    print("=" * 50)
    
    try:
        test_event_registry()
        test_event_formatter() 
        test_frontend_metadata()
        
        print("=" * 50)
        print("🎉 所有测试通过！统一事件系统工作正常")
        
        # 显示一些统计信息
        all_events = event_registry.get_all_events()
        print(f"\n📊 系统统计:")
        print(f"   总事件类型数: {len(all_events)}")
        
        from ai_town.events.event_registry import EventCategory
        for category in EventCategory:
            category_events = event_registry.get_events_by_category(category)
            print(f"   {category.value}: {len(category_events)} 个事件")
        
        # 显示每个角色的专属事件
        for agent in ['alice', 'bob', 'charlie']:
            agent_events = event_registry.get_events_by_tags([agent])
            print(f"   {agent}: {len(agent_events)} 个专属事件")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AI Town 基础功能测试
"""

print('🧪 正在测试 AI 小镇基础组件...')
print('=' * 50)

try:
    from ai_town.core.time_manager import GameTime
    print('✅ GameTime 模块导入成功')
    
    GameTime.initialize(time_multiplier=5.0)
    print(f'✅ GameTime 初始化成功: {GameTime.format_time()}')
    print(f'   时段: {GameTime.get_time_of_day()}')
    
except Exception as e:
    print(f'❌ GameTime 测试失败: {e}')

try:
    from ai_town.core.world import World
    world = World()
    print(f'✅ 世界创建成功: {world.map.width}x{world.map.height} 地图')
    print(f'   建筑物: {len(world.map.buildings)}')
    
except Exception as e:
    print(f'❌ 世界测试失败: {e}')

try:
    from ai_town.agents.agent_manager import agent_manager
    
    # 测试智能体管理器
    available_agents = agent_manager.registry.get_available_agents()
    print(f'✅ 智能体管理器测试成功')
    print(f'   可用智能体类型: {available_agents}')
    
    # 创建测试智能体
    alice = agent_manager.create_agent('alice')
    if alice:
        print(f'✅ Alice 创建成功: {alice.name}，{alice.age}岁')
        print(f'   位置: ({alice.position.x}, {alice.position.y}) 在 {alice.position.area}')
        print(f'   能量: {alice.energy}，心情: {alice.mood}')
        
        world.add_agent(alice)
        print(f'✅ Alice 已添加到世界。智能体总数: {len(world.agents)}')
    else:
        print('❌ Alice 创建失败')
    
except Exception as e:
    print(f'❌ 智能体测试失败: {e}')
    import traceback
    traceback.print_exc()

print()
print('🎯 基础功能测试完成！')

#!/usr/bin/env python3
"""
AI Town 基础功能测试
"""

print('🧪 Testing AI Town Basic Components...')
print('=' * 50)

try:
    from ai_town.core.time_manager import GameTime
    print('✅ GameTime imported successfully')
    
    GameTime.initialize(time_multiplier=5.0)
    print(f'✅ GameTime initialized: {GameTime.format_time()}')
    print(f'   Time of day: {GameTime.get_time_of_day()}')
    
except Exception as e:
    print(f'❌ GameTime test failed: {e}')

try:
    from ai_town.core.world import World
    world = World()
    print(f'✅ World created: {world.map.width}x{world.map.height} map')
    print(f'   Buildings: {len(world.map.buildings)}')
    
except Exception as e:
    print(f'❌ World test failed: {e}')

try:
    from ai_town.agents.characters.alice import Alice
    alice = Alice()
    print(f'✅ Alice created: {alice.name}, Age {alice.age}')
    print(f'   Position: ({alice.position.x}, {alice.position.y}) in {alice.position.area}')
    print(f'   Energy: {alice.energy}, Mood: {alice.mood}')
    
    world.add_agent(alice)
    print(f'✅ Alice added to world. Total agents: {len(world.agents)}')
    
except Exception as e:
    print(f'❌ Alice test failed: {e}')
    import traceback
    traceback.print_exc()

print()
print('🎯 Basic functionality test completed!')

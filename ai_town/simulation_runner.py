"""
AI Town 模拟启动器
创建智能体并启动模拟
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ai_town.agents.agent_manager import agent_manager
from ai_town.core.time_manager import GameTime
from ai_town.core.world import World


async def main():
    """主函数"""
    print("🏘️ 欢迎来到 AI 小镇！")
    print("=" * 50)
    
    # 初始化游戏时间
    GameTime.initialize(time_multiplier=10.0)  # 10倍速度
    print(f"⏰ 游戏时间初始化: {GameTime.format_time()}")
    print(f"🔄 时间倍率: 10x (现实1分钟 = 游戏10分钟)")
    
    # 创建世界
    world = World()
    print(f"🗺️  世界已创建，地图大小: {world.map.width}x{world.map.height}")
    
    # 创建智能体
    print("\n👥 正在创建智能体...")
    
    # 使用智能体管理器创建默认智能体
    created_agents = agent_manager.create_default_agents()
    
    # 添加智能体到世界
    for agent in created_agents:
        world.add_agent(agent)
    
    print(f"✅ 已添加 {len(world.agents)} 个智能体:")
    for agent_id, agent in world.agents.items():
        print(f"   - {agent.name} ({agent.age}岁): {agent.background[:50]}...")
    
    # 显示初始世界状态
    print(f"\n🌍 初始世界状态:")
    world_state = world.get_world_state()
    print(f"   - 时间: {world_state['current_time']} ({world_state['time_of_day']})")
    print(f"   - 活跃智能体: {len(world_state['agent_positions'])}")
    print(f"   - 建筑物: {len(world_state['map_data']['buildings'])}")
    
    # 选择运行模式
    print(f"\n🚀 选择模拟模式:")
    print("1. 运行指定时长")
    print("2. 逐步控制运行")
    print("3. 连续运行 (按 Ctrl+C 停止)")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1":
            duration = int(input("请输入运行时长(分钟): "))
            await world.run_simulation(duration_minutes=duration)
            
        elif choice == "2":
            print("\n⏯️  逐步模式。按回车进行下一步，输入 'q' 退出:")
            step = 0
            while True:
                user_input = input(f"第 {step} 步 > ").strip().lower()
                if user_input in ['q', 'quit', 'exit', '退出']:
                    break
                
                step_results = await world.step()
                
                # 显示步骤结果
                print(f"\n📊 第 {world.step_count} 步结果:")
                for agent_id, result in step_results.items():
                    action_type = result.get('type', 'unknown')
                    agent = world.agents[agent_id]
                    print(f"   {agent.name}: {action_type}")
                    if result.get('description'):
                        print(f"      └─ {result['description']}")
                
                # 显示当前事件
                if world.current_events:
                    print(f"\n📰 当前事件 ({len(world.current_events)}):")
                    for event in world.current_events[-3:]:  # 显示最近3个事件
                        print(f"   • {event.description}")
                
                step += 1
                
        elif choice == "3":
            await world.run_simulation()
            
        else:
            print("无效选择")
            return
            
    except KeyboardInterrupt:
        print(f"\n⏹️ 模拟已中断")
        world.stop_simulation()
    
    # 显示最终统计
    print(f"\n📈 最终统计:")
    stats = world.get_simulation_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"      {sub_key}: {sub_value}")
        else:
            print(f"   {key}: {value}")
    
    # 保存世界状态
    output_file = f"simulation_result_{GameTime.now().strftime('%Y%m%d_%H%M%S')}.json"
    world.save_world_state(output_file)
    print(f"\n💾 世界状态已保存至: {output_file}")
    
    print(f"\n🎉 感谢访问 AI 小镇！")


if __name__ == "__main__":
    asyncio.run(main())

"""
AI Town 模拟启动器
创建智能体并启动模拟
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ai_town.core.world import World
from ai_town.core.time_manager import GameTime
from ai_town.agents.characters.alice import Alice
from ai_town.agents.base_agent import Position


def create_bob():
    """创建 Bob 角色 - 书店老板"""
    from ai_town.agents.base_agent import BaseAgent
    
    class Bob(BaseAgent):
        def __init__(self):
            personality = {
                'extraversion': 0.4,      # 较内向
                'agreeableness': 0.8,     # 友善
                'conscientiousness': 0.9, # 认真负责
                'neuroticism': 0.3,       # 稳定
                'openness': 0.8          # 开放
            }
            
            background = (
                "Bob is a quiet and thoughtful bookstore owner in his late 40s. "
                "He's been running the local bookstore for over 15 years and knows "
                "everything about books and literature. Bob enjoys deep conversations "
                "about philosophy, history, and science. He's a bit introverted but "
                "very knowledgeable and helpful to customers."
            )
            
            super().__init__(
                agent_id="bob",
                name="Bob",
                age=47,
                personality=personality,
                background=background,
                initial_position=Position(35, 20, "bookstore"),
                occupation="bookstore_owner",
                work_area="bookstore"
            )
        
        async def _generate_insights(self, memories):
            insights = []
            
            # 分析读书相关的记忆
            book_memories = [m for m in memories 
                           if any(word in m.description.lower() 
                                 for word in ['book', 'read', 'story', 'novel'])]
            
            if len(book_memories) >= 3:
                insights.append(
                    "I've been thinking about the books that customers are interested in lately. "
                    "There seems to be a growing interest in science fiction."
                )
            
            # 分析客户互动
            customer_memories = [m for m in memories 
                               if 'customer' in m.description.lower()]
            
            if len(customer_memories) >= 2:
                insights.append(
                    "The bookstore is becoming more than just a place to buy books. "
                    "People come here to discuss ideas and find intellectual connection."
                )
            
            return insights[:2]
    
    return Bob()


def create_charlie():
    """创建 Charlie 角色 - 办公室职员"""
    from ai_town.agents.base_agent import BaseAgent
    
    class Charlie(BaseAgent):
        def __init__(self):
            personality = {
                'extraversion': 0.6,      # 适度外向
                'agreeableness': 0.7,     # 友善
                'conscientiousness': 0.8, # 负责任
                'neuroticism': 0.4,       # 略有压力
                'openness': 0.5          # 中等开放性
            }
            
            background = (
                "Charlie is a 28-year-old office worker who moved to town recently "
                "for a new job. He's still getting to know people and exploring "
                "the community. Charlie is hardworking and ambitious, but also "
                "values work-life balance. He enjoys meeting new people and "
                "discovering what the town has to offer."
            )
            
            super().__init__(
                agent_id="charlie",
                name="Charlie",
                age=28,
                personality=personality,
                background=background,
                initial_position=Position(60, 30, "office_1"),
                occupation="office_worker",
                work_area="office_1"
            )
        
        async def _generate_insights(self, memories):
            insights = []
            
            # 分析工作记忆
            work_memories = [m for m in memories 
                           if 'work' in m.description.lower() or 'office' in m.description.lower()]
            
            if len(work_memories) >= 3:
                insights.append(
                    "I'm starting to get into a good routine at work. "
                    "The office environment here is quite different from my previous job."
                )
            
            # 分析新环境适应
            social_memories = [m for m in memories 
                             if any(word in m.description.lower() 
                                   for word in ['meet', 'talk', 'conversation'])]
            
            if len(social_memories) >= 2:
                insights.append(
                    "I'm gradually getting to know more people in town. "
                    "Everyone seems quite friendly and welcoming."
                )
            
            return insights[:2]
    
    return Charlie()


async def main():
    """主函数"""
    print("🏘️ Welcome to AI Town!")
    print("=" * 50)
    
    # 初始化游戏时间
    GameTime.initialize(time_multiplier=10.0)  # 10倍速度
    print(f"⏰ Game time initialized: {GameTime.format_time()}")
    print(f"🔄 Time multiplier: 10x (1 real minute = 10 game minutes)")
    
    # 创建世界
    world = World()
    print(f"🗺️  World created with {world.map.width}x{world.map.height} map")
    
    # 创建智能体
    print("\n👥 Creating agents...")
    
    alice = Alice()
    bob = create_bob()
    charlie = create_charlie()
    
    # 添加智能体到世界
    world.add_agent(alice)
    world.add_agent(bob) 
    world.add_agent(charlie)
    
    print(f"✅ Added {len(world.agents)} agents:")
    for agent_id, agent in world.agents.items():
        print(f"   - {agent.name} ({agent.age}): {agent.background[:50]}...")
    
    # 显示初始世界状态
    print(f"\n🌍 Initial world state:")
    world_state = world.get_world_state()
    print(f"   - Time: {world_state['current_time']} ({world_state['time_of_day']})")
    print(f"   - Active agents: {len(world_state['agent_positions'])}")
    print(f"   - Buildings: {len(world_state['map_data']['buildings'])}")
    
    # 选择运行模式
    print(f"\n🚀 Choose simulation mode:")
    print("1. Run for specific duration")
    print("2. Run with step-by-step control")
    print("3. Run continuously (Ctrl+C to stop)")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            duration = int(input("Enter duration in minutes: "))
            await world.run_simulation(duration_minutes=duration)
            
        elif choice == "2":
            print("\n⏯️  Step-by-step mode. Press Enter for next step, 'q' to quit:")
            step = 0
            while True:
                user_input = input(f"Step {step} > ").strip().lower()
                if user_input in ['q', 'quit', 'exit']:
                    break
                
                step_results = await world.step()
                
                # 显示步骤结果
                print(f"\n📊 Step {world.step_count} results:")
                for agent_id, result in step_results.items():
                    action_type = result.get('type', 'unknown')
                    agent = world.agents[agent_id]
                    print(f"   {agent.name}: {action_type}")
                    if result.get('description'):
                        print(f"      └─ {result['description']}")
                
                # 显示当前事件
                if world.current_events:
                    print(f"\n📰 Current events ({len(world.current_events)}):")
                    for event in world.current_events[-3:]:  # 显示最近3个事件
                        print(f"   • {event.description}")
                
                step += 1
                
        elif choice == "3":
            await world.run_simulation()
            
        else:
            print("Invalid choice")
            return
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Simulation interrupted")
        world.stop_simulation()
    
    # 显示最终统计
    print(f"\n📈 Final Statistics:")
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
    print(f"\n💾 World state saved to: {output_file}")
    
    print(f"\n🎉 Thank you for visiting AI Town!")


if __name__ == "__main__":
    asyncio.run(main())

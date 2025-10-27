"""
Alice - 示例智能体角色
一个友好的咖啡店老板
"""

from ai_town.agents.base_agent import BaseAgent, Position
from ai_town.core.time_manager import GameTime
from typing import List, Dict, Any
import asyncio
import random


class Alice(BaseAgent):
    """
    Alice - 咖啡店老板
    
    性格特点：
    - 友好外向
    - 喜欢与人交流
    - 关心他人
    - 工作勤奋
    """
    
    def __init__(self):
        personality = {
            'extraversion': 0.8,      # 外向性
            'agreeableness': 0.9,     # 宜人性  
            'conscientiousness': 0.7, # 尽责性
            'neuroticism': 0.2,       # 神经质
            'openness': 0.6          # 开放性
        }
        
        background = (
            "Alice 是一位温暖友好的咖啡店老板，今年32岁。"
            "她5年前搬到这个小镇，开了她梦想中的咖啡店。"
            "Alice 喜欢结识新朋友，让每个人都感到宾至如归。"
            "她以出色的咖啡和记住每个人最爱的订单而闻名。"
            "闲暇时，她喜欢读书和尝试新的咖啡配方。"
        )
        
        super().__init__(
            agent_id="alice",
            name="Alice",
            age=32,
            personality=personality,
            background=background,
            initial_position=Position(25, 25, "coffee_shop"),
            occupation="coffee_shop_owner",
            work_area="coffee_shop"
        )
        
        # Alice 特定的属性
        self.favorite_topics = ['coffee', 'books', 'travel', 'food', 'community']
        self.regular_customers = []
        self.coffee_knowledge = 8.5  # 1-10 scale
        
    async def _generate_insights(self, memories: List) -> List[str]:
        """生成 Alice 特有的洞察"""
        insights = []
        
        # 分析客户模式
        customer_memories = [m for m in memories 
                           if 'customer' in m.description.lower() or 
                              'coffee' in m.description.lower()]
        
        if len(customer_memories) >= 3:
            insights.append(
                "I've been noticing more customers are interested in specialty coffee. "
                "Maybe I should consider expanding my menu with more unique blends."
            )
        
        # 分析社交互动
        social_memories = [m for m in memories 
                          if any(keyword in m.description.lower() 
                                for keyword in ['talk', 'conversation', 'chat'])]
        
        if len(social_memories) >= 5:
            insights.append(
                "I really enjoy connecting with people in my community. "
                "These conversations make running the coffee shop so rewarding."
            )
        
        # 分析工作相关记忆
        work_memories = [m for m in memories
                        if 'work' in m.description.lower() or 
                           'coffee_shop' in m.description.lower()]
        
        if len(work_memories) >= 4:
            insights.append(
                "The coffee shop is becoming a real community hub. "
                "I should think about hosting some events to bring people together."
            )
        
        # 时间相关洞察
        morning_memories = [m for m in memories 
                           if GameTime.get_time_of_day() == 'morning']
        
        if len(morning_memories) >= 3:
            insights.append(
                "Mornings are always busy at the shop. "
                "People really depend on their coffee to start the day right."
            )
        
        return insights[:3]  # 最多返回3个洞察
    
    def get_conversation_style(self) -> Dict[str, Any]:
        """获取 Alice 的对话风格"""
        return {
            'tone': 'warm and friendly',
            'topics': self.favorite_topics,
            'greeting_style': 'enthusiastic',
            'tends_to_ask_about': ['how_are_you', 'coffee_preferences', 'daily_activities'],
            'conversation_starters': [
                "How's your day going so far?",
                "Have you tried our new coffee blend?", 
                "Beautiful weather today, isn't it?",
                "What brings you by the shop today?",
                "How do you like your coffee prepared?"
            ]
        }
    
    async def handle_customer_interaction(self, customer_id: str, interaction_type: str) -> Dict[str, Any]:
        """处理客户互动"""
        if customer_id not in self.regular_customers:
            self.regular_customers.append(customer_id)
        
        # 根据互动类型生成响应
        responses = {
            'order_coffee': "Of course! What can I get started for you today?",
            'casual_chat': "I'm doing well, thanks for asking! How about you?",
            'compliment_coffee': "Thank you so much! I really put a lot of care into each cup.",
            'ask_recommendation': "I'd recommend trying our house blend - it's got a lovely smooth finish!"
        }
        
        response = responses.get(interaction_type, "Thanks for stopping by!")
        
        return {
            'type': 'customer_service',
            'response': response,
            'customer_id': customer_id,
            'mood_impact': 0.1  # 客户互动提升心情
        }
    
    def get_daily_schedule(self) -> List[Dict[str, Any]]:
        """获取 Alice 的日常作息"""
        return [
            {'time': '06:00', 'activity': 'wake_up', 'location': 'home'},
            {'time': '06:30', 'activity': 'prepare_for_work', 'location': 'home'},
            {'time': '07:00', 'activity': 'commute_to_shop', 'location': 'street'},
            {'time': '07:30', 'activity': 'open_shop', 'location': 'coffee_shop'},
            {'time': '08:00', 'activity': 'serve_customers', 'location': 'coffee_shop'},
            {'time': '12:00', 'activity': 'lunch_break', 'location': 'coffee_shop'},
            {'time': '13:00', 'activity': 'serve_customers', 'location': 'coffee_shop'},
            {'time': '17:00', 'activity': 'close_shop', 'location': 'coffee_shop'},
            {'time': '17:30', 'activity': 'social_time', 'location': 'park'},
            {'time': '19:00', 'activity': 'dinner', 'location': 'home'},
            {'time': '20:00', 'activity': 'read_book', 'location': 'home'},
            {'time': '22:00', 'activity': 'sleep', 'location': 'home'}
        ]
    
    def should_approach_for_conversation(self, other_agent: Dict[str, Any]) -> bool:
        """判断是否应该主动接近某人对话"""
        # Alice 比较外向，容易主动与人交流
        if self.personality['extraversion'] > 0.7:
            # 如果对方在咖啡店附近或看起来需要帮助
            distance = ((other_agent['x'] - self.position.x) ** 2 + 
                       (other_agent['y'] - self.position.y) ** 2) ** 0.5
            
            if distance < 3.0 and other_agent.get('state') in ['idle', 'socializing']:
                return True
        
        return False
    
    def get_work_tasks(self) -> List[str]:
        """获取工作任务列表"""
        return [
            "Clean coffee machines",
            "Prepare fresh coffee beans",
            "Serve customers with a smile",
            "Maintain clean and welcoming atmosphere",
            "Try new coffee recipes",
            "Chat with regular customers",
            "Manage inventory",
            "Balance daily cash register"
        ]
    
    async def _decide_next_action(self) -> Dict[str, Any]:
        """Alice特定的行为决策"""
        from ai_town.core.time_manager import GameTime
        import random
        
        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()
        
        # 根据时间和性格特征决定行为
        if time_of_day in ['morning', 'afternoon']:
            # 工作时间，在咖啡店
            if self.position.area != "coffee_shop":
                return {
                    'type': 'move',
                    'position': {'x': 25, 'y': 25, 'area': 'coffee_shop'},
                    'reason': '去咖啡店工作'
                }
            else:
                # 在咖啡店内的工作行为
                work_actions = [
                    {'type': 'work', 'description': '制作新鲜咖啡'},
                    {'type': 'work', 'description': '清理咖啡机'},
                    {'type': 'work', 'description': '招呼顾客'},
                    {'type': 'work', 'description': '尝试新的咖啡配方'},
                    {'type': 'socialize', 'description': '与常客聊天'}
                ]
                return random.choice(work_actions)
        
        elif time_of_day == 'evening':
            # 傍晚时光，可能外出社交或继续工作
            if self.position.area == "coffee_shop" and random.random() < 0.4:
                # 40%概率外出
                evening_destinations = [
                    {'x': 50, 'y': 50, 'area': 'park', 'reason': '去公园散步'},
                    {'x': 35, 'y': 20, 'area': 'bookstore', 'reason': '去书店看看有什么新书'},
                    {'x': 70, 'y': 40, 'area': 'restaurant', 'reason': '去餐厅吃晚饭'},
                    {'x': 60, 'y': 55, 'area': 'market', 'reason': '去市场买新鲜食材'}
                ]
                destination = random.choice(evening_destinations)
                return {
                    'type': 'move',
                    'position': {'x': destination['x'], 'y': destination['y'], 'area': destination['area']},
                    'reason': destination['reason']
                }
            else:
                # 继续在咖啡店或其他地方的活动
                evening_activities = [
                    {'type': 'socialize', 'description': '与朋友聊天'},
                    {'type': 'explore', 'description': '探索小镇新角落'},
                    {'type': 'relax', 'description': '享受悠闲时光'},
                    {'type': 'plan', 'description': '计划明天的咖啡店活动'}
                ]
                return random.choice(evening_activities)
        
        else:  # night
            # 夜晚回家休息
            if self.position.area != "house_1":
                return {
                    'type': 'move',
                    'position': {'x': 10, 'y': 75, 'area': 'house_1'},
                    'reason': '回家休息'
                }
            else:
                night_activities = [
                    {'type': 'relax', 'description': '阅读咖啡制作相关的书籍'},
                    {'type': 'plan', 'description': '为明天准备新的咖啡配方'},
                    {'type': 'rest', 'description': '准备就寝'},
                    {'type': 'think', 'description': '回想今天与顾客的有趣对话'}
                ]
                return random.choice(night_activities)

"""
Bob - 书店老板智能体
安静博学的书店经营者
"""

from ai_town.agents.base_agent import BaseAgent, Position
from typing import List, Dict, Any


class Bob(BaseAgent):
    """
    Bob - 书店老板
    
    性格特点：
    - 内向但博学
    - 喜欢深度对话
    - 关心书籍和知识
    - 乐于助人
    """
    
    def __init__(self):
        personality = {
            'extraversion': 0.4,      # 内向
            'agreeableness': 0.8,     # 友善
            'conscientiousness': 0.9, # 尽责
            'neuroticism': 0.3,       # 稳定
            'openness': 0.8          # 开放
        }
        
        background = (
            "Bob 是一位安静而深思的书店老板，今年47岁。"
            "他经营当地书店已有15年多，对书籍和文学了如指掌。"
            "Bob 喜欢关于哲学、历史和科学的深度对话。"
            "他有点内向，但知识渊博，乐于帮助顾客。"
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
        """生成Bob的洞察"""
        insights = []
        
        # 分析读书相关记忆
        book_memories = [m for m in memories 
                       if any(word in m.description.lower() 
                             for word in ['book', 'read', 'library', 'literature'])]
        
        if len(book_memories) >= 2:
            insights.append(
                "我一直在思考最近读到的书籍内容。"
                "每本书都能带来新的视角和思考。"
            )
        
        # 分析客户互动
        social_memories = [m for m in memories 
                         if any(word in m.description.lower() 
                               for word in ['customer', 'talk', 'conversation', 'help'])]
        
        if len(social_memories) >= 2:
            insights.append(
                "帮助顾客找到合适的书籍让我很有成就感。"
                "每个人都有自己独特的阅读之旅。"
            )
        
        # 分析独处时间
        solitude_memories = [m for m in memories 
                           if any(word in m.description.lower() 
                                 for word in ['alone', 'quiet', 'think', 'reflect'])]
        
        if len(solitude_memories) >= 3:
            insights.append(
                "安静的时光让我能够深入思考和反省。"
                "有时候独处比社交更能让我获得内心的平静。"
            )
        
        return insights[:2]
    
    async def _decide_next_action(self) -> Dict[str, Any]:
        """Bob特定的行为决策"""
        from ai_town.core.time_manager import GameTime
        
        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()
        
        # 根据时间和性格特征决定行为
        if time_of_day in ['morning', 'afternoon']:
            # 工作时间，在书店
            if self.position.area != "bookstore":
                return {
                    'type': 'move',
                    'position': {'x': 35, 'y': 20, 'area': 'bookstore'},
                    'reason': '去书店工作'
                }
            else:
                # 在书店内的行为
                actions = [
                    {'type': 'work', 'description': '整理书架'},
                    {'type': 'work', 'description': '阅读新到的书籍'},
                    {'type': 'work', 'description': '准备书籍推荐清单'},
                    {'type': 'idle', 'description': '静静地思考'}
                ]
                import random
                return random.choice(actions)
        
        elif time_of_day == 'evening':
            # 傍晚可能去其他地方放松
            if random.random() < 0.3:  # 30%概率外出
                return {
                    'type': 'move', 
                    'position': {'x': 50, 'y': 50, 'area': 'park'},
                    'reason': '去公园散步思考'
                }
            else:
                return {'type': 'idle', 'description': '在书店里继续阅读'}
        
        else:  # night
            # 夜晚回家休息
            return {
                'type': 'move',
                'position': {'x': 15, 'y': 60, 'area': 'house_2'},
                'reason': '回家休息'
            }

"""
Charlie - 上班族智能体
新来镇上的年轻办公室职员
"""

from ai_town.agents.base_agent import BaseAgent, Position
from typing import List, Dict, Any
import random


class Charlie(BaseAgent):
    """
    Charlie - 上班族
    
    性格特点：
    - 勤奋有抱负
    - 适应新环境
    - 重视工作生活平衡
    - 喜欢社交
    """
    
    def __init__(self):
        personality = {
            'extraversion': 0.6,      # 较外向
            'agreeableness': 0.7,     # 友善
            'conscientiousness': 0.8, # 负责任
            'neuroticism': 0.4,       # 略有压力
            'openness': 0.5          # 中等开放性
        }
        
        background = (
            "Charlie 是一位28岁的上班族，最近因为新工作搬到了镇上。"
            "他还在逐渐认识新朋友，探索这个社区。"
            "Charlie 工作勤奋且有抱负，但也重视工作与生活的平衡。"
            "他喜欢结识新朋友，探索这个小镇的魅力。"
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
        """生成Charlie的洞察"""
        insights = []
        
        # 分析工作记忆
        work_memories = [m for m in memories 
                       if any(word in m.description.lower() 
                             for word in ['work', 'office', 'job', 'project'])]
        
        if len(work_memories) >= 3:
            insights.append(
                "我开始习惯这里的工作节奏了。"
                "这个办公室环境和我之前的工作很不一样。"
            )
        
        # 分析新环境适应
        social_memories = [m for m in memories 
                         if any(word in m.description.lower() 
                               for word in ['meet', 'talk', 'conversation', 'friend'])]
        
        if len(social_memories) >= 2:
            insights.append(
                "我正在逐渐认识镇上的更多人。"
                "大家看起来都很友善和热情。"
            )
        
        # 分析探索活动
        exploration_memories = [m for m in memories 
                              if any(word in m.description.lower() 
                                    for word in ['explore', 'discover', 'visit', 'new'])]
        
        if len(exploration_memories) >= 2:
            insights.append(
                "这个小镇比我想象的更有趣。"
                "还有很多地方值得我去探索。"
            )
        
        return insights[:2]
    
    async def _decide_next_action(self) -> Dict[str, Any]:
        """Charlie特定的行为决策"""
        from ai_town.core.time_manager import GameTime
        
        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()
        
        # 根据时间和性格特征决定行为
        if time_of_day in ['morning', 'afternoon']:
            # 工作时间
            if self.position.area != "office_1":
                return {
                    'type': 'move',
                    'position': {'x': 60, 'y': 30, 'area': 'office_1'},
                    'reason': '去办公室上班'
                }
            else:
                # 办公室内工作行为
                work_actions = [
                    {'type': 'work', 'description': '处理工作邮件'},
                    {'type': 'work', 'description': '参加会议'},
                    {'type': 'work', 'description': '完成项目任务'},
                    {'type': 'work', 'description': '学习新的工作技能'}
                ]
                return random.choice(work_actions)
        
        elif time_of_day == 'evening':
            # 下班后的活动
            if self.position.area == "office_1":
                # 先离开办公室
                evening_destinations = [
                    {'x': 25, 'y': 25, 'area': 'coffee_shop', 'reason': '去咖啡店放松'},
                    {'x': 35, 'y': 20, 'area': 'bookstore', 'reason': '去书店看看'},
                    {'x': 50, 'y': 50, 'area': 'park', 'reason': '去公园散步'},
                    {'x': 70, 'y': 40, 'area': 'restaurant', 'reason': '去餐厅吃晚饭'}
                ]
                destination = random.choice(evening_destinations)
                return {
                    'type': 'move',
                    'position': {'x': destination['x'], 'y': destination['y'], 'area': destination['area']},
                    'reason': destination['reason']
                }
            else:
                # 在其他地方的休闲活动
                leisure_actions = [
                    {'type': 'socialize', 'description': '和当地人聊天'},
                    {'type': 'explore', 'description': '探索周围环境'},
                    {'type': 'relax', 'description': '享受悠闲时光'},
                    {'type': 'think', 'description': '思考今天的工作'}
                ]
                return random.choice(leisure_actions)
        
        else:  # night
            # 夜晚回家休息
            if self.position.area != "house_3":
                return {
                    'type': 'move',
                    'position': {'x': 85, 'y': 70, 'area': 'house_3'},
                    'reason': '回家休息'
                }
            else:
                night_activities = [
                    {'type': 'rest', 'description': '准备明天的工作'},
                    {'type': 'relax', 'description': '看书或听音乐'},
                    {'type': 'sleep', 'description': '准备睡觉'}
                ]
                return random.choice(night_activities)

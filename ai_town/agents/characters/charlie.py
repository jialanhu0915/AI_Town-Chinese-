"""
Charlie - LLM 增强的上班族智能体
新来镇上的年轻办公室职员，使用大语言模型驱动适应和社交决策
"""

from ai_town.agents.llm_enhanced_agent import LLMEnhancedAgent
from ai_town.agents.base_agent import Position
from typing import List, Dict, Any
import random


class Charlie(LLMEnhancedAgent):
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
        
        # 从配置文件获取 LLM 设置
        from ai_town.config_loader import get_llm_config_for_agent
        llm_config = get_llm_config_for_agent("charlie")
        
        super().__init__(
            agent_id="charlie",
            name="Charlie",
            age=28,
            personality=personality,
            background=background,
            initial_position=Position(60, 30, "office_1"),
            occupation="office_worker",
            work_area="office_1",
            llm_provider=llm_config["provider"]
        )
        
        # 应用 LLM 配置
        self.use_llm_for_planning = llm_config["use_llm_for_planning"]
        self.use_llm_for_conversation = llm_config["use_llm_for_conversation"]
        self.use_llm_for_reflection = llm_config["use_llm_for_reflection"]
        
        # Charlie 特定的属性
        self.work_projects = []
        self.networking_contacts = []
        self.stress_level = 0.3  # 0-1 scale
        self.work_life_balance = 0.7  # 重视工作生活平衡
    
    def _define_available_behaviors(self) -> List[str]:
        """Charlie 可用的行为类型"""
        return [
            'move', 'talk', 'work',  # 基础行为
            'socialize', 'network', 'attend_meeting',  # 社交和职场
            'take_lunch_break', 'commute', 'exercise',  # 生活平衡
            'learn_skill', 'relax', 'explore_town',  # 个人发展
            'eat', 'sleep'  # 生理需求
        ]
    
    def _define_behavior_preferences(self) -> Dict[str, float]:
        """Charlie 的行为偏好"""
        preferences = super()._define_behavior_preferences()
        
        # Charlie 作为上班族的特殊偏好
        preferences.update({
            'work': 0.8,  # 工作认真
            'socialize': 0.7,  # 喜欢社交
            'network': 0.6,  # 建立人脉
            'attend_meeting': 0.5,  # 参加会议
            'take_lunch_break': 0.7,  # 重视午休
            'exercise': 0.6,  # 保持健康
            'learn_skill': 0.7,  # 学习新技能
            'relax': 0.6,  # 放松休息
            'explore_town': 0.5,  # 探索新环境
            'reflect': 0.5  # 适度思考
        })
        
        return preferences
    
    def _define_action_durations(self) -> Dict[str, float]:
        """Charlie 的行为持续时间"""
        durations = super()._define_action_durations()
        
        # Charlie 的专门行为时间
        durations.update({
            'network': 18.0,  # 建立人脉需要时间
            'attend_meeting': 25.0,  # 会议时间
            'take_lunch_break': 20.0,  # 午休时间
            'commute': 12.0,  # 通勤时间
            'exercise': 30.0,  # 锻炼时间
            'learn_skill': 40.0,  # 学习技能
            'relax': 15.0,  # 放松时间
            'explore_town': 35.0  # 探索小镇
        })
        
        return durations
    
    async def _execute_network_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行建立人脉行动"""
        return {
            'type': 'networking',
            'agent_id': self.agent_id,
            'activity': 'building_professional_connections',
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_attend_meeting_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行参加会议行动"""
        meeting_type = self.current_action.get('meeting_type', 'team_meeting')
        return {
            'type': 'meeting_attendance',
            'agent_id': self.agent_id,
            'meeting_type': meeting_type,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_take_lunch_break_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行午休行动"""
        return {
            'type': 'lunch_break',
            'agent_id': self.agent_id,
            'activity': 'taking_midday_rest',
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_exercise_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行锻炼行动"""
        exercise_type = self.current_action.get('exercise_type', 'walking')
        return {
            'type': 'exercising',
            'agent_id': self.agent_id,
            'exercise_type': exercise_type,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_learn_skill_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行学习技能行动"""
        skill = self.current_action.get('skill', 'professional_development')
        return {
            'type': 'skill_learning',
            'agent_id': self.agent_id,
            'skill': skill,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_explore_town_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行探索小镇行动"""
        return {
            'type': 'town_exploration',
            'agent_id': self.agent_id,
            'activity': 'discovering_local_attractions',
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
        
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
    
    async def _llm_decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用 LLM 决定 Charlie 的下一个行为"""
        from ai_town.llm.llm_integration import ask_llm
        from ai_town.core.time_manager import GameTime
        
        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()
        
        # 构建决策上下文
        personality_desc = (
            "你是Charlie，28岁的上班族，勤奋有抱负，适应新环境，重视工作生活平衡，喜欢社交。"
            f"当前适应水平: {self.adaptation_level:.1f}，工作压力: {self.work_stress:.1f}，"
            f"社交网络规模: {self.social_network_size}"
        )
        
        situation_desc = (
            f"现在是{time_of_day}（{GameTime.format_time()}），"
            f"你在{self.position.area}的位置({self.position.x}, {self.position.y})。"
        )
        
        # 获取最近的记忆
        recent_memories = self.memory.get_recent_memories(5)
        memory_desc = "最近的经历: " + "; ".join([m.description for m in recent_memories]) if recent_memories else "暂无最近经历"
        
        # 构建决策提示
        decision_prompt = f"""
{personality_desc}

{situation_desc}

{memory_desc}

基于你的性格、当前情况和最近经历，你接下来想要做什么？
请从以下行为类型中选择一个，并说明原因：

1. move - 移动到新位置（指定目标区域和原因）
2. work - 工作相关活动（如果在办公室）
3. socialize - 社交互动
4. explore - 探索环境
5. relax - 放松休息
6. think - 思考反思
7. sleep - 睡觉休息

请以JSON格式回答，包含type、description和reason字段。
如果是move类型，还要包含target_area字段。

例如：
{{"type": "work", "description": "处理工作邮件", "reason": "现在是工作时间，需要完成今天的任务"}}
或
{{"type": "move", "target_area": "coffee_shop", "description": "去咖啡店", "reason": "工作压力大，想要放松一下"}}
"""

        try:
            # 调用 LLM
            llm_response = await ask_llm(decision_prompt, provider=self.preferred_llm_provider)
            
            # 解析 LLM 响应
            import json
            try:
                decision = json.loads(llm_response.strip())
                
                # 验证和转换决策格式
                if decision.get('type') == 'move' and 'target_area' in decision:
                    # 转换为标准移动格式
                    area_positions = {
                        'office_1': {'x': 60, 'y': 30},
                        'coffee_shop': {'x': 25, 'y': 25},
                        'bookstore': {'x': 35, 'y': 20},
                        'park': {'x': 50, 'y': 50},
                        'restaurant': {'x': 70, 'y': 40},
                        'house_3': {'x': 85, 'y': 70}
                    }
                    
                    target_area = decision['target_area']
                    if target_area in area_positions:
                        pos = area_positions[target_area]
                        return {
                            'type': 'move',
                            'position': {'x': pos['x'], 'y': pos['y'], 'area': target_area},
                            'reason': decision.get('reason', decision.get('description', ''))
                        }
                
                # 其他类型的行为
                return {
                    'type': decision.get('type', 'think'),
                    'description': decision.get('description', '思考当前情况'),
                    'reason': decision.get('reason', '')
                }
                
            except json.JSONDecodeError:
                # LLM 返回格式有误，使用后备逻辑
                print(f"Charlie: LLM 响应格式解析失败，使用后备决策")
                return await self._decide_next_action()
        
        except Exception as e:
            print(f"Charlie: LLM 决策失败 ({e})，使用后备决策")
            return await self._decide_next_action()
    
    async def decide_next_action(self) -> Dict[str, Any]:
        """Charlie 的主要决策方法"""
        if self.use_llm_for_planning:
            try:
                from ai_town.core.time_manager import GameTime
                context = {
                    'current_time': GameTime.format_time(),
                    'position': self.position.__dict__,
                    'recent_memories': [m.description for m in self.memory.get_recent_memories(3)]
                }
                return await self._llm_decide_action(context)
            except Exception as e:
                print(f"Charlie: LLM 决策失败，使用后备决策: {e}")
        
        # 后备决策逻辑
        return await self._decide_next_action()

    async def start_conversation(self, other_agent_name: str, topic: str = "") -> str:
        """Charlie 开始对话"""
        if self.use_llm_for_conversation:
            try:
                return await self._llm_start_conversation(other_agent_name, topic)
            except Exception as e:
                print(f"Charlie: LLM 对话失败，使用后备对话: {e}")
        
        # 后备对话
        greetings = [
            f"你好，{other_agent_name}！我是Charlie，很高兴认识你。",
            f"嗨 {other_agent_name}！我还在熟悉这个镇子，你能给我一些建议吗？",
            f"{other_agent_name}，你好！我是新来的，这里的生活怎么样？",
            f"很高兴遇到你，{other_agent_name}！我刚搬到这里不久。"
        ]
        return random.choice(greetings)
    
    async def respond_to_conversation(self, other_agent_name: str, message: str) -> str:
        """Charlie 回应对话"""
        if self.use_llm_for_conversation:
            try:
                return await self._llm_respond_to_conversation(other_agent_name, message)
            except Exception as e:
                print(f"Charlie: LLM 回应失败，使用后备回应: {e}")
        
        # 后备回应
        if "工作" in message or "office" in message.lower():
            responses = [
                "是的，我在办公室工作。还在适应新的工作环境。",
                "工作很有挑战性，但我喜欢学习新东西。",
                "我正在努力平衡工作和生活，这个镇子很适合放松。"
            ]
        elif "镇子" in message or "town" in message.lower() or "这里" in message:
            responses = [
                "这个镇子真的很棒！大家都很友善。",
                "我还在探索，有什么地方推荐吗？",
                "比我之前住的地方安静多了，我很喜欢。"
            ]
        elif "新" in message or "new" in message.lower():
            responses = [
                "是的，我刚搬来不久。还在适应中。",
                "每天都有新发现，很兴奋！",
                "虽然是新环境，但感觉很温馨。"
            ]
        else:
            responses = [
                "那很有趣！能详细说说吗？",
                "我也有同样的感受。",
                "谢谢你告诉我这些！",
                "我会记住你的建议的。"
            ]
        
        return random.choice(responses)

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

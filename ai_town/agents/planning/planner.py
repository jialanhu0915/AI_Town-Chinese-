"""
智能体行为规划系统
实现 AI Town 中的分层规划架构
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import asyncio

from ai_town.core.time_manager import GameTime


@dataclass
class Goal:
    """目标"""
    id: str
    description: str
    priority: float
    deadline: Optional[datetime] = None
    is_active: bool = True
    progress: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Plan:
    """计划"""
    id: str
    goal_id: str
    description: str
    actions: List[Dict[str, Any]]
    created_at: datetime
    status: str = "active"  # active, completed, failed, cancelled


class ActionPlanner:
    """
    行为规划器
    
    实现分层规划：
    1. 高层计划：长期目标和日常安排
    2. 中层计划：具体任务分解  
    3. 原子动作：可执行的基本行为
    """
    
    def __init__(self, agent):
        self.agent = agent
        self.goals: List[Goal] = []
        self.plans: List[Plan] = []
        self.current_plan: Optional[Plan] = None
        
        # 基本行为模板
        self.action_templates = {
            'daily_routine': self._create_daily_routine,
            'social_interaction': self._create_social_plan,
            'work_activity': self._create_work_plan,
            'leisure_activity': self._create_leisure_plan,
            'maintenance': self._create_maintenance_plan
        }
        
        # 初始化基本目标
        self._initialize_basic_goals()
    
    def _initialize_basic_goals(self):
        """初始化基本的生活目标"""
        basic_goals = [
            Goal(
                id="maintain_energy",
                description="Keep energy levels above 30%",
                priority=9.0
            ),
            Goal(
                id="social_connection", 
                description="Maintain relationships with others",
                priority=7.0
            ),
            Goal(
                id="daily_productivity",
                description="Complete daily work and activities",
                priority=6.0
            ),
            Goal(
                id="personal_growth",
                description="Learn new things and develop skills",
                priority=5.0
            )
        ]
        
        self.goals.extend(basic_goals)
    
    async def plan_next_action(
        self, 
        world_state: Dict[str, Any], 
        context_memories: List[Any],
        current_state: Any
    ) -> Optional[Dict[str, Any]]:
        """
        规划下一个行动
        
        Args:
            world_state: 当前世界状态
            context_memories: 相关记忆上下文
            current_state: 智能体当前状态
            
        Returns:
            下一个行动的详细信息
        """
        # 1. 评估当前需求
        needs = self._assess_needs(world_state, context_memories)
        
        # 2. 选择最紧急的目标
        active_goal = self._select_active_goal(needs)
        
        # 3. 根据目标生成或选择计划
        plan = await self._get_or_create_plan(active_goal, world_state, context_memories)
        
        # 4. 从计划中选择下一个行动
        if plan and plan.actions:
            action = plan.actions[0]  # 执行计划中的第一个行动
            
            # 如果行动完成，从计划中移除
            if action.get('completed', False):
                plan.actions.pop(0)
                if not plan.actions:
                    plan.status = "completed"
            
            return action
        
        # 5. 如果没有具体计划，生成默认行动
        return self._generate_default_action(world_state, needs)
    
    def _assess_needs(self, world_state: Dict[str, Any], context_memories: List[Any]) -> Dict[str, float]:
        """评估智能体的当前需求"""
        needs = {
            'energy': 0.0,
            'social': 0.0,
            'work': 0.0,
            'exploration': 0.0,
            'maintenance': 0.0
        }
        
        # 基于智能体状态评估需求
        if self.agent.energy < 30:
            needs['energy'] = 0.9
        elif self.agent.energy < 60:
            needs['energy'] = 0.5
        
        # 基于时间评估需求
        time_of_day = GameTime.get_time_of_day()
        if time_of_day == "night" and self.agent.energy < 70:
            needs['energy'] = 0.8
        elif time_of_day == "morning":
            needs['work'] = 0.6
        elif time_of_day == "evening":
            needs['social'] = 0.7
        
        # 基于记忆评估社交需求
        recent_social_memories = [
            memory for memory in context_memories
            if any(keyword in memory.description.lower() 
                  for keyword in ['talk', 'conversation', 'chat', 'meet'])
        ]
        
        if len(recent_social_memories) < 3:  # 最近社交活动较少
            needs['social'] = 0.6
        
        # 基于位置和环境评估需求
        current_area = self.agent.position.area
        if current_area == "home":
            needs['maintenance'] = 0.4
        elif current_area == "office":
            needs['work'] = 0.7
        elif current_area == "park":
            needs['social'] = 0.5
            needs['exploration'] = 0.3
        
        return needs
    
    def _select_active_goal(self, needs: Dict[str, float]) -> Goal:
        """根据需求选择活跃目标"""
        # 计算每个目标的紧急度
        goal_urgency = {}
        
        for goal in self.goals:
            if not goal.is_active:
                continue
                
            urgency = goal.priority * 0.1  # 基础紧急度
            
            # 根据需求调整紧急度
            if goal.id == "maintain_energy":
                urgency += needs.get('energy', 0) * 0.9
            elif goal.id == "social_connection":
                urgency += needs.get('social', 0) * 0.7
            elif goal.id == "daily_productivity":
                urgency += needs.get('work', 0) * 0.6
            
            # 考虑截止时间
            if goal.deadline:
                hours_to_deadline = (goal.deadline - GameTime.now()).total_seconds() / 3600
                if hours_to_deadline < 24:
                    urgency += 0.3
                if hours_to_deadline < 6:
                    urgency += 0.5
            
            goal_urgency[goal.id] = urgency
        
        # 选择紧急度最高的目标
        if goal_urgency:
            most_urgent_id = max(goal_urgency, key=goal_urgency.get)
            return next(goal for goal in self.goals if goal.id == most_urgent_id)
        
        # 默认返回第一个活跃目标
        return next((goal for goal in self.goals if goal.is_active), self.goals[0])
    
    async def _get_or_create_plan(
        self, 
        goal: Goal, 
        world_state: Dict[str, Any], 
        context_memories: List[Any]
    ) -> Optional[Plan]:
        """获取或创建实现目标的计划"""
        # 查找现有的活跃计划
        existing_plan = next(
            (plan for plan in self.plans 
             if plan.goal_id == goal.id and plan.status == "active"),
            None
        )
        
        if existing_plan and existing_plan.actions:
            return existing_plan
        
        # 创建新计划
        return await self._create_plan_for_goal(goal, world_state, context_memories)
    
    async def _create_plan_for_goal(
        self, 
        goal: Goal, 
        world_state: Dict[str, Any], 
        context_memories: List[Any]
    ) -> Plan:
        """为特定目标创建计划"""
        plan_id = f"{goal.id}_{len(self.plans)}"
        
        # 根据目标类型选择计划模板
        if goal.id == "maintain_energy":
            actions = await self._create_energy_plan(world_state)
        elif goal.id == "social_connection":
            actions = await self._create_social_plan(world_state)
        elif goal.id == "daily_productivity":
            actions = await self._create_work_plan(world_state)
        else:
            actions = await self._create_default_plan(world_state)
        
        plan = Plan(
            id=plan_id,
            goal_id=goal.id,
            description=f"Plan to achieve: {goal.description}",
            actions=actions,
            created_at=GameTime.now()
        )
        
        self.plans.append(plan)
        self.current_plan = plan
        
        return plan
    
    async def _create_energy_plan(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建恢复能量的计划"""
        actions = []
        
        if self.agent.energy < 20:
            # 紧急休息
            actions.append({
                'type': 'sleep',
                'duration': 60,  # 分钟
                'target_position': {'x': 10, 'y': 10, 'area': 'home'},
                'description': 'Take a nap to restore energy'
            })
        elif self.agent.energy < 50:
            # 吃饭恢复能量
            actions.append({
                'type': 'eat',
                'duration': 20,
                'target_position': {'x': 15, 'y': 15, 'area': 'kitchen'},
                'description': 'Have a meal to restore energy'
            })
        else:
            # 轻松活动
            actions.append({
                'type': 'socialize',
                'duration': 15,
                'activity': 'relax',
                'description': 'Take a short break'
            })
        
        return actions
    
    async def _create_social_plan(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建社交计划"""
        actions = []
        
        # 寻找附近的其他智能体
        nearby_agents = world_state.get('nearby_agents', [])
        
        if nearby_agents:
            # 选择一个智能体进行交流
            target_agent = nearby_agents[0]  # 简单选择第一个
            
            actions.append({
                'type': 'move',
                'target_position': {
                    'x': target_agent['x'],
                    'y': target_agent['y'],
                    'area': target_agent.get('area', 'unknown')
                },
                'description': f"Move closer to {target_agent['name']}"
            })
            
            actions.append({
                'type': 'talk',
                'target_agent': target_agent['id'],
                'message': self._generate_greeting(target_agent),
                'duration': 10,
                'description': f"Start a conversation with {target_agent['name']}"
            })
        else:
            # 去社交场所
            actions.append({
                'type': 'move',
                'target_position': {'x': 50, 'y': 50, 'area': 'park'},
                'description': 'Go to the park to meet people'
            })
            
            actions.append({
                'type': 'socialize',
                'activity': 'look_for_people',
                'duration': 15,
                'description': 'Look for people to talk to'
            })
        
        return actions
    
    async def _create_work_plan(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建工作计划"""
        actions = []
        
        # 根据智能体的背景决定工作类型
        work_area = getattr(self.agent, 'work_area', 'office')
        
        actions.append({
            'type': 'move',
            'target_position': {'x': 30, 'y': 30, 'area': work_area},
            'description': f'Go to {work_area}'
        })
        
        actions.append({
            'type': 'work',
            'work_type': getattr(self.agent, 'occupation', 'general'),
            'duration': 45,
            'description': 'Focus on work tasks'
        })
        
        return actions
    
    async def _create_default_plan(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建默认计划"""
        return [{
            'type': 'socialize',
            'activity': 'observe',
            'duration': 5,
            'description': 'Observe the environment'
        }]
    
    async def _create_leisure_plan(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建休闲计划"""
        actions = []
        
        # 根据时间和心情选择休闲活动
        time_of_day = GameTime.get_time_of_day()
        
        if time_of_day == "evening":
            # 晚上去公园散步
            actions.append({
                'type': 'move',
                'target_position': {'x': 55, 'y': 52, 'area': 'park'},
                'description': 'Go to the park for an evening walk'
            })
            
            actions.append({
                'type': 'socialize',
                'activity': 'enjoy_nature',
                'duration': 20,
                'description': 'Enjoy the peaceful evening at the park'
            })
        else:
            # 其他时间在附近闲逛
            actions.append({
                'type': 'socialize',
                'activity': 'explore',
                'duration': 10,
                'description': 'Take a leisurely stroll around the area'
            })
        
        return actions
    
    async def _create_maintenance_plan(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建维护/保养计划"""
        actions = []
        
        # 基于智能体的能量和需求
        if self.agent.energy < 40:
            # 低能量时回家休息
            actions.append({
                'type': 'move',
                'target_position': {'x': 10, 'y': 10, 'area': 'home'},
                'description': 'Go home to rest and recharge'
            })
            
            actions.append({
                'type': 'sleep',
                'duration': 30,
                'description': 'Take a restorative nap'
            })
        else:
            # 正常维护活动
            actions.append({
                'type': 'socialize',
                'activity': 'self_care',
                'duration': 15,
                'description': 'Take some time for personal maintenance'
            })
        
        return actions
    
    async def _create_daily_routine(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建日常作息计划"""
        actions = []
        time_of_day = GameTime.get_time_of_day()
        
        if time_of_day == "morning":
            # 早晨例行公事
            actions.extend([
                {
                    'type': 'move',
                    'target_position': {'x': 15, 'y': 15, 'area': 'kitchen'},
                    'description': 'Go to kitchen for morning coffee'
                },
                {
                    'type': 'eat',
                    'duration': 15,
                    'description': 'Have morning coffee and light breakfast'
                }
            ])
        elif time_of_day == "afternoon":
            # 下午活动
            actions.append({
                'type': 'work',
                'work_type': 'daily_tasks',
                'duration': 30,
                'description': 'Focus on daily work tasks'
            })
        elif time_of_day == "evening":
            # 晚间放松
            actions.extend([
                {
                    'type': 'socialize',
                    'activity': 'relax',
                    'duration': 20,
                    'description': 'Evening relaxation time'
                },
                {
                    'type': 'move',
                    'target_position': {'x': 10, 'y': 10, 'area': 'home'},
                    'description': 'Head home for the evening'
                }
            ])
        else:  # night
            # 夜间休息
            actions.append({
                'type': 'sleep',
                'duration': 120,  # 2小时
                'description': 'Sleep to restore energy'
            })
        
        return actions
    
    def _generate_default_action(self, world_state: Dict[str, Any], needs: Dict[str, float]) -> Dict[str, Any]:
        """生成默认行动"""
        # 根据最高需求生成行动
        highest_need = max(needs, key=needs.get)
        
        if highest_need == 'energy':
            return {
                'type': 'move',
                'target_position': {'x': 10, 'y': 10, 'area': 'home'},
                'description': 'Go home to rest'
            }
        elif highest_need == 'social':
            return {
                'type': 'move', 
                'target_position': {'x': 50, 'y': 50, 'area': 'park'},
                'description': 'Go to park to socialize'
            }
        elif highest_need == 'work':
            return {
                'type': 'move',
                'target_position': {'x': 30, 'y': 30, 'area': 'office'},
                'description': 'Go to work'
            }
        else:
            return {
                'type': 'socialize',
                'activity': 'explore',
                'description': 'Explore the environment'
            }
    
    def _generate_greeting(self, target_agent: Dict[str, Any]) -> str:
        """生成问候语"""
        time_of_day = GameTime.get_time_of_day()
        
        greetings = {
            'morning': [
                "Good morning! How are you today?",
                "Morning! Nice weather, isn't it?",
                "Hi there! Hope you're having a good start to your day."
            ],
            'afternoon': [
                "Good afternoon! How's your day going?",
                "Hi! Beautiful afternoon, don't you think?",
                "Hey there! How are things with you?"
            ],
            'evening': [
                "Good evening! How was your day?",
                "Hi! Lovely evening, isn't it?",
                "Hey! How are you doing this evening?"
            ],
            'night': [
                "Good evening! Still up I see.",
                "Hi there! Working late?",
                "Hey! Nice to see you this evening."
            ]
        }
        
        import random
        return random.choice(greetings.get(time_of_day, greetings['afternoon']))
    
    def add_goal(self, goal: Goal):
        """添加新目标"""
        self.goals.append(goal)
    
    def complete_goal(self, goal_id: str):
        """完成目标"""
        goal = next((g for g in self.goals if g.id == goal_id), None)
        if goal:
            goal.is_active = False
            goal.progress = 1.0
    
    def get_active_goals(self) -> List[Goal]:
        """获取活跃目标"""
        return [goal for goal in self.goals if goal.is_active]
    
    def get_current_plan_status(self) -> Dict[str, Any]:
        """获取当前计划状态"""
        if self.current_plan:
            return {
                'plan_id': self.current_plan.id,
                'goal_id': self.current_plan.goal_id,
                'description': self.current_plan.description,
                'remaining_actions': len(self.current_plan.actions),
                'status': self.current_plan.status
            }
        return {'status': 'no_active_plan'}

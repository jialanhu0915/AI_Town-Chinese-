"""
基础智能体类
实现 AI Town 中智能体的核心架构
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import asyncio
from enum import Enum

from ai_town.agents.memory.memory_stream import MemoryStream
from ai_town.agents.planning.planner import ActionPlanner
from ai_town.core.time_manager import GameTime


class AgentState(Enum):
    """智能体状态"""
    IDLE = "idle"
    MOVING = "moving"  
    TALKING = "talking"
    WORKING = "working"
    SLEEPING = "sleeping"
    EATING = "eating"
    SOCIALIZING = "socializing"


@dataclass
class Position:
    """位置信息"""
    x: float
    y: float
    area: str = "unknown"
    
    def distance_to(self, other: 'Position') -> float:
        """计算到另一个位置的距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Observation:
    """观察信息"""
    timestamp: datetime
    observer_id: str
    event_type: str
    description: str
    location: Position
    participants: List[str] = field(default_factory=list)
    importance: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    基础智能体类
    
    实现斯坦福 AI Town 论文中的智能体架构：
    - Memory Stream: 记忆流管理
    - Planning: 行为规划 
    - Reflection: 反思机制
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        age: int,
        personality: Dict[str, Any],
        background: str,
        initial_position: Position,
        occupation: str = "resident",
        work_area: str = None,
        **kwargs
    ):
        self.agent_id = agent_id
        self.name = name
        self.age = age
        self.personality = personality
        self.background = background
        self.occupation = occupation
        self.work_area = work_area
        
        # 状态管理
        self.state = AgentState.IDLE
        self.position = initial_position
        self.energy = 100.0
        self.mood = 0.0  # -1.0 到 1.0
        
        # 核心组件
        self.memory = MemoryStream(agent_id)
        self.planner = ActionPlanner(self)
        
        # 社交关系
        self.relationships: Dict[str, float] = {}  # agent_id -> relationship_strength
        
        # 当前活动
        self.current_action: Optional[Dict[str, Any]] = None
        self.action_start_time: Optional[datetime] = None
        
        # 感知范围
        self.perception_radius = 5.0
        self.conversation_radius = 2.0
        
        # 创建初始记忆
        self._initialize_memories()
    
    def _initialize_memories(self):
        """初始化基础记忆"""
        initial_memory = Observation(
            timestamp=GameTime.now(),
            observer_id=self.agent_id,
            event_type="self_introduction",
            description=f"I am {self.name}, {self.age} years old. {self.background}",
            location=self.position,
            importance=9.0
        )
        self.memory.add_observation(initial_memory)
    
    async def step(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行一个时间步
        
        Args:
            world_state: 当前世界状态
            
        Returns:
            执行的动作信息
        """
        # 1. 感知环境
        observations = await self._perceive(world_state)
        
        # 2. 更新记忆
        for obs in observations:
            self.memory.add_observation(obs)
        
        # 3. 反思（如果需要）
        if self.memory.should_reflect():
            await self._reflect()
        
        # 4. 规划行动
        if self._should_replan():
            await self._plan_next_action(world_state)
        
        # 5. 执行当前行动
        action_result = await self._execute_current_action(world_state)
        
        # 6. 更新内部状态
        self._update_internal_state()
        
        return action_result
    
    async def _perceive(self, world_state: Dict[str, Any]) -> List[Observation]:
        """感知环境，生成观察"""
        observations = []
        current_time = GameTime.now()
        
        # 感知附近的其他智能体
        nearby_agents = world_state.get('nearby_agents', [])
        for agent_data in nearby_agents:
            if agent_data['id'] != self.agent_id:
                agent_pos = Position(agent_data['x'], agent_data['y'], agent_data.get('area', 'unknown'))
                if self.position.distance_to(agent_pos) <= self.perception_radius:
                    obs = Observation(
                        timestamp=current_time,
                        observer_id=self.agent_id,
                        event_type="agent_nearby",
                        description=f"I see {agent_data['name']} at {agent_data['area']}",
                        location=agent_pos,
                        participants=[agent_data['id']],
                        importance=2.0
                    )
                    observations.append(obs)
        
        # 感知环境事件
        events = world_state.get('events', [])
        for event in events:
            if self._can_perceive_event(event):
                obs = Observation(
                    timestamp=current_time,
                    observer_id=self.agent_id,
                    event_type=event['type'],
                    description=event['description'],
                    location=Position(event['x'], event['y'], event.get('area', 'unknown')),
                    participants=event.get('participants', []),
                    importance=event.get('importance', 3.0)
                )
                observations.append(obs)
        
        return observations
    
    def _can_perceive_event(self, event: Dict[str, Any]) -> bool:
        """判断是否能感知到某个事件"""
        event_pos = Position(event['x'], event['y'])
        distance = self.position.distance_to(event_pos)
        
        # 根据事件类型和距离判断
        perception_range = {
            'conversation': self.conversation_radius * 1.5,
            'movement': self.perception_radius,
            'activity': self.perception_radius * 0.8,
            'default': self.perception_radius
        }
        
        max_distance = perception_range.get(event.get('type'), perception_range['default'])
        return distance <= max_distance
    
    async def _reflect(self):
        """执行反思，生成高级洞察"""
        # 获取最近的重要记忆
        recent_memories = self.memory.get_recent_memories(limit=50)
        
        # 识别模式和生成洞察
        insights = await self._generate_insights(recent_memories)
        
        # 将洞察作为新的记忆添加
        for insight in insights:
            reflection_obs = Observation(
                timestamp=GameTime.now(),
                observer_id=self.agent_id,
                event_type="reflection",
                description=insight,
                location=self.position,
                importance=7.0,
                metadata={'type': 'reflection'}
            )
            self.memory.add_observation(reflection_obs)
    
    @abstractmethod
    async def _generate_insights(self, memories: List[Observation]) -> List[str]:
        """生成基于记忆的洞察（由子类实现）"""
        pass
    
    def _should_replan(self) -> bool:
        """判断是否需要重新规划"""
        if self.current_action is None:
            return True
        
        # 检查当前行动是否完成
        if self._is_current_action_complete():
            return True
        
        # 检查是否有重要的新信息需要调整计划
        recent_important_memories = self.memory.get_memories_by_importance(
            min_importance=7.0, 
            hours_back=1
        )
        
        return len(recent_important_memories) > 0
    
    def _is_current_action_complete(self) -> bool:
        """检查当前行动是否完成"""
        if self.current_action is None or self.action_start_time is None:
            return True
        
        # 基于行动类型和时间判断
        elapsed_minutes = (GameTime.now() - self.action_start_time).total_seconds() / 60
        
        action_durations = {
            'move': 2.0,
            'talk': 5.0,
            'work': 30.0,
            'eat': 15.0,
            'sleep': 480.0,  # 8小时
            'socialize': 20.0
        }
        
        action_type = self.current_action.get('type', 'unknown')
        expected_duration = action_durations.get(action_type, 10.0)
        
        return elapsed_minutes >= expected_duration
    
    async def _plan_next_action(self, world_state: Dict[str, Any]):
        """规划下一个行动"""
        # 获取相关记忆作为规划上下文
        context_memories = self.memory.retrieve_relevant(
            query=f"What should {self.name} do now?",
            limit=10
        )
        
        # 使用规划器生成行动
        self.current_action = await self.planner.plan_next_action(
            world_state, 
            context_memories,
            self.state
        )
        
        if self.current_action:
            self.action_start_time = GameTime.now()
            self.state = AgentState(self.current_action.get('state', 'idle'))
    
    async def _execute_current_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行当前行动"""
        if self.current_action is None:
            return {'type': 'idle', 'agent_id': self.agent_id}
        
        action_type = self.current_action.get('type')
        
        if action_type == 'move':
            return await self._execute_move_action()
        elif action_type == 'talk':
            return await self._execute_talk_action(world_state)
        elif action_type == 'work':
            return await self._execute_work_action()
        elif action_type == 'socialize':
            return await self._execute_socialize_action(world_state)
        else:
            return {'type': action_type or 'idle', 'agent_id': self.agent_id}
    
    async def _execute_move_action(self) -> Dict[str, Any]:
        """执行移动行动"""
        target = self.current_action.get('target_position')
        if target:
            # 简单的移动逻辑
            dx = target['x'] - self.position.x
            dy = target['y'] - self.position.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > 0.1:  # 还未到达
                # 每步移动一定距离
                move_speed = 1.0
                if distance > move_speed:
                    self.position.x += (dx / distance) * move_speed
                    self.position.y += (dy / distance) * move_speed
                else:
                    self.position.x = target['x']
                    self.position.y = target['y']
                    self.position.area = target.get('area', self.position.area)
        
        return {
            'type': 'move',
            'agent_id': self.agent_id,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_talk_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行对话行动"""
        target_id = self.current_action.get('target_agent')
        message = self.current_action.get('message', f"Hello!")
        
        return {
            'type': 'talk',
            'agent_id': self.agent_id,
            'target_agent': target_id,
            'message': message,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_work_action(self) -> Dict[str, Any]:
        """执行工作行动"""
        work_type = self.current_action.get('work_type', 'general')
        
        return {
            'type': 'work',
            'agent_id': self.agent_id,
            'work_type': work_type,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    async def _execute_socialize_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行社交行动"""
        activity = self.current_action.get('activity', 'chat')
        
        return {
            'type': 'socialize', 
            'agent_id': self.agent_id,
            'activity': activity,
            'position': {'x': self.position.x, 'y': self.position.y, 'area': self.position.area}
        }
    
    def _update_internal_state(self):
        """更新内部状态"""
        # 更新能量
        self.energy -= 1.0  # 基础消耗
        if self.state == AgentState.SLEEPING:
            self.energy += 5.0
        elif self.state == AgentState.WORKING:
            self.energy -= 2.0
        
        # 限制范围
        self.energy = max(0, min(100, self.energy))
        
        # 更新心情（简单实现）
        if self.energy < 20:
            self.mood -= 0.1
        elif self.energy > 80:
            self.mood += 0.05
        
        self.mood = max(-1.0, min(1.0, self.mood))
    
    def receive_message(self, sender_id: str, message: str, context: Dict[str, Any]):
        """接收来自其他智能体的消息"""
        # 创建观察记录
        obs = Observation(
            timestamp=GameTime.now(),
            observer_id=self.agent_id,
            event_type="received_message",
            description=f"{context.get('sender_name', sender_id)} said: {message}",
            location=self.position,
            participants=[sender_id],
            importance=4.0,
            metadata={'message': message, 'sender': sender_id}
        )
        self.memory.add_observation(obs)
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体当前状态"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'age': self.age,
            'occupation': self.occupation,
            'work_area': self.work_area,
            'position': {
                'x': self.position.x,
                'y': self.position.y, 
                'area': self.position.area
            },
            'state': self.state.value,
            'energy': self.energy,
            'mood': self.mood,
            'current_action': self.current_action,
            'memory_count': len(self.memory.observations)
        }

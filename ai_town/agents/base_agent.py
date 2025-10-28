"""
基础智能体类
实现 AI Town 中智能体的核心架构
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ai_town.agents.memory.memory_stream import MemoryStream
from ai_town.agents.planning.planner import ActionPlanner
from ai_town.core.time_manager import GameTime
from ai_town.events.event_registry import event_registry


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

    def distance_to(self, other: "Position") -> float:
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
        **kwargs,
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

        # 个性化行为配置
        self.available_behaviors = self._define_available_behaviors()
        self.behavior_preferences = self._define_behavior_preferences()
        self.action_durations = self._define_action_durations()

        # 创建初始记忆
        self._initialize_memories()

    def _define_available_behaviors(self) -> List[str]:
        """
        定义此智能体可用的行为类型（子类可重写）
        """
        return [
            "move",
            "talk",
            "work",
            "eat",
            "sleep",
            "socialize",
            "reflect",
            "read",
            "create",
        ]

    def _define_behavior_preferences(self) -> Dict[str, float]:
        """基于性格定义行为偏好权重（子类可重写）"""
        preferences = {
            "move": 0.3,
            "talk": self.personality.get("extraversion", 0.5),
            "work": self.personality.get("conscientiousness", 0.7),
            "eat": 0.2,
            "sleep": 0.1,
            "socialize": self.personality.get("extraversion", 0.5) * 0.8,
            "reflect": self.personality.get("openness", 0.5),
            "read": self.personality.get("openness", 0.5),
            "create": self.personality.get("openness", 0.5),
        }

        # 内向者更喜欢独处活动
        if self.personality.get("extraversion", 0.5) < 0.5:
            preferences["socialize"] *= 0.3
            preferences["reflect"] *= 1.5
            preferences["read"] = preferences.get("read", 0.5) * 1.3

        return preferences

    def _define_action_durations(self) -> Dict[str, float]:
        """
        定义各种行为的持续时间（子类可重写）
        优先从统一事件元（EventRegistry）读取 duration_range，最少枚举。
        """
        durations = {}
        for behavior in self.available_behaviors:
            event_id = self._to_event_id(behavior)
            metadata = event_registry.get_event_metadata(event_id)
            if metadata and hasattr(metadata, "duration_range"):
                min_dur, max_dur = metadata.duration_range
                durations[behavior] = (min_dur + max_dur) / 2
            else:
                # 兜底值，尽量减少显式枚举
                defaults = {"movement": 2.0, "conversation": 5.0, "work": 30.0, "sleeping": 480.0}
                durations[behavior] = defaults.get(event_id, 10.0)
        return durations

    def _initialize_memories(self):
        """初始化基础记忆"""
        initial_memory = Observation(
            timestamp=GameTime.now(),
            observer_id=self.agent_id,
            event_type="self_introduction",
            description=f"I am {self.name}, {self.age} years old. {self.background}",
            location=self.position,
            importance=9.0,
        )
        self.memory.add_observation(initial_memory)

    def _to_event_id(self, behavior: str) -> str:
        """
        将行为名规范化为事件ID（尽量无枚举，少量必要映射）。
        例如: move->movement, talk->conversation, sleep->sleeping, eat->eating。
        未匹配则返回原值（假定已是事件ID）。
        """
        b = (behavior or "").lower()
        mapping = {
            "move": "movement",
            "talk": "conversation",
            "sleep": "sleeping",
            "eat": "eating",
            "read": "reading",
            "create": "creating",
            "reflect": "reflection",
            "explore": "town_exploration",
            # 追加最小必要别名映射（来自角色常用行为）
            "idle": "reflection",
            "think": "reflection",
            "plan": "reflection",
            "relax": "socialize",
            "rest": "sleeping",
            "commute": "movement",
            "take_break": "socialize",
        }
        return mapping.get(b, b)

    def _resolve_executor(self, action_type: str):
        """
        解析动作执行方法。优先精确匹配 _execute_{action_type}_action；
        其次处理少量词形变化（movement->move, conversation->talk, *ing 还原）。
        找不到则返回 None，由通用执行处理。
        """
        if not action_type:
            return None
        name = action_type.lower()
        # 1) 直接匹配
        method_name = f"_execute_{name}_action"
        if hasattr(self, method_name):
            return getattr(self, method_name)
        # 2) 少量必要词形映射
        special = {"movement": "move", "conversation": "talk", "town_exploration": "explore"}
        if name in special:
            m2 = f"_execute_{special[name]}_action"
            if hasattr(self, m2):
                return getattr(self, m2)
        # 3) 处理 *ing 词形（read/create/sleep/eat/work 等）
        if name.endswith("ing"):
            base = name[:-3]  # reading->read, sleeping->sleep, eating->eat, working->work
            for cand in (base, base + "e"):
                m3 = f"_execute_{cand}_action"
                if hasattr(self, m3):
                    return getattr(self, m3)
        return None

    def _set_state_for_action(self, event_id: str):
        """
        根据事件ID或事件分类设置 AgentState，尽量不逐一枚举。
        优先少量确定映射；否则依据事件分类（social->SOCIALIZING, work->WORKING）。
        """
        e = (event_id or "").lower()
        fixed = {
            "movement": AgentState.MOVING,
            "conversation": AgentState.TALKING,
            "socialize": AgentState.SOCIALIZING,
            "work": AgentState.WORKING,
            "sleeping": AgentState.SLEEPING,
            "eating": AgentState.EATING,
        }
        if e in fixed:
            self.state = fixed[e]
            return
        # 基于事件分类回退
        metadata = event_registry.get_event_metadata(e)
        if metadata:
            cat = getattr(metadata, "category", None)
            if str(getattr(cat, "value", cat)).lower() == "social":
                self.state = AgentState.SOCIALIZING
            elif str(getattr(cat, "value", cat)).lower() == "work":
                self.state = AgentState.WORKING
            # 其余分类保持原状态

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
        nearby_agents = world_state.get("nearby_agents", [])
        for agent_data in nearby_agents:
            if agent_data["id"] != self.agent_id:
                agent_pos = Position(
                    agent_data["x"], agent_data["y"], agent_data.get("area", "unknown")
                )
                if self.position.distance_to(agent_pos) <= self.perception_radius:
                    obs = Observation(
                        timestamp=current_time,
                        observer_id=self.agent_id,
                        event_type="agent_nearby",
                        description=f"I see {agent_data['name']} at {agent_data['area']}",
                        location=agent_pos,
                        participants=[agent_data["id"]],
                        importance=2.0,
                    )
                    observations.append(obs)

        # 感知环境事件
        events = world_state.get("events", [])
        for event in events:
            if self._can_perceive_event(event):
                obs = Observation(
                    timestamp=current_time,
                    observer_id=self.agent_id,
                    event_type=event["type"],
                    description=event["description"],
                    location=Position(event["x"], event["y"], event.get("area", "unknown")),
                    participants=event.get("participants", []),
                    importance=event.get("importance", 3.0),
                )
                observations.append(obs)

        return observations

    def _can_perceive_event(self, event: Dict[str, Any]) -> bool:
        """判断是否能感知到某个事件"""
        event_pos = Position(event["x"], event["y"])
        distance = self.position.distance_to(event_pos)

        # 根据事件类型和距离判断
        perception_range = {
            "conversation": self.conversation_radius * 1.5,
            "movement": self.perception_radius,
            "activity": self.perception_radius * 0.8,
            "default": self.perception_radius,
        }

        max_distance = perception_range.get(event.get("type"), perception_range["default"])
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
                metadata={"type": "reflection"},
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
            min_importance=7.0, hours_back=1
        )

        return len(recent_important_memories) > 0

    def _is_current_action_complete(self) -> bool:
        """检查当前行动是否完成"""
        if self.current_action is None or self.action_start_time is None:
            return True

        # 基于行动类型和时间判断
        elapsed_minutes = (GameTime.now() - self.action_start_time).total_seconds() / 60

        action_type = self.current_action.get("type", "unknown")
        expected_duration = self.action_durations.get(action_type, 10.0)

        return elapsed_minutes >= expected_duration

    async def _plan_next_action(self, world_state: Dict[str, Any]):
        """规划下一个行动"""
        # 获取相关记忆作为规划上下文
        context_memories = self.memory.retrieve_relevant(
            query=f"What should {self.name} do now?", limit=10
        )

        # 使用规划器生成行动
        self.current_action = await self.planner.plan_next_action(
            world_state, context_memories, self.state
        )

        if self.current_action:
            self.action_start_time = GameTime.now()
            self.state = AgentState(self.current_action.get("state", "idle"))

    async def _execute_current_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行当前行动（统一解析，最少枚举）。
        """
        if self.current_action is None:
            return {"type": "idle", "agent_id": self.agent_id}

        action_type = self.current_action.get("type")

        # 行为可用性不再严格限制，缺省进入解析/通用执行
        executor = self._resolve_executor(action_type)
        if executor:
            # 在具体执行前设置状态（具体方法内如有覆盖，以覆盖为准）
            self._set_state_for_action(self._to_event_id(action_type))
            return (
                await executor(world_state)
                if asyncio.iscoroutinefunction(executor)
                else executor(world_state)
            )

        # 通用执行：事件类型用标准化ID，并设置状态
        event_id = self._to_event_id(action_type)
        self._set_state_for_action(event_id)
        return await self._execute_generic_action(event_id, world_state)

    async def _execute_default_action(
        self, attempted_action: str, world_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        默认回退：不枚举别名，直接走通用执行，事件类型使用标准化ID。
        """
        event_id = self._to_event_id(attempted_action)
        self._set_state_for_action(event_id)
        return await self._execute_generic_action(event_id, world_state)

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
            metadata={"message": message, "sender": sender_id},
        )
        self.memory.add_observation(obs)

    def get_status(self) -> Dict[str, Any]:
        """获取智能体当前状态"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "work_area": self.work_area,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
            "state": self.state.value,
            "energy": self.energy,
            "mood": self.mood,
            "current_action": self.current_action,
            "memory_count": len(self.memory.observations),
        }

    async def _execute_move_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行移动行动
        """
        self.state = AgentState.MOVING
        target = self.current_action.get("target_position")
        if target:
            # 简单的移动逻辑
            dx = target["x"] - self.position.x
            dy = target["y"] - self.position.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 0.1:  # 还未到达
                # 每步移动一定距离
                move_speed = 1.0
                if distance > move_speed:
                    self.position.x += (dx / distance) * move_speed
                    self.position.y += (dy / distance) * move_speed
                else:
                    self.position.x = target["x"]
                    self.position.y = target["y"]
                    self.position.area = target.get("area", self.position.area)

        return {
            "type": "movement",
            "agent_id": self.agent_id,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_talk_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行对话行动"""
        self.state = AgentState.TALKING
        target_id = self.current_action.get("target_agent")
        message = self.current_action.get("message", f"Hello!")

        return {
            "type": "conversation",
            "agent_id": self.agent_id,
            "target_agent": target_id,
            "message": message,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_work_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作行动
        """
        self.state = AgentState.WORKING
        work_type = self.current_action.get("work_type", "general")

        return {
            "type": "work",
            "agent_id": self.agent_id,
            "work_type": work_type,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_socialize_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行社交行动"""
        self.state = AgentState.SOCIALIZING
        activity = self.current_action.get("activity", "chat")

        return {
            "type": "socialize",
            "agent_id": self.agent_id,
            "activity": activity,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_reflect_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行反思行动"""
        reflection_topic = self.current_action.get("topic", "recent_experiences")

        return {
            "type": "reflection",
            "agent_id": self.agent_id,
            "topic": reflection_topic,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_read_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行阅读行动"""
        material = self.current_action.get("material", "book")

        return {
            "type": "reading",
            "agent_id": self.agent_id,
            "material": material,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_create_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行创作行动"""
        creation_type = self.current_action.get("creation_type", "writing")

        return {
            "type": "creating",
            "agent_id": self.agent_id,
            "creation_type": creation_type,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_eat_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行进食行动，统一事件类型为 'eating'
        """
        self.state = AgentState.EATING
        return {
            "type": "eating",
            "agent_id": self.agent_id,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_sleep_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行睡眠行动，统一事件类型为 'sleeping'
        """
        self.state = AgentState.SLEEPING
        return {
            "type": "sleeping",
            "agent_id": self.agent_id,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
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

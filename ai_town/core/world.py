"""
世界状态管理器
管理整个 AI Town 的世界状态、事件和智能体协调
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ai_town.agents.base_agent import BaseAgent, Observation, Position
from ai_town.core.time_manager import GameTime
from ai_town.environment.map import GameMap


@dataclass
class WorldEvent:
    """世界事件"""

    id: str
    timestamp: datetime
    event_type: str
    description: str
    location: Position
    participants: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[int] = None  # 持续时间（分钟）

    def is_expired(self) -> bool:
        """检查事件是否已过期"""
        if self.duration is None:
            return False

        elapsed_minutes = GameTime.minutes_since(self.timestamp)
        return elapsed_minutes >= self.duration


class World:
    """
    世界状态管理器

    负责：
    - 管理所有智能体
    - 维护世界状态
    - 处理智能体间的交互
    - 管理事件系统
    - 协调时间步进
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.map = GameMap()

        # 世界状态
        self.current_events: List[WorldEvent] = []
        self.event_history: List[WorldEvent] = []

        # 运行状态
        self.is_running = False
        self.step_count = 0
        self.last_step_time: Optional[datetime] = None

        # 配置
        self.step_interval = 1.0  # 秒
        self.max_events = 100  # 最大同时事件数

        # 统计信息
        self.stats = {
            "total_interactions": 0,
            "total_movements": 0,
            "total_conversations": 0,
            "uptime_start": GameTime.now(),
        }

        # 自动交互冷却：记录两两智能体最近一次自动交互时间
        self._last_auto_interaction: Dict[tuple, datetime] = {}

    def add_agent(self, agent: BaseAgent):
        """添加智能体到世界"""
        self.agents[agent.agent_id] = agent

        # 在地图上注册智能体位置
        building = self.map.get_building_at(int(agent.position.x), int(agent.position.y))
        if building:
            self.map.add_agent_to_building(agent.agent_id, building.id)

    def remove_agent(self, agent_id: str):
        """从世界中移除智能体"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]

            # 从地图上注销
            building = self.map.get_building_at(int(agent.position.x), int(agent.position.y))
            if building:
                self.map.remove_agent_from_building(agent_id, building.id)

            del self.agents[agent_id]

    def get_world_state(self, for_agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取世界状态

        Args:
            for_agent_id: 如果指定，返回该智能体视角的世界状态
        """
        agent_positions = {}
        for agent_id, agent in self.agents.items():
            agent_positions[agent_id] = {
                "id": agent_id,
                "name": agent.name,
                "x": agent.position.x,
                "y": agent.position.y,
                "area": agent.position.area,
                "state": agent.state.value,
                "energy": agent.energy,
                "mood": agent.mood,
            }

        world_state = {
            "current_time": GameTime.format_time(),
            "time_of_day": GameTime.get_time_of_day(),
            "day_of_week": GameTime.get_day_of_week(),
            "step_count": self.step_count,
            "agent_positions": agent_positions,
            "events": [self._serialize_event(event) for event in self.current_events],
            "map_data": self.map.get_map_data(),
        }

        # 如果是特定智能体的视角，添加附近智能体信息
        if for_agent_id and for_agent_id in self.agents:
            agent = self.agents[for_agent_id]
            nearby_agents = self.map.get_nearby_agents(
                agent.position.x, agent.position.y, agent.perception_radius, agent_positions
            )
            world_state["nearby_agents"] = nearby_agents

        return world_state

    async def step(self) -> Dict[str, Any]:
        """
        执行一个世界时间步

        Returns:
            本轮执行的所有行动
        """
        self.step_count += 1
        self.last_step_time = GameTime.now()

        # 清理过期事件
        self._cleanup_expired_events()

        # 并行执行所有智能体的步骤
        agent_tasks = []
        for agent in self.agents.values():
            world_state = self.get_world_state(agent.agent_id)
            task = asyncio.create_task(agent.step(world_state))
            agent_tasks.append((agent.agent_id, task))

        # 等待所有智能体完成步骤
        step_results = {}
        for agent_id, task in agent_tasks:
            try:
                result = await task
                step_results[agent_id] = result

                # 处理行动结果
                await self._process_agent_action(agent_id, result)

            except Exception as e:
                print(f"Error in agent {agent_id} step: {e}")
                step_results[agent_id] = {"type": "error", "error": str(e)}

        # 处理智能体间的交互
        await self._process_interactions()

        # 更新统计信息
        self._update_stats(step_results)

        return step_results

    def _to_event_id(self, action_type: str) -> str:
        """
        将动作类型标准化为事件ID，最少必要映射。
        """
        if not action_type:
            return "unknown"
        name = action_type.lower()
        mapping = {"move": "movement", "talk": "conversation"}
        return mapping.get(name, name)

    async def _process_agent_action(self, agent_id: str, action: Dict[str, Any]):
        """处理智能体的行动"""
        action_type = action.get("type")
        event_id = self._to_event_id(action_type)

        if event_id == "movement":
            # 确保传入类型为 movement
            action["type"] = "movement"
            await self._process_movement(agent_id, action)
        elif event_id == "conversation":
            # 确保传入类型为 conversation
            action["type"] = "conversation"
            await self._process_talk(agent_id, action)
        else:
            # 其余统一走通用活动处理
            action["type"] = event_id
            await self._process_activity(agent_id, action)

    async def _process_movement(self, agent_id: str, action: Dict[str, Any]):
        """处理移动行动"""
        agent = self.agents.get(agent_id)
        if not agent:
            return

        old_position = Position(agent.position.x, agent.position.y, agent.position.area)
        new_position = action.get("position", {})

        # 更新智能体在地图上的位置
        old_building = self.map.get_building_at(int(old_position.x), int(old_position.y))
        new_building = self.map.get_building_at(
            int(new_position.get("x", agent.position.x)),
            int(new_position.get("y", agent.position.y)),
        )

        if old_building and old_building != new_building:
            self.map.remove_agent_from_building(agent_id, old_building.id)

        if new_building and new_building != old_building:
            self.map.add_agent_to_building(agent_id, new_building.id)

        # 创建移动事件
        move_event = WorldEvent(
            id=str(uuid.uuid4()),
            timestamp=GameTime.now(),
            event_type="movement",
            description=f"{agent.name} moved from {old_position.area} to {new_position.get('area', 'unknown')}",
            location=Position(
                new_position.get("x", agent.position.x),
                new_position.get("y", agent.position.y),
                new_position.get("area", agent.position.area),
            ),
            participants=[agent_id],
            duration=1,
        )

        self.current_events.append(move_event)
        self.stats["total_movements"] += 1

    async def _process_talk(self, agent_id: str, action: Dict[str, Any]):
        """处理对话行动"""
        speaker = self.agents.get(agent_id)
        target_id = action.get("target_agent")
        target = self.agents.get(target_id)

        if not speaker or not target:
            return

        message = action.get("message", "")

        # 计算距离，确保在对话范围内
        distance = speaker.position.distance_to(target.position)
        if distance > speaker.conversation_radius:
            return

        # 发送消息给目标智能体
        target.receive_message(
            agent_id, message, {"sender_name": speaker.name, "location": speaker.position.area}
        )

        # 创建对话事件
        conversation_event = WorldEvent(
            id=str(uuid.uuid4()),
            timestamp=GameTime.now(),
            event_type="conversation",
            description=f"{speaker.name} said to {target.name}: {message}",
            location=speaker.position,
            participants=[agent_id, target_id],
            metadata={"message": message, "speaker": agent_id, "listener": target_id},
            duration=5,
        )

        self.current_events.append(conversation_event)
        self.stats["total_conversations"] += 1
        self.stats["total_interactions"] += 1

    async def _process_activity(self, agent_id: str, action: Dict[str, Any]):
        """处理一般活动"""
        agent = self.agents.get(agent_id)
        if not agent:
            return

        activity_type = action.get("type", "activity")

        # 合并动作中除通用字段外的参数到元数据，便于格式化器提取
        extra_meta = {k: v for k, v in action.items() if k not in {"type", "agent_id", "position"}}

        # 创建活动事件：使用具体动作名作为事件类型，便于统一事件元匹配
        activity_event = WorldEvent(
            id=str(uuid.uuid4()),
            timestamp=GameTime.now(),
            event_type=activity_type,
            description=f"{agent.name} is {activity_type.replace('_', ' ')}",
            location=agent.position,
            participants=[agent_id],
            metadata=extra_meta,
            duration=10,
        )

        self.current_events.append(activity_event)

    async def _process_interactions(self):
        """处理智能体间的自动交互"""
        agent_list = list(self.agents.values())

        for i, agent1 in enumerate(agent_list):
            for agent2 in agent_list[i + 1 :]:
                distance = agent1.position.distance_to(agent2.position)

                # 如果距离很近且都处于社交状态，可能发生自动交互
                if (
                    distance <= 2.0
                    and agent1.state.value in ["idle", "socializing"]
                    and agent2.state.value in ["idle", "socializing"]
                ):

                    # 成对冷却：十分钟内重复相同对话不再自动触发
                    pair_key = tuple(sorted([agent1.agent_id, agent2.agent_id]))
                    last = self._last_auto_interaction.get(pair_key)
                    if last is not None and GameTime.minutes_since(last) < 10:
                        continue

                    # 检查是否应该发生交互（基于性格等）
                    should_interact = self._should_agents_interact(agent1, agent2)

                    if should_interact:
                        await self._create_automatic_interaction(agent1, agent2)
                        self._last_auto_interaction[pair_key] = GameTime.now()

    def _should_agents_interact(self, agent1: BaseAgent, agent2: BaseAgent) -> bool:
        """判断两个智能体是否应该自动交互"""
        # 基于性格的简单判断
        agent1_social = agent1.personality.get("extraversion", 0.5)
        agent2_social = agent2.personality.get("extraversion", 0.5)

        # 概率采用乘积（只要一方内向就显著降低），并总体降频
        interaction_probability = agent1_social * agent2_social * 0.08
        # 若任一方偏内向，再次衰减
        if agent1_social < 0.5 or agent2_social < 0.5:
            interaction_probability *= 0.5

        import random

        return random.random() < interaction_probability

    async def _create_automatic_interaction(self, agent1: BaseAgent, agent2: BaseAgent):
        """创建自动交互"""
        # 简单的问候交互
        greeting_messages = [
            f"Hello {agent2.name}! Nice to see you.",
            f"Hi there! How are you doing?",
            f"Good {GameTime.get_time_of_day()}! How's everything?",
        ]

        import random

        message = random.choice(greeting_messages)

        # 发送消息
        agent2.receive_message(
            agent1.agent_id,
            message,
            {
                "sender_name": agent1.name,
                "location": agent1.position.area,
                "interaction_type": "automatic_greeting",
            },
        )

        # 创建交互事件
        interaction_event = WorldEvent(
            id=str(uuid.uuid4()),
            timestamp=GameTime.now(),
            event_type="automatic_interaction",
            description=f"{agent1.name} and {agent2.name} had a brief interaction",
            location=agent1.position,
            participants=[agent1.agent_id, agent2.agent_id],
            metadata={"type": "greeting"},
            duration=3,
        )

        self.current_events.append(interaction_event)
        self.stats["total_interactions"] += 1

    def _cleanup_expired_events(self):
        """清理过期的事件"""
        unexpired_events = []

        for event in self.current_events:
            if not event.is_expired():
                unexpired_events.append(event)
            else:
                # 移动到历史记录
                self.event_history.append(event)

        self.current_events = unexpired_events

        # 限制历史记录大小
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]

    def _serialize_event(self, event: WorldEvent) -> Dict[str, Any]:
        """序列化事件为字典"""
        return {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "type": event.event_type,
            "description": event.description,
            "x": event.location.x,
            "y": event.location.y,
            "area": event.location.area,
            "participants": event.participants,
            "metadata": event.metadata,
            "duration": event.duration,
        }

    def _update_stats(self, step_results: Dict[str, Any]):
        """更新统计信息"""
        # 统计不同类型的行动
        action_counts = {}
        for result in step_results.values():
            action_type = result.get("type", "unknown")
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        # 更新全局统计
        if not hasattr(self, "action_history"):
            self.action_history = {}

        for action_type, count in action_counts.items():
            self.action_history[action_type] = self.action_history.get(action_type, 0) + count

    async def run_simulation(self, duration_minutes: Optional[int] = None):
        """
        运行模拟

        Args:
            duration_minutes: 运行时长（分钟），None表示无限运行
        """
        self.is_running = True
        start_time = GameTime.now()

        print(f"🏘️ AI 小镇模拟开始于 {GameTime.format_time()}")
        print(f"👥 {len(self.agents)} 个智能体活跃中")

        try:
            while self.is_running:
                # 执行一步
                step_results = await self.step()

                # 打印步骤信息
                if self.step_count % 10 == 0:  # 每10步打印一次
                    print(
                        f"第 {self.step_count} 步: {len([r for r in step_results.values() if r.get('type') != 'idle'])} 个活跃行动"
                    )

                # 检查是否达到运行时长
                if duration_minutes:
                    elapsed = GameTime.minutes_since(start_time)
                    if elapsed >= duration_minutes:
                        break

                # 等待下一步
                await asyncio.sleep(self.step_interval)

        except KeyboardInterrupt:
            print("\n⏹️ 用户中断了模拟")
        finally:
            self.is_running = False
            print(f"📊 模拟结束，共进行了 {self.step_count} 步")
            print(f"📈 总互动次数: {self.stats['total_interactions']}")
            print(f"🚶 总移动次数: {self.stats['total_movements']}")
            print(f"💬 总对话次数: {self.stats['total_conversations']}")

    def stop_simulation(self):
        """停止模拟"""
        self.is_running = False

    def get_simulation_stats(self) -> Dict[str, Any]:
        """获取模拟统计信息"""
        uptime = GameTime.minutes_since(self.stats["uptime_start"])

        return {
            "step_count": self.step_count,
            "uptime_minutes": uptime,
            "agent_count": len(self.agents),
            "active_events": len(self.current_events),
            "total_interactions": self.stats["total_interactions"],
            "total_movements": self.stats["total_movements"],
            "total_conversations": self.stats["total_conversations"],
            "action_history": getattr(self, "action_history", {}),
            "average_steps_per_minute": self.step_count / max(uptime, 1),
        }

    def save_world_state(self, filepath: str):
        """保存世界状态到文件"""
        import os
        from pathlib import Path

        # 确保数据目录存在
        data_dir = Path("ai_town/data/simulation_results")
        data_dir.mkdir(parents=True, exist_ok=True)

        # 如果传入的是文件名，则放到数据目录中
        if not os.path.dirname(filepath):
            filepath = data_dir / filepath

        world_data = {
            "timestamp": GameTime.format_time(),
            "step_count": self.step_count,
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            "events": [self._serialize_event(event) for event in self.current_events],
            "stats": self.get_simulation_stats(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(world_data, f, indent=2, ensure_ascii=False)

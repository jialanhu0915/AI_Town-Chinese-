"""
记忆流系统
实现 AI Town 论文中的记忆流架构
"""

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ai_town.core.time_manager import GameTime


@dataclass
class Memory:
    """单条记忆"""

    id: str
    timestamp: datetime
    description: str
    importance: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    keywords: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.metadata is None:
            self.metadata = {}

    def get_recency_score(self) -> float:
        """计算记忆的新近度得分"""
        hours_ago = GameTime.hours_since(self.timestamp)
        # 使用指数衰减函数
        return math.exp(-hours_ago / 24)  # 24小时半衰期

    def get_importance_score(self) -> float:
        """获取重要性得分"""
        return self.importance / 10.0  # 归一化到0-1

    def get_relevance_score(self, query_keywords: List[str]) -> float:
        """计算与查询的相关性得分"""
        if not query_keywords or not self.keywords:
            return 0.0

        # 计算关键词重叠
        common_keywords = set(self.keywords) & set(query_keywords)
        if not common_keywords:
            return 0.0

        # 使用 Jaccard 相似度
        union_keywords = set(self.keywords) | set(query_keywords)
        return len(common_keywords) / len(union_keywords)

    def get_retrieval_score(self, query_keywords: List[str]) -> float:
        """
        计算检索得分

        根据论文，检索得分 = α * recency + β * importance + γ * relevance
        """
        alpha, beta, gamma = 1.0, 1.0, 1.0  # 权重参数

        recency = self.get_recency_score()
        importance = self.get_importance_score()
        relevance = self.get_relevance_score(query_keywords)

        return alpha * recency + beta * importance + gamma * relevance


class MemoryStream:
    """
    记忆流管理器

    实现智能体的记忆系统，包括：
    - 观察记录
    - 重要性评估
    - 记忆检索
    - 反思触发
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.observations: List[Memory] = []
        self.reflections: List[Memory] = []

        # 反思参数
        self.reflection_threshold = 150  # 累积重要性阈值
        self.importance_sum = 0.0

        # 环境变量开关
        # AI_TOWN_MEMORY_PERSIST: 是否持久化到磁盘（默认开启）
        # AI_TOWN_MEMORY_LOAD: 是否从磁盘加载历史记忆（默认开启）
        def _env_true(name: str, default: str = "1") -> bool:
            return os.getenv(name, default).lower() in ("1", "true", "yes", "on")

        self._persist_enabled = _env_true("AI_TOWN_MEMORY_PERSIST", "1")
        self._load_enabled = _env_true("AI_TOWN_MEMORY_LOAD", "1")

        # 数据持久化路径（仅在启用持久化时设置与创建）
        self.data_dir = None
        if self._persist_enabled:
            self.data_dir = f"ai_town/data/memories/{agent_id}"
            os.makedirs(self.data_dir, exist_ok=True)

        # 加载已有记忆（仅当持久化与加载均启用时）
        if self._persist_enabled and self._load_enabled:
            self._load_memories()

    def add_observation(self, observation) -> str:
        """
        添加观察记录

        Args:
            observation: Observation 对象

        Returns:
            记忆ID
        """
        # 从 Observation 创建 Memory
        memory = Memory(
            id=f"{self.agent_id}_obs_{len(self.observations)}",
            timestamp=observation.timestamp,
            description=observation.description,
            importance=observation.importance,
            keywords=self._extract_keywords(observation.description),
            metadata={
                "event_type": observation.event_type,
                "location": {
                    "x": observation.location.x,
                    "y": observation.location.y,
                    "area": observation.location.area,
                },
                "participants": observation.participants,
                "observer_id": observation.observer_id,
            },
        )

        self.observations.append(memory)
        self.importance_sum += memory.importance

        # 保存到磁盘
        self._save_memory(memory)

        return memory.id

    def add_reflection(self, insight: str, importance: float = 8.0) -> str:
        """添加反思洞察"""
        memory = Memory(
            id=f"{self.agent_id}_refl_{len(self.reflections)}",
            timestamp=GameTime.now(),
            description=insight,
            importance=importance,
            keywords=self._extract_keywords(insight),
            metadata={"type": "reflection"},
        )

        self.reflections.append(memory)

        # 保存到磁盘
        self._save_memory(memory)

        return memory.id

    def retrieve_relevant(self, query: str, limit: int = 10) -> List[Memory]:
        """
        检索相关记忆

        Args:
            query: 查询字符串
            limit: 返回记忆数量限制

        Returns:
            按相关性排序的记忆列表
        """
        query_keywords = self._extract_keywords(query)

        # 合并观察和反思
        all_memories = self.observations + self.reflections

        # 计算每条记忆的检索得分
        scored_memories = []
        for memory in all_memories:
            score = memory.get_retrieval_score(query_keywords)
            scored_memories.append((score, memory))

        # 按得分排序并返回前N条
        scored_memories.sort(key=lambda x: x[0], reverse=True)

        # 更新访问信息
        result_memories = []
        for score, memory in scored_memories[:limit]:
            if score > 0:  # 只返回有相关性的记忆
                memory.access_count += 1
                memory.last_accessed = GameTime.now()
                result_memories.append(memory)

        return result_memories

    def get_recent_memories(self, hours_back: int = 24, limit: int = 50) -> List[Memory]:
        """获取最近的记忆"""
        cutoff_time = GameTime.now() - timedelta(hours=hours_back)

        recent_memories = [
            memory
            for memory in self.observations + self.reflections
            if memory.timestamp >= cutoff_time
        ]

        # 按时间排序
        recent_memories.sort(key=lambda x: x.timestamp, reverse=True)

        return recent_memories[:limit]

    def get_memories_by_importance(
        self, min_importance: float = 5.0, hours_back: int = 24
    ) -> List[Memory]:
        """获取重要的记忆"""
        cutoff_time = GameTime.now() - timedelta(hours=hours_back)

        important_memories = [
            memory
            for memory in self.observations + self.reflections
            if (memory.timestamp >= cutoff_time and memory.importance >= min_importance)
        ]

        # 按重要性排序
        important_memories.sort(key=lambda x: x.importance, reverse=True)

        return important_memories

    def should_reflect(self) -> bool:
        """判断是否应该进行反思"""
        return self.importance_sum >= self.reflection_threshold

    def reset_importance_sum(self):
        """重置重要性累计（反思后调用）"""
        self.importance_sum = 0.0

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取（实际项目中可以使用更复杂的NLP技术）
        import re

        # 移除标点符号并转为小写
        clean_text = re.sub(r"[^\w\s]", " ", text.lower())
        words = clean_text.split()

        # 过滤停用词和短词
        stop_words = {
            "i",
            "me",
            "my",
            "myself",
            "we",
            "our",
            "ours",
            "ourselves",
            "you",
            "your",
            "yours",
            "yourself",
            "yourselves",
            "he",
            "him",
            "his",
            "himself",
            "she",
            "her",
            "hers",
            "herself",
            "it",
            "its",
            "itself",
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            "what",
            "which",
            "who",
            "whom",
            "this",
            "that",
            "these",
            "those",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "having",
            "do",
            "does",
            "did",
            "doing",
            "a",
            "an",
            "the",
            "and",
            "but",
            "if",
            "or",
            "because",
            "as",
            "until",
            "while",
            "of",
            "at",
            "by",
            "for",
            "with",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
            "in",
            "out",
            "on",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
        }

        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        return list(set(keywords))  # 去重

    def _save_memory(self, memory: Memory):
        """保存单条记忆到磁盘"""
        # 如关闭持久化，直接返回
        if not self._persist_enabled or not self.data_dir:
            return
        filename = f"{memory.id}.json"
        filepath = os.path.join(self.data_dir, filename)

        memory_data = {
            "id": memory.id,
            "timestamp": memory.timestamp.isoformat(),
            "description": memory.description,
            "importance": memory.importance,
            "access_count": memory.access_count,
            "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else None,
            "keywords": memory.keywords,
            "metadata": memory.metadata,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

    def _load_memories(self):
        """从磁盘加载记忆"""
        # 如关闭持久化或加载，直接返回
        if not self._persist_enabled or not self._load_enabled or not self.data_dir:
            return
        if not os.path.exists(self.data_dir):
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    memory = Memory(
                        id=data["id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        description=data["description"],
                        importance=data["importance"],
                        access_count=data.get("access_count", 0),
                        last_accessed=(
                            datetime.fromisoformat(data["last_accessed"])
                            if data.get("last_accessed")
                            else None
                        ),
                        keywords=data.get("keywords", []),
                        metadata=data.get("metadata", {}),
                    )

                    # 根据类型添加到对应列表
                    if memory.metadata.get("type") == "reflection":
                        self.reflections.append(memory)
                    else:
                        self.observations.append(memory)

                except Exception as e:
                    print(f"Error loading memory from {filepath}: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        return {
            "total_observations": len(self.observations),
            "total_reflections": len(self.reflections),
            "importance_sum": self.importance_sum,
            "reflection_threshold": self.reflection_threshold,
            "should_reflect": self.should_reflect(),
        }

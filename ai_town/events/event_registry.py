"""
统一事件注册系统
集中管理所有事件类型的元数据，实现前后端统一的事件处理
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EventCategory(Enum):
    """事件分类"""

    MOVEMENT = "movement"
    SOCIAL = "social"
    WORK = "work"
    PERSONAL = "personal"
    LEARNING = "learning"
    MAINTENANCE = "maintenance"
    RECREATION = "recreation"


@dataclass
class EventMetadata:
    """事件元数据"""

    event_id: str
    icon: str
    category: EventCategory
    display_names: Dict[str, str]  # 多语言显示名称
    description_template: Dict[str, str]  # 多语言描述模板
    color: str = "#667eea"
    duration_range: tuple = (5, 30)  # 默认持续时间范围（分钟）
    importance: float = 3.0  # 默认重要性
    tags: List[str] = field(default_factory=list)


class EventRegistry:
    """事件注册表"""

    def __init__(self):
        self._events: Dict[str, EventMetadata] = {}
        self._register_default_events()

    def register_event(self, metadata: EventMetadata):
        """注册事件类型"""
        self._events[metadata.event_id] = metadata

    def get_event_metadata(self, event_id: str) -> Optional[EventMetadata]:
        """获取事件元数据"""
        return self._events.get(event_id)

    def get_all_events(self) -> Dict[str, EventMetadata]:
        """获取所有事件元数据"""
        return self._events.copy()

    def get_events_by_category(self, category: EventCategory) -> Dict[str, EventMetadata]:
        """按分类获取事件"""
        return {k: v for k, v in self._events.items() if v.category == category}

    def get_events_by_tags(self, tags: List[str]) -> Dict[str, EventMetadata]:
        """按标签获取事件"""
        result = {}
        for event_id, metadata in self._events.items():
            if any(tag in metadata.tags for tag in tags):
                result[event_id] = metadata
        return result

    def _register_default_events(self):
        """注册默认事件类型"""

        # 基础行为事件
        self.register_event(
            EventMetadata(
                event_id="movement",
                icon="🚶",
                category=EventCategory.MOVEMENT,
                display_names={"zh": "移动", "en": "Movement"},
                description_template={
                    "zh": "{agent_name} 从{from_area}移动到{to_area}",
                    "en": "{agent_name} moved from {from_area} to {to_area}",
                },
                color="#28a745",
                tags=["basic", "navigation"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="conversation",
                icon="💬",
                category=EventCategory.SOCIAL,
                display_names={"zh": "对话", "en": "Conversation"},
                description_template={
                    "zh": "{agent_name} 与 {target_name} 开始对话",
                    "en": "{agent_name} started conversation with {target_name}",
                },
                color="#17a2b8",
                tags=["social", "communication"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="reflection",
                icon="💭",
                category=EventCategory.PERSONAL,
                display_names={"zh": "思考", "en": "Reflection"},
                description_template={
                    "zh": "{agent_name} 正在深度思考{topic}",
                    "en": "{agent_name} is reflecting on {topic}",
                },
                color="#6f42c1",
                tags=["introspection", "mental"],
            )
        )

        # Alice 专属事件
        self.register_event(
            EventMetadata(
                event_id="customer_greeting",
                icon="👋",
                category=EventCategory.WORK,
                display_names={"zh": "迎接顾客", "en": "Greeting Customer"},
                description_template={
                    "zh": "{agent_name} 热情地迎接进店的顾客",
                    "en": "{agent_name} warmly greets incoming customers",
                },
                color="#FF69B4",
                tags=["alice", "service", "hospitality"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="coffee_making",
                icon="☕",
                category=EventCategory.WORK,
                display_names={"zh": "制作咖啡", "en": "Making Coffee"},
                description_template={
                    "zh": "{agent_name} 正在精心制作{coffee_type}",
                    "en": "{agent_name} is carefully making {coffee_type}",
                },
                color="#8B4513",
                tags=["alice", "craft", "beverage"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="friendly_chat",
                icon="😊",
                category=EventCategory.SOCIAL,
                display_names={"zh": "友好聊天", "en": "Friendly Chat"},
                description_template={
                    "zh": "{agent_name} 与常客进行愉快的闲聊",
                    "en": "{agent_name} has a pleasant chat with regular customers",
                },
                color="#FF69B4",
                tags=["alice", "social", "customers"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="drink_recommendation",
                icon="🥤",
                category=EventCategory.WORK,
                display_names={"zh": "推荐饮品", "en": "Recommending Drinks"},
                description_template={
                    "zh": "{agent_name} 为顾客推荐合适的饮品",
                    "en": "{agent_name} recommends suitable drinks to customers",
                },
                color="#FF8C00",
                tags=["alice", "service", "recommendation"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="shop_maintenance",
                icon="🧹",
                category=EventCategory.MAINTENANCE,
                display_names={"zh": "店铺维护", "en": "Shop Maintenance"},
                description_template={
                    "zh": "{agent_name} 正在清洁和维护咖啡店",
                    "en": "{agent_name} is cleaning and maintaining the coffee shop",
                },
                color="#32CD32",
                tags=["alice", "cleaning", "upkeep"],
            )
        )

        # Bob 专属事件
        self.register_event(
            EventMetadata(
                event_id="organizing_books",
                icon="📚",
                category=EventCategory.WORK,
                display_names={"zh": "整理书籍", "en": "Organizing Books"},
                description_template={
                    "zh": "{agent_name} 仔细地整理书架上的书籍",
                    "en": "{agent_name} carefully organizes books on the shelves",
                },
                color="#4169E1",
                tags=["bob", "organization", "books"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="customer_service",
                icon="🤝",
                category=EventCategory.WORK,
                display_names={"zh": "客户服务", "en": "Customer Service"},
                description_template={
                    "zh": "{agent_name} 正在帮助顾客寻找合适的书籍",
                    "en": "{agent_name} is helping customers find suitable books",
                },
                color="#4169E1",
                tags=["bob", "service", "assistance"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="researching",
                icon="🔍",
                category=EventCategory.LEARNING,
                display_names={"zh": "研究", "en": "Researching"},
                description_template={
                    "zh": "{agent_name} 正在深入研究{topic}",
                    "en": "{agent_name} is deeply researching {topic}",
                },
                color="#800080",
                tags=["bob", "study", "academic"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="book_recommendation",
                icon="📖",
                category=EventCategory.WORK,
                display_names={"zh": "推荐书籍", "en": "Book Recommendation"},
                description_template={
                    "zh": "{agent_name} 为顾客推荐适合的书籍",
                    "en": "{agent_name} recommends suitable books to customers",
                },
                color="#4169E1",
                tags=["bob", "recommendation", "books"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="reading",
                icon="📘",
                category=EventCategory.LEARNING,
                display_names={"zh": "阅读", "en": "Reading"},
                description_template={
                    "zh": "{agent_name} 正在专心阅读{material}",
                    "en": "{agent_name} is focused on reading {material}",
                },
                color="#4169E1",
                tags=["bob", "reading", "knowledge"],
            )
        )

        # Charlie 专属事件
        self.register_event(
            EventMetadata(
                event_id="networking",
                icon="🤝",
                category=EventCategory.SOCIAL,
                display_names={"zh": "建立人脉", "en": "Networking"},
                description_template={
                    "zh": "{agent_name} 正在建立职业人脉关系",
                    "en": "{agent_name} is building professional connections",
                },
                color="#FFD700",
                tags=["charlie", "professional", "career"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="meeting_attendance",
                icon="👔",
                category=EventCategory.WORK,
                display_names={"zh": "参加会议", "en": "Attending Meeting"},
                description_template={
                    "zh": "{agent_name} 正在参加{meeting_type}",
                    "en": "{agent_name} is attending {meeting_type}",
                },
                color="#2F4F4F",
                tags=["charlie", "meeting", "professional"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="lunch_break",
                icon="🍽️",
                category=EventCategory.PERSONAL,
                display_names={"zh": "午休", "en": "Lunch Break"},
                description_template={
                    "zh": "{agent_name} 正在享受午休时光",
                    "en": "{agent_name} is enjoying lunch break",
                },
                color="#FF6347",
                tags=["charlie", "break", "wellness"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="exercising",
                icon="💪",
                category=EventCategory.RECREATION,
                display_names={"zh": "锻炼", "en": "Exercising"},
                description_template={
                    "zh": "{agent_name} 正在进行{exercise_type}锻炼",
                    "en": "{agent_name} is doing {exercise_type} exercise",
                },
                color="#32CD32",
                tags=["charlie", "fitness", "health"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="skill_learning",
                icon="📚",
                category=EventCategory.LEARNING,
                display_names={"zh": "学习技能", "en": "Learning Skills"},
                description_template={
                    "zh": "{agent_name} 正在学习{skill}",
                    "en": "{agent_name} is learning {skill}",
                },
                color="#9370DB",
                tags=["charlie", "development", "career"],
            )
        )

        self.register_event(
            EventMetadata(
                event_id="town_exploration",
                icon="🗺️",
                category=EventCategory.RECREATION,
                display_names={"zh": "探索小镇", "en": "Exploring Town"},
                description_template={
                    "zh": "{agent_name} 正在探索小镇的新地方",
                    "en": "{agent_name} is exploring new places in town",
                },
                color="#FF4500",
                tags=["charlie", "exploration", "adventure"],
            )
        )

        # 通用工作事件
        self.register_event(
            EventMetadata(
                event_id="work",
                icon="💼",
                category=EventCategory.WORK,
                display_names={"zh": "工作", "en": "Working"},
                description_template={
                    "zh": "{agent_name} 正在专心工作",
                    "en": "{agent_name} is working diligently",
                },
                color="#FF8C00",
                tags=["general", "productive"],
            )
        )


# 全局事件注册表实例
event_registry = EventRegistry()

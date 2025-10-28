"""
Alice - LLM 增强的智能体角色
一个友好的咖啡店老板，使用大语言模型驱动行为和对话
"""

import asyncio
import random
from typing import Any, Dict, List

from ai_town.agents.base_agent import Position
from ai_town.agents.llm_enhanced_agent import LLMEnhancedAgent
from ai_town.core.time_manager import GameTime


class Alice(LLMEnhancedAgent):
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
            "extraversion": 0.8,  # 外向性
            "agreeableness": 0.9,  # 宜人性
            "conscientiousness": 0.7,  # 尽责性
            "neuroticism": 0.2,  # 神经质
            "openness": 0.6,  # 开放性
        }

        background = (
            "Alice 是一位温暖友好的咖啡店老板，今年32岁。"
            "她5年前搬到这个小镇，开了她梦想中的咖啡店。"
            "Alice 喜欢结识新朋友，让每个人都感到宾至如归。"
            "她以出色的咖啡和记住每个人最爱的订单而闻名。"
            "闲暇时，她喜欢读书和尝试新的咖啡配方。"
        )

        # 从配置文件获取 LLM 设置
        from ai_town.config_loader import get_llm_config_for_agent

        llm_config = get_llm_config_for_agent("alice")

        super().__init__(
            agent_id="alice",
            name="Alice",
            age=32,
            personality=personality,
            background=background,
            initial_position=Position(25, 25, "coffee_shop"),
            occupation="coffee_shop_owner",
            work_area="coffee_shop",
            llm_provider=llm_config["provider"],
        )

        # 应用 LLM 配置
        self.use_llm_for_planning = llm_config["use_llm_for_planning"]
        self.use_llm_for_conversation = llm_config["use_llm_for_conversation"]
        self.use_llm_for_reflection = llm_config["use_llm_for_reflection"]

        # Alice 特定的属性
        self.favorite_topics = ["coffee", "books", "travel", "food", "community"]
        self.regular_customers = []
        self.coffee_knowledge = 8.5  # 1-10 scale

    def _define_available_behaviors(self) -> List[str]:
        """Alice 可用的行为类型"""
        return [
            "move",
            "talk",
            "work",  # 基础行为
            "socialize",
            "greet_customer",
            "make_coffee",  # 咖啡店相关
            "chat_with_regulars",
            "recommend_drink",
            "clean_shop",  # 服务相关
            "eat",
            "sleep",
            "take_break",  # 生理需求
        ]

    def _define_behavior_preferences(self) -> Dict[str, float]:
        """Alice 的行为偏好"""
        preferences = super()._define_behavior_preferences()

        # Alice 作为外向的咖啡店老板的特殊偏好
        preferences.update(
            {
                "socialize": 0.9,  # 非常喜欢社交
                "greet_customer": 0.8,  # 喜欢迎接顾客
                "make_coffee": 0.7,  # 喜欢制作咖啡
                "chat_with_regulars": 0.9,  # 喜欢与常客聊天
                "recommend_drink": 0.8,  # 喜欢推荐饮品
                "clean_shop": 0.6,  # 保持店铺整洁
                "reflect": 0.4,  # 不太喜欢独自思考
                "work": 0.7,  # 工作认真
            }
        )

        return preferences

    def _define_action_durations(self) -> Dict[str, float]:
        """Alice 的行为持续时间"""
        durations = super()._define_action_durations()

        # Alice 的专门行为时间
        durations.update(
            {
                "greet_customer": 3.0,  # 快速热情问候
                "make_coffee": 8.0,  # 制作咖啡
                "chat_with_regulars": 12.0,  # 与常客聊天
                "recommend_drink": 5.0,  # 推荐饮品
                "clean_shop": 15.0,  # 清洁店铺
                "take_break": 10.0,  # 短暂休息
            }
        )

        return durations

    async def _execute_greet_customer_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行迎接顾客行动"""
        return {
            "type": "customer_greeting",
            "agent_id": self.agent_id,
            "activity": "welcoming_customers",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_make_coffee_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行制作咖啡行动"""
        coffee_type = self.current_action.get("coffee_type", "espresso")
        return {
            "type": "coffee_making",
            "agent_id": self.agent_id,
            "coffee_type": coffee_type,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_chat_with_regulars_action(
        self, world_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行与常客聊天行动"""
        return {
            "type": "friendly_chat",
            "agent_id": self.agent_id,
            "activity": "chatting_with_regular_customers",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_recommend_drink_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行推荐饮品行动"""
        return {
            "type": "drink_recommendation",
            "agent_id": self.agent_id,
            "activity": "suggesting_beverages",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_clean_shop_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行清洁店铺行动"""
        return {
            "type": "shop_maintenance",
            "agent_id": self.agent_id,
            "activity": "cleaning_coffee_shop",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _generate_insights(self, memories: List) -> List[str]:
        """生成 Alice 特有的洞察"""
        insights = []

        # 分析客户模式
        customer_memories = [
            m
            for m in memories
            if "customer" in m.description.lower() or "coffee" in m.description.lower()
        ]

        if len(customer_memories) >= 3:
            insights.append(
                "I've been noticing more customers are interested in specialty coffee. "
                "Maybe I should consider expanding my menu with more unique blends."
            )

        # 分析社交互动
        social_memories = [
            m
            for m in memories
            if any(keyword in m.description.lower() for keyword in ["talk", "conversation", "chat"])
        ]

        if len(social_memories) >= 5:
            insights.append(
                "I really enjoy connecting with people in my community. "
                "These conversations make running the coffee shop so rewarding."
            )

        # 分析工作相关记忆
        work_memories = [
            m
            for m in memories
            if "work" in m.description.lower() or "coffee_shop" in m.description.lower()
        ]

        if len(work_memories) >= 4:
            insights.append(
                "The coffee shop is becoming a real community hub. "
                "I should think about hosting some events to bring people together."
            )

        # 时间相关洞察
        morning_memories = [m for m in memories if GameTime.get_time_of_day() == "morning"]

        if len(morning_memories) >= 3:
            insights.append(
                "Mornings are always busy at the shop. "
                "People really depend on their coffee to start the day right."
            )

        return insights[:3]  # 最多返回3个洞察

    def get_conversation_style(self) -> Dict[str, Any]:
        """获取 Alice 的对话风格"""
        return {
            "tone": "warm and friendly",
            "topics": self.favorite_topics,
            "greeting_style": "enthusiastic",
            "tends_to_ask_about": ["how_are_you", "coffee_preferences", "daily_activities"],
            "conversation_starters": [
                "How's your day going so far?",
                "Have you tried our new coffee blend?",
                "Beautiful weather today, isn't it?",
                "What brings you by the shop today?",
                "How do you like your coffee prepared?",
            ],
        }

    async def handle_customer_interaction(
        self, customer_id: str, interaction_type: str
    ) -> Dict[str, Any]:
        """处理客户互动"""
        if customer_id not in self.regular_customers:
            self.regular_customers.append(customer_id)

        # 根据互动类型生成响应
        responses = {
            "order_coffee": "Of course! What can I get started for you today?",
            "casual_chat": "I'm doing well, thanks for asking! How about you?",
            "compliment_coffee": "Thank you so much! I really put a lot of care into each cup.",
            "ask_recommendation": "I'd recommend trying our house blend - it's got a lovely smooth finish!",
        }

        response = responses.get(interaction_type, "Thanks for stopping by!")

        return {
            "type": "customer_service",
            "response": response,
            "customer_id": customer_id,
            "mood_impact": 0.1,  # 客户互动提升心情
        }

    def get_daily_schedule(self) -> List[Dict[str, Any]]:
        """获取 Alice 的日常作息"""
        return [
            {"time": "06:00", "activity": "wake_up", "location": "home"},
            {"time": "06:30", "activity": "prepare_for_work", "location": "home"},
            {"time": "07:00", "activity": "commute_to_shop", "location": "street"},
            {"time": "07:30", "activity": "open_shop", "location": "coffee_shop"},
            {"time": "08:00", "activity": "serve_customers", "location": "coffee_shop"},
            {"time": "12:00", "activity": "lunch_break", "location": "coffee_shop"},
            {"time": "13:00", "activity": "serve_customers", "location": "coffee_shop"},
            {"time": "17:00", "activity": "close_shop", "location": "coffee_shop"},
            {"time": "17:30", "activity": "social_time", "location": "park"},
            {"time": "19:00", "activity": "dinner", "location": "home"},
            {"time": "20:00", "activity": "read_book", "location": "home"},
            {"time": "22:00", "activity": "sleep", "location": "home"},
        ]

    def should_approach_for_conversation(self, other_agent: Dict[str, Any]) -> bool:
        """判断是否应该主动接近某人对话"""
        # Alice 比较外向，容易主动与人交流
        if self.personality["extraversion"] > 0.7:
            # 如果对方在咖啡店附近或看起来需要帮助
            distance = (
                (other_agent["x"] - self.position.x) ** 2
                + (other_agent["y"] - self.position.y) ** 2
            ) ** 0.5

            if distance < 3.0 and other_agent.get("state") in ["idle", "socializing"]:
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
            "Balance daily cash register",
        ]

    async def _decide_next_action(self) -> Dict[str, Any]:
        """Alice特定的行为决策"""
        import random

        from ai_town.core.time_manager import GameTime

        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()

        # 根据时间和性格特征决定行为
        if time_of_day in ["morning", "afternoon"]:
            # 工作时间，在咖啡店
            if self.position.area != "coffee_shop":
                return {
                    "type": "move",
                    "position": {"x": 25, "y": 25, "area": "coffee_shop"},
                    "reason": "去咖啡店工作",
                }
            else:
                # 在咖啡店内的工作行为
                work_actions = [
                    {"type": "work", "description": "制作新鲜咖啡"},
                    {"type": "work", "description": "清理咖啡机"},
                    {"type": "work", "description": "招呼顾客"},
                    {"type": "work", "description": "尝试新的咖啡配方"},
                    {"type": "socialize", "description": "与常客聊天"},
                ]
                return random.choice(work_actions)

        elif time_of_day == "evening":
            # 傍晚时光，可能外出社交或继续工作
            if self.position.area == "coffee_shop" and random.random() < 0.4:
                # 40%概率外出
                evening_destinations = [
                    {"x": 50, "y": 50, "area": "park", "reason": "去公园散步"},
                    {"x": 35, "y": 20, "area": "bookstore", "reason": "去书店看看有什么新书"},
                    {"x": 70, "y": 40, "area": "restaurant", "reason": "去餐厅吃晚饭"},
                    {"x": 60, "y": 55, "area": "market", "reason": "去市场买新鲜食材"},
                ]
                destination = random.choice(evening_destinations)
                return {
                    "type": "move",
                    "position": {
                        "x": destination["x"],
                        "y": destination["y"],
                        "area": destination["area"],
                    },
                    "reason": destination["reason"],
                }
            else:
                # 继续在咖啡店或其他地方的活动
                evening_activities = [
                    {"type": "socialize", "description": "与朋友聊天"},
                    {"type": "explore", "description": "探索小镇新角落"},
                    {"type": "relax", "description": "享受悠闲时光"},
                    {"type": "plan", "description": "计划明天的咖啡店活动"},
                ]
                return random.choice(evening_activities)

        else:  # night
            # 夜晚回家休息
            if self.position.area != "house_1":
                return {
                    "type": "move",
                    "position": {"x": 10, "y": 75, "area": "house_1"},
                    "reason": "回家休息",
                }
            else:
                night_activities = [
                    {"type": "relax", "description": "阅读咖啡制作相关的书籍"},
                    {"type": "plan", "description": "为明天准备新的咖啡配方"},
                    {"type": "rest", "description": "准备就寝"},
                    {"type": "think", "description": "回想今天与顾客的有趣对话"},
                ]
                return random.choice(night_activities)

    async def _fallback_decide_action(self) -> Dict[str, Any]:
        """Alice 的智能回退决策逻辑"""
        return await self._decide_next_action()

    def _fallback_conversation_response(self, speaker_name: str, message: str) -> str:
        """Alice 特有的对话回应风格"""
        message_lower = message.lower()

        # 咖啡相关话题
        if any(word in message_lower for word in ["coffee", "drink", "latte", "espresso", "brew"]):
            responses = [
                "哦，你也是咖啡爱好者！我很乐意为你推荐一些特别的饮品。",
                "咖啡对我来说不只是饮品，更像是艺术品。每一杯都有自己的故事。",
                "你有什么特别喜欢的咖啡口味吗？我一直在尝试新的配方。",
                "一杯好咖啡真的能让整天都变得美好，不是吗？",
            ]

        # 工作相关话题
        elif any(word in message_lower for word in ["work", "job", "busy", "shop", "business"]):
            responses = [
                "经营咖啡店虽然忙碌，但看到顾客因为我的咖啡而微笑，一切都值得了。",
                "这个小镇的人们真的很棒，每天都有新的故事和有趣的对话。",
                "我喜欢我的工作，因为它让我能够为社区带来一些温暖。",
                "忙碌的日子让时间过得特别快，但我享受每一刻。",
            ]

        # 天气相关
        elif any(word in message_lower for word in ["weather", "sunny", "rain", "cold", "warm"]):
            responses = [
                "是啊，这样的天气很适合坐在店里慢慢品味一杯热咖啡呢。",
                "不管天气如何，总有一款咖啡适合当下的心情。",
                "我喜欢观察不同天气下，人们对咖啡的选择也会不同。",
                "天气变化时，咖啡就成了最好的陪伴。",
            ]

        # 问候和关心
        elif any(word in message_lower for word in ["how", "doing", "good", "great", "fine"]):
            responses = [
                f"谢谢你的关心，{speaker_name}！我过得很不错，店里的生意也很好。",
                "每天都充满新的可能性，我很享受这种感觉！你呢？",
                "生活很美好，特别是能在这里遇见像你这样的好朋友。",
                "我一直都很好，因为做着自己喜欢的事情。最近你怎么样？",
            ]

        # 通用友好回应
        else:
            responses = [
                f"这很有趣，{speaker_name}！请告诉我更多。",
                "我很喜欢听你分享这些，继续说吧！",
                "你总是有这么有趣的想法，我很欣赏。",
                "这让我想起了一些相似的经历...",
                "谢谢你和我分享这个，真的很棒！",
            ]

        import random

        return random.choice(responses)

    async def decide_next_action(self) -> Dict[str, Any]:
        """Alice 的主要决策方法"""
        if self.use_llm_for_planning:
            try:
                from ai_town.core.time_manager import GameTime

                context = {
                    "current_time": GameTime.format_time(),
                    "position": self.position.__dict__,
                    "recent_memories": [m.description for m in self.memory.get_recent_memories(3)],
                }
                return await self._llm_decide_action(context)
            except Exception as e:
                print(f"Alice: LLM 决策失败，使用后备决策: {e}")

        # 后备决策逻辑
        return await self._decide_next_action()

    async def start_conversation(self, other_agent_name: str, topic: str = "") -> str:
        """Alice 开始对话"""
        if self.use_llm_for_conversation:
            try:
                return await self._llm_start_conversation(other_agent_name, topic)
            except Exception as e:
                print(f"Alice: LLM 对话失败，使用后备对话: {e}")

        # 后备对话
        import random

        greetings = [
            f"你好，{other_agent_name}！欢迎来我的咖啡店！",
            f"嗨 {other_agent_name}！今天想喝点什么吗？",
            f"{other_agent_name}，很高兴见到你！我刚泡了新鲜的咖啡。",
            f"欢迎，{other_agent_name}！坐下来聊聊天吧！",
        ]
        return random.choice(greetings)

    async def respond_to_conversation(self, other_agent_name: str, message: str) -> str:
        """Alice 回应对话"""
        if self.use_llm_for_conversation:
            try:
                return await self._llm_respond_to_conversation(other_agent_name, message)
            except Exception as e:
                print(f"Alice: LLM 回应失败，使用后备回应: {e}")

        # 后备回应逻辑
        import random

        if "咖啡" in message or "coffee" in message.lower():
            responses = [
                "我们有最好的咖啡豆！你想试试今天的特调吗？",
                "咖啡是我的专长！让我为你推荐一款。",
                "刚烘焙的豆子特别香，你一定会喜欢的。",
            ]
        elif "店" in message or "shop" in message.lower():
            responses = [
                "这家店是我的心血，我希望每个人都能感到舒适。",
                "我努力让这里成为大家聚会聊天的好地方。",
                "你觉得店里的氛围怎么样？",
            ]
        elif "朋友" in message or "friend" in message.lower():
            responses = [
                "我很享受和不同的人聊天，每个人都有有趣的故事。",
                "这里的常客都是我的好朋友！",
                "我希望能认识更多像你这样的朋友。",
            ]
        else:
            responses = [
                "真的吗？告诉我更多！",
                "这听起来很有趣！",
                "我喜欢听你这么说。",
                "让我们继续聊下去！",
            ]

        return random.choice(responses)

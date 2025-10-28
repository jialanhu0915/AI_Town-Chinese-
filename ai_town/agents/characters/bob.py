"""
Bob - LLM 增强的书店老板智能体
安静博学的书店经营者，使用大语言模型驱动深度思考和对话
"""

from typing import Any, Dict, List

from ai_town.agents.base_agent import Position
from ai_town.agents.llm_enhanced_agent import LLMEnhancedAgent


class Bob(LLMEnhancedAgent):
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
            "extraversion": 0.4,  # 内向
            "agreeableness": 0.8,  # 友善
            "conscientiousness": 0.9,  # 尽责
            "neuroticism": 0.3,  # 稳定
            "openness": 0.8,  # 开放
        }

        background = (
            "Bob 是一位安静而深思的书店老板，今年47岁。"
            "他经营当地书店已有15年多，对书籍和文学了如指掌。"
            "Bob 喜欢关于哲学、历史和科学的深度对话。"
            "他有点内向，但知识渊博，乐于帮助顾客。"
        )

        # 从配置文件获取 LLM 设置
        from ai_town.config_loader import get_llm_config_for_agent

        llm_config = get_llm_config_for_agent("bob")

        super().__init__(
            agent_id="bob",
            name="Bob",
            age=47,
            personality=personality,
            background=background,
            initial_position=Position(35, 20, "bookstore"),
            occupation="bookstore_owner",
            work_area="bookstore",
            llm_provider=llm_config["provider"],
        )

        # 应用 LLM 配置
        self.use_llm_for_planning = llm_config["use_llm_for_planning"]
        self.use_llm_for_conversation = llm_config["use_llm_for_conversation"]
        self.use_llm_for_reflection = llm_config["use_llm_for_reflection"]

        # Bob 特定的属性
        self.favorite_books = ["philosophy", "history", "science", "literature"]
        self.book_recommendations = {}
        self.reading_preferences = 8.0  # 1-10 scale
        self.customer_interactions = []

    def _define_available_behaviors(self) -> List[str]:
        """Bob 可用的行为类型"""
        return [
            "move",
            "talk",
            "work",  # 基础行为
            "read",
            "organize_books",
            "help_customer",  # 书店相关
            "reflect",
            "research",
            "recommend_book",  # 知识相关
            "eat",
            "sleep",  # 生理需求
        ]

    def _define_behavior_preferences(self) -> Dict[str, float]:
        """Bob 的行为偏好"""
        preferences = super()._define_behavior_preferences()

        # Bob 作为内向的书店老板的特殊偏好
        preferences.update(
            {
                "read": 0.8,  # 非常喜欢阅读
                "organize_books": 0.7,  # 喜欢整理书籍
                "help_customer": 0.6,  # 乐于帮助顾客
                "research": 0.7,  # 喜欢研究
                "recommend_book": 0.8,  # 喜欢推荐书籍
                "socialize": 0.2,  # 不太喜欢一般社交
                "reflect": 0.9,  # 非常喜欢深度思考
                "work": 0.8,  # 工作认真
            }
        )

        return preferences

    def _define_action_durations(self) -> Dict[str, float]:
        """Bob 的行为持续时间"""
        durations = super()._define_action_durations()

        # Bob 的专门行为时间
        durations.update(
            {
                "read": 35.0,  # 读书时间较长
                "organize_books": 20.0,
                "help_customer": 15.0,
                "research": 45.0,  # 研究时间很长
                "recommend_book": 10.0,
                "reflect": 25.0,  # 深度思考时间较长
            }
        )

        return durations

    async def _execute_organize_books_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行整理书籍行动"""
        return {
            "type": "organizing_books",
            "agent_id": self.agent_id,
            "activity": "arranging_shelves",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_help_customer_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行帮助顾客行动"""
        return {
            "type": "customer_service",
            "agent_id": self.agent_id,
            "activity": "helping_customer_find_book",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_research_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行研究行动"""
        topic = self.current_action.get("topic", "literary_analysis")
        return {
            "type": "researching",
            "agent_id": self.agent_id,
            "topic": topic,
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _execute_recommend_book_action(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """执行推荐书籍行动"""
        return {
            "type": "book_recommendation",
            "agent_id": self.agent_id,
            "activity": "suggesting_reading_material",
            "position": {"x": self.position.x, "y": self.position.y, "area": self.position.area},
        }

    async def _generate_insights(self, memories):
        """生成Bob的洞察"""
        insights = []

        # 分析读书相关记忆
        book_memories = [
            m
            for m in memories
            if any(
                word in m.description.lower() for word in ["book", "read", "library", "literature"]
            )
        ]

        if len(book_memories) >= 2:
            insights.append("我一直在思考最近读到的书籍内容。" "每本书都能带来新的视角和思考。")

        # 分析客户互动
        social_memories = [
            m
            for m in memories
            if any(
                word in m.description.lower()
                for word in ["customer", "talk", "conversation", "help"]
            )
        ]

        if len(social_memories) >= 2:
            insights.append(
                "帮助顾客找到合适的书籍让我很有成就感。" "每个人都有自己独特的阅读之旅。"
            )

        # 分析独处时间
        solitude_memories = [
            m
            for m in memories
            if any(word in m.description.lower() for word in ["alone", "quiet", "think", "reflect"])
        ]

        if len(solitude_memories) >= 3:
            insights.append(
                "安静的时光让我能够深入思考和反省。" "有时候独处比社交更能让我获得内心的平静。"
            )

        return insights[:2]

    async def _decide_next_action(self) -> Dict[str, Any]:
        """Bob特定的行为决策"""
        from ai_town.core.time_manager import GameTime

        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()

        # 根据时间和性格特征决定行为
        if time_of_day in ["morning", "afternoon"]:
            # 工作时间，在书店
            if self.position.area != "bookstore":
                return {
                    "type": "move",
                    "position": {"x": 35, "y": 20, "area": "bookstore"},
                    "reason": "去书店工作",
                }
            else:
                # 在书店内的行为
                actions = [
                    {"type": "work", "description": "整理书架"},
                    {"type": "work", "description": "阅读新到的书籍"},
                    {"type": "work", "description": "准备书籍推荐清单"},
                    {"type": "idle", "description": "静静地思考"},
                ]
                import random

                return random.choice(actions)

        elif time_of_day == "evening":
            # 傍晚可能去其他地方放松
            if random.random() < 0.3:  # 30%概率外出
                return {
                    "type": "move",
                    "position": {"x": 50, "y": 50, "area": "park"},
                    "reason": "去公园散步思考",
                }
            else:
                return {"type": "idle", "description": "在书店里继续阅读"}

        else:  # night
            # 夜晚回家或继续在书店
            if self.position.area != "house_2":
                return {
                    "type": "move",
                    "position": {"x": 80, "y": 15, "area": "house_2"},
                    "reason": "回家继续阅读",
                }
            else:
                night_activities = [
                    {"type": "rest", "description": "准备就寝"},
                    {"type": "idle", "description": "思考今天阅读的内容"},
                    {"type": "explore", "description": "研究新的书籍知识"},
                ]
                import random

                return random.choice(night_activities)

    async def _fallback_decide_action(self) -> Dict[str, Any]:
        """Bob 的智能回退决策逻辑"""
        return await self._decide_next_action()

    def _fallback_conversation_response(self, speaker_name: str, message: str) -> str:
        """Bob 特有的对话回应风格 - 深度思考型"""
        message_lower = message.lower()

        # 书籍和文学相关话题
        if any(
            word in message_lower
            for word in ["book", "read", "literature", "story", "author", "novel"]
        ):
            responses = [
                "这让我想起了一本很棒的书，它探讨了类似的主题。你有兴趣了解吗？",
                "阅读真的能开拓我们的视野。每本书都是通向另一个世界的门户。",
                "书籍是人类智慧的结晶，我很乐意和你讨论你感兴趣的任何作品。",
                "我正在读Marcus Aurelius的《沉思录》，里面有很多关于人生的深刻思考。",
            ]

        # 哲学和深度话题
        elif any(
            word in message_lower
            for word in ["philosophy", "meaning", "purpose", "life", "wisdom", "think"]
        ):
            responses = [
                "这是个很有深度的话题。我觉得每个人都应该花时间思考生命的意义。",
                "哲学教会我们如何更好地理解世界和自己。你对此有什么看法？",
                "苏格拉底说过'未经审视的生活不值得过'，我很认同这个观点。",
                "智慧不是知识的积累，而是对真理的不断追寻。",
            ]

        # 历史和知识相关
        elif any(
            word in message_lower
            for word in ["history", "past", "ancient", "civilization", "learn", "knowledge"]
        ):
            responses = [
                "历史是最好的老师，它告诉我们人性的复杂和社会的演进。",
                "了解过去能帮助我们更好地理解现在，甚至预见未来。",
                "知识的价值不在于记住多少，而在于能否用它来理解世界。",
                "每一个时代都有其独特的智慧，值得我们去学习和思考。",
            ]

        # 安静和内省话题
        elif any(
            word in message_lower for word in ["quiet", "peace", "calm", "solitude", "reflection"]
        ):
            responses = [
                "我很享受安静的时光，它让我能够深入思考和反省。",
                "有时候，最好的对话是与自己的内心对话。",
                "在这个喧嚣的世界里，找到内心的平静变得越来越珍贵。",
                "独处并不孤单，它是与自己深度连接的时刻。",
            ]

        # 工作相关
        elif any(word in message_lower for word in ["work", "job", "bookstore", "business"]):
            responses = [
                "经营书店不只是生意，更像是传播知识和文化的使命。",
                "每当看到顾客找到心仪的书籍，我就感到很满足。",
                "书店是思想交流的场所，我很荣幸能够守护这个空间。",
                "好书值得被更多人发现，这是我工作的意义所在。",
            ]

        # 通用深度回应
        else:
            responses = [
                f"这让我想到了很多，{speaker_name}。你能详细说说你的想法吗？",
                "每个观点都有其价值，我很想听听你的深层思考。",
                "这个话题值得我们深入探讨，请继续分享你的见解。",
                "你提出了一个很有趣的观点，让我重新思考这个问题。",
                "谢谢你的分享，这给了我新的思考角度。",
            ]

        import random

        return random.choice(responses)

    def get_book_recommendation(self, genre: str = None) -> str:
        """根据类型推荐书籍"""
        recommendations = {
            "philosophy": [
                "《沉思录》- Marcus Aurelius 的智慧结晶",
                "《理想国》- 柏拉图对正义的深度思考",
                "《存在与时间》- 海德格尔的存在主义杰作",
            ],
            "literature": [
                "《百年孤独》- 魔幻现实主义的经典",
                "《卡拉马佐夫兄弟》- 陀思妥耶夫斯基的巨著",
                "《追忆似水年华》- 普鲁斯特的时间艺术",
            ],
            "history": [
                "《人类简史》- 尤瓦尔·赫拉利的宏观视角",
                "《史记》- 司马迁的史学巨著",
                "《罗马帝国衰亡史》- 吉本的经典史学作品",
            ],
        }

        if genre and genre in recommendations:
            import random

            return random.choice(recommendations[genre])
        else:
            # 随机推荐
            all_books = []
            for books in recommendations.values():
                all_books.extend(books)
            import random

            return random.choice(all_books)

    async def decide_next_action(self) -> Dict[str, Any]:
        """Bob 的主要决策方法"""
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
                print(f"Bob: LLM 决策失败，使用后备决策: {e}")

        # 后备决策逻辑
        return await self._decide_next_action()

    async def start_conversation(self, other_agent_name: str, topic: str = "") -> str:
        """Bob 开始对话"""
        if self.use_llm_for_conversation:
            try:
                return await self._llm_start_conversation(other_agent_name, topic)
            except Exception as e:
                print(f"Bob: LLM 对话失败，使用后备对话: {e}")

        # 后备对话
        import random

        greetings = [
            f"你好，{other_agent_name}。欢迎来我的书店。",
            f"{other_agent_name}，今天想找什么类型的书吗？",
            f"嗨 {other_agent_name}，我这里有些新到的好书。",
            f"很高兴见到你，{other_agent_name}。有什么我可以帮助的吗？",
        ]
        return random.choice(greetings)

    async def respond_to_conversation(self, other_agent_name: str, message: str) -> str:
        """Bob 回应对话"""
        if self.use_llm_for_conversation:
            try:
                return await self._llm_respond_to_conversation(other_agent_name, message)
            except Exception as e:
                print(f"Bob: LLM 回应失败，使用后备回应: {e}")

        # 后备回应逻辑
        import random

        if "书" in message or "book" in message.lower():
            responses = [
                "我有很多好书推荐！你喜欢什么类型？",
                "书籍是知识的海洋，让我为你找到合适的。",
                "这里的每本书都有它独特的价值。",
            ]
        elif "知识" in message or "学习" in message or "knowledge" in message.lower():
            responses = [
                "知识确实是最宝贵的财富。",
                "学习是终生的追求，我很佩服你的态度。",
                "书本中藏着无数智慧，值得我们去发现。",
            ]
        elif "安静" in message or "quiet" in message.lower():
            responses = [
                "我喜欢这里的宁静，它让人能专心思考。",
                "安静的环境确实有助于阅读和思考。",
                "有时候，最好的对话就是与书本的无声交流。",
            ]
        else:
            responses = [
                "这是个深刻的观察。",
                "你说得很有道理。",
                "我从未这样想过，很有启发。",
                "请继续，我很感兴趣。",
            ]

        return random.choice(responses)

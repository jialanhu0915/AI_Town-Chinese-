"""
LLM 增强的智能体基类
为智能体添加大语言模型驱动的推理和决策能力
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime

from ai_town.agents.base_agent import BaseAgent, Position, Observation
from ai_town.llm.llm_integration import llm_manager, ask_llm, chat_with_llm
from ai_town.core.time_manager import GameTime


class LLMEnhancedAgent(BaseAgent):
    """LLM 增强的智能体基类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # LLM 相关配置
        self.preferred_llm_provider = kwargs.get('llm_provider', 'mock')
        self.use_llm_for_planning = True
        self.use_llm_for_conversation = True
        self.use_llm_for_reflection = True
        
        # 对话历史
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        
        # 当前思考状态
        self.current_thoughts = ""
        self.current_goals = []
    
    async def _generate_insights(self, memories: List[Observation]) -> List[str]:
        """使用 LLM 生成基于记忆的洞察"""
        if not self.use_llm_for_reflection or not memories:
            return await self._fallback_generate_insights(memories)
        
        # 准备记忆摘要
        memory_summaries = []
        for memory in memories[-10:]:  # 最近10条记忆
            summary = f"[{memory.timestamp.strftime('%H:%M')}] {memory.description}"
            memory_summaries.append(summary)
        
        memories_text = "\n".join(memory_summaries)
        
        # 构建反思提示
        reflection_prompt = f"""
你是 {self.name}，{self.age}岁，职业是{self.occupation}。

你的背景: {self.background}

你的性格特征:
- 外向性: {self.personality.get('extraversion', 0.5):.1f} (0=内向, 1=外向)
- 宜人性: {self.personality.get('agreeableness', 0.5):.1f} (0=冷漠, 1=友善)
- 尽责性: {self.personality.get('conscientiousness', 0.5):.1f} (0=散漫, 1=负责)
- 神经质: {self.personality.get('neuroticism', 0.5):.1f} (0=稳定, 1=焦虑)
- 开放性: {self.personality.get('openness', 0.5):.1f} (0=保守, 1=开放)

最近的经历和记忆:
{memories_text}

当前时间: {GameTime.format_time()}
当前心情: {self.mood:.1f} (-1=糟糕, 1=很好)
当前能量: {self.energy:.1f}%

请基于这些记忆和经历，生成2-3个深入的个人洞察或反思。这些洞察应该:
1. 符合你的性格特征
2. 反映你对最近经历的思考
3. 可能影响你未来的行为决策
4. 用第一人称表达

请只返回洞察内容，每行一个洞察，不需要其他解释。
"""

        try:
            response = await ask_llm(
                reflection_prompt, 
                provider=self.preferred_llm_provider,
                context={'agent': self.name, 'task': 'reflection'}
            )
            
            # 解析洞察
            insights = [line.strip() for line in response.split('\n') if line.strip()]
            return insights[:3]  # 最多返回3个洞察
            
        except Exception as e:
            print(f"LLM reflection failed for {self.name}: {e}")
            return await self._fallback_generate_insights(memories)
    
    async def _fallback_generate_insights(self, memories: List[Observation]) -> List[str]:
        """回退到基于规则的洞察生成"""
        insights = []
        
        # 简单的基于规则的洞察
        if len(memories) >= 5:
            insights.append(f"我注意到最近发生了很多事情，需要好好整理一下思绪。")
        
        # 基于心情的洞察
        if self.mood > 0.5:
            insights.append("最近心情不错，感觉生活很充实。")
        elif self.mood < -0.5:
            insights.append("最近有些烦躁，可能需要调整一下节奏。")
        
        # 基于能量的洞察
        if self.energy < 30:
            insights.append("感觉有些疲惫，需要好好休息一下。")
        
        return insights[:2]
    
    async def _decide_next_action(self) -> Dict[str, Any]:
        """使用 LLM 决定下一个行动"""
        if not self.use_llm_for_planning:
            return await self._fallback_decide_action()
        
        # 获取当前情境信息
        current_time = GameTime.now()
        time_of_day = GameTime.get_time_of_day()
        recent_memories = self.memory.get_recent_memories(limit=5)
        
        # 构建决策提示
        memory_context = ""
        if recent_memories:
            memory_context = "最近的经历:\n" + "\n".join([
                f"- {mem.description}" for mem in recent_memories
            ])
        
        decision_prompt = f"""
你是 {self.name}，{self.age}岁，职业是{self.occupation}。

你的背景: {self.background}

你的性格特征:
- 外向性: {self.personality.get('extraversion', 0.5):.1f}
- 宜人性: {self.personality.get('agreeableness', 0.5):.1f}
- 尽责性: {self.personality.get('conscientiousness', 0.5):.1f}
- 神经质: {self.personality.get('neuroticism', 0.5):.1f}
- 开放性: {self.personality.get('openness', 0.5):.1f}

当前状态:
- 时间: {GameTime.format_time()} ({time_of_day})
- 位置: {self.position.area}
- 心情: {self.mood:.1f} (-1=糟糕, 1=很好)
- 能量: {self.energy:.1f}%

{memory_context}

可用的行动类型:
1. move - 移动到其他地方 (需要指定目标位置和原因)
2. work - 工作相关活动 (需要描述具体工作内容)
3. socialize - 社交活动 (需要描述社交意图)
4. rest - 休息或放松 (需要描述休息方式)
5. explore - 探索或学习新事物 (需要描述探索内容)
6. idle - 待机或思考 (需要描述在想什么)

请基于你的性格、当前状态和最近经历，决定下一个最合适的行动。

请以JSON格式返回决策，格式如下:
{{
    "type": "行动类型",
    "description": "详细描述你要做什么",
    "reason": "为什么选择这个行动",
    "duration": 预计持续时间（分钟）
}}

只返回JSON，不需要其他说明。
"""

        try:
            response = await ask_llm(
                decision_prompt,
                provider=self.preferred_llm_provider,
                context={'agent': self.name, 'task': 'decision_making'}
            )
            
            # 尝试解析JSON响应
            try:
                action = json.loads(response.strip())
                
                # 验证必需字段
                if 'type' in action and 'description' in action:
                    return action
                else:
                    raise ValueError("Missing required fields in LLM response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse LLM action for {self.name}: {e}")
                print(f"Raw response: {response}")
                return await self._fallback_decide_action()
                
        except Exception as e:
            print(f"LLM decision making failed for {self.name}: {e}")
            return await self._fallback_decide_action()
    
    async def _fallback_decide_action(self) -> Dict[str, Any]:
        """回退到基于规则的行动决策"""
        # 这里调用原来的简单决策逻辑
        # 子类可以重写这个方法
        return {
            'type': 'idle',
            'description': '静静地思考',
            'reason': '没有特别想做的事情',
            'duration': 5
        }
    
    async def generate_conversation_response(self, speaker_name: str, message: str, context: Dict[str, Any] = None) -> str:
        """使用 LLM 生成对话响应"""
        if not self.use_llm_for_conversation:
            return self._fallback_conversation_response(speaker_name, message)
        
        # 获取与此人的对话历史
        conversation_key = f"{self.agent_id}-{speaker_name}"
        if conversation_key not in self.conversation_history:
            self.conversation_history[conversation_key] = []
        
        history = self.conversation_history[conversation_key]
        
        # 构建对话提示
        conversation_prompt = f"""
你是 {self.name}，正在与 {speaker_name} 对话。

你的背景: {self.background}

你的性格特征:
- 外向性: {self.personality.get('extraversion', 0.5):.1f} (影响你的话多话少)
- 宜人性: {self.personality.get('agreeableness', 0.5):.1f} (影响你的友善程度)
- 尽责性: {self.personality.get('conscientiousness', 0.5):.1f} (影响你的谈话深度)

当前状态:
- 心情: {self.mood:.1f} (-1=糟糕, 1=很好)
- 时间: {GameTime.format_time()}
- 地点: {self.position.area}

对话历史:
"""
        
        # 添加对话历史
        for msg in history[-6:]:  # 最近6轮对话
            conversation_prompt += f"{msg['role']}: {msg['content']}\n"
        
        conversation_prompt += f"\n{speaker_name}: {message}\n\n"
        conversation_prompt += f"""
请生成 {self.name} 的回应。回应应该:
1. 符合你的性格特征和背景
2. 考虑当前的心情和状态
3. 自然地延续对话
4. 不超过2-3句话
5. 用中文回复

只返回对话内容，不需要其他格式或说明。
"""
        
        try:
            response = await ask_llm(
                conversation_prompt,
                provider=self.preferred_llm_provider,
                context={'agent': self.name, 'task': 'conversation'}
            )
            
            # 更新对话历史
            history.append({"role": speaker_name, "content": message})
            history.append({"role": self.name, "content": response})
            
            # 保持历史长度
            if len(history) > 20:
                history = history[-20:]
            
            self.conversation_history[conversation_key] = history
            
            return response.strip()
            
        except Exception as e:
            print(f"LLM conversation failed for {self.name}: {e}")
            return self._fallback_conversation_response(speaker_name, message)
    
    def _fallback_conversation_response(self, speaker_name: str, message: str) -> str:
        """回退的对话响应"""
        responses = [
            "是的，我明白你的意思。",
            "这很有趣！",
            "你说得对。",
            "我也有同感。",
            f"谢谢你告诉我这个，{speaker_name}。"
        ]
        
        import random
        return random.choice(responses)
    
    async def set_goals(self, goals: List[str]):
        """设置当前目标"""
        self.current_goals = goals
        
        # 将目标记录为记忆
        goal_text = "我设定了新的目标: " + ", ".join(goals)
        goal_memory = Observation(
            timestamp=GameTime.now(),
            observer_id=self.agent_id,
            event_type="goal_setting",
            description=goal_text,
            location=self.position,
            importance=8.0,
            metadata={'goals': goals}
        )
        self.memory.add_observation(goal_memory)
    
    def get_current_thoughts(self) -> str:
        """获取当前思考内容"""
        return self.current_thoughts
    
    def update_thoughts(self, thoughts: str):
        """更新当前思考"""
        self.current_thoughts = thoughts
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """获取增强状态信息"""
        base_status = self.get_status()
        base_status.update({
            'llm_provider': self.preferred_llm_provider,
            'current_thoughts': self.current_thoughts,
            'current_goals': self.current_goals,
            'conversation_partners': list(self.conversation_history.keys())
        })
        return base_status

    async def _llm_decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用 LLM 决定下一个行为"""
        from ai_town.llm.llm_integration import ask_llm
        
        # 构建决策上下文
        personality_desc = f"你是{self.name}，{self.age}岁，{self.occupation}。{self.background}"
        
        situation_desc = (
            f"当前时间: {context.get('current_time', '未知')}，"
            f"位置: {context.get('position', {}).get('area', '未知区域')}。"
        )
        
        memory_desc = "最近经历: " + "; ".join(context.get('recent_memories', [])) if context.get('recent_memories') else "暂无最近经历"
        
        # 构建决策提示
        decision_prompt = f"""
{personality_desc}

{situation_desc}

{memory_desc}

基于你的性格、当前情况和最近经历，你接下来想要做什么？
请从以下行为类型中选择一个，并说明原因：

1. move - 移动到新位置
2. work - 工作相关活动
3. socialize - 社交互动
4. explore - 探索环境
5. relax - 放松休息
6. think - 思考反思
7. sleep - 睡觉休息

请以JSON格式回答，包含type、description和reason字段。

例如：
{{"type": "work", "description": "整理书架", "reason": "现在是工作时间，需要维护好书店"}}
"""

        try:
            # 调用 LLM
            llm_response = await ask_llm(decision_prompt, provider=self.preferred_llm_provider)
            
            # 解析 LLM 响应
            import json
            try:
                decision = json.loads(llm_response.strip())
                return {
                    'type': decision.get('type', 'think'),
                    'description': decision.get('description', '思考当前情况'),
                    'reason': decision.get('reason', '')
                }
            except json.JSONDecodeError:
                # LLM 返回格式有误，返回默认行为
                return {
                    'type': 'think',
                    'description': '思考当前情况',
                    'reason': 'LLM响应解析失败'
                }
        
        except Exception as e:
            # LLM 调用失败
            return {
                'type': 'think',
                'description': '思考当前情况',
                'reason': f'LLM调用失败: {e}'
            }
    
    async def _llm_start_conversation(self, other_agent_name: str, topic: str = "") -> str:
        """使用 LLM 开始对话"""
        from ai_town.llm.llm_integration import ask_llm
        
        personality_desc = f"你是{self.name}，{self.age}岁，{self.occupation}。{self.background}"
        
        conversation_prompt = f"""
{personality_desc}

你想要和 {other_agent_name} 开始一段对话。
{f'话题是: {topic}' if topic else '可以是任何你感兴趣的话题。'}

请生成一个自然、友好的开场白，符合你的性格特征。
直接回答对话内容，不需要引号或格式。
"""

        try:
            response = await ask_llm(conversation_prompt, provider=self.preferred_llm_provider)
            return response.strip()
        except Exception as e:
            # 后备开场白
            return f"你好，{other_agent_name}！很高兴见到你。"
    
    async def _llm_respond_to_conversation(self, other_agent_name: str, message: str) -> str:
        """使用 LLM 回应对话"""
        from ai_town.llm.llm_integration import chat_with_llm
        
        # 获取或初始化对话历史
        if other_agent_name not in self.conversation_history:
            self.conversation_history[other_agent_name] = []
        
        conversation_history = self.conversation_history[other_agent_name]
        
        # 构建对话上下文
        personality_desc = f"你是{self.name}，{self.age}岁，{self.occupation}。{self.background}"
        
        messages = [
            {"role": "system", "content": personality_desc},
            {"role": "system", "content": f"你正在和 {other_agent_name} 对话。请保持你的性格特征，给出自然的回应。"}
        ]
        
        # 添加对话历史（最近5轮）
        for msg in conversation_history[-10:]:
            messages.append(msg)
        
        # 添加当前消息
        messages.append({"role": "user", "content": f"{other_agent_name}: {message}"})
        
        try:
            response = await chat_with_llm(messages, provider=self.preferred_llm_provider)
            
            # 保存对话历史
            conversation_history.append({"role": "user", "content": f"{other_agent_name}: {message}"})
            conversation_history.append({"role": "assistant", "content": response})
            
            # 限制对话历史长度
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                self.conversation_history[other_agent_name] = conversation_history
            
            return response.strip()
            
        except Exception as e:
            # 后备回应
            return f"谢谢你告诉我这些，{other_agent_name}。"

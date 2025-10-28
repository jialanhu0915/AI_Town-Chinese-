"""
AI Town LLM 集成模块
支持多种大语言模型后端
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM 响应数据结构"""

    content: str
    reasoning: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = None


class LLMProvider(ABC):
    """LLM 提供者抽象基类"""

    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        """生成文本响应"""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """对话模式"""
        pass


class OllamaProvider(LLMProvider):
    """Ollama 本地 LLM 提供者"""

    def __init__(self, model_name: str = "tinyllama", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        """使用 Ollama 生成响应"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 500},
                },
            )

            if response.status_code == 200:
                result = response.json()
                return LLMResponse(
                    content=result.get("response", "").strip(),
                    metadata={"model": self.model_name, "provider": "ollama"},
                )
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return LLMResponse(content="[LLM Error: Unable to generate response]")

        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return LLMResponse(content="[LLM Error: Connection failed]")

    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """对话模式"""
        # 将消息转换为单个 prompt
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"

        prompt += "Assistant: "
        return await self.generate(prompt)

    async def aclose(self):
        try:
            await self.client.aclose()
        except Exception:
            pass


class OpenAIProvider(LLMProvider):
    """OpenAI API 提供者"""

    def __init__(self, api_key: str = None, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}, timeout=60.0
        )

    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        """使用 OpenAI API 生成响应"""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """对话模式"""
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return LLMResponse(
                    content=content.strip(),
                    metadata={"model": self.model_name, "provider": "openai"},
                )
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return LLMResponse(content="[LLM Error: API request failed]")

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(content="[LLM Error: Connection failed]")

    async def aclose(self):
        try:
            await self.client.aclose()
        except Exception:
            pass


class MockLLMProvider(LLMProvider):
    """模拟 LLM 提供者（用于测试和演示）"""

    def __init__(self):
        self.responses = {
            "greeting": ["你好！很高兴见到你。", "嗨！今天过得怎么样？", "欢迎来到小镇！"],
            "work": ["我正在努力工作。", "工作很充实。", "今天的任务进展顺利。"],
            "social": ["和朋友聊天总是很愉快。", "我喜欢认识新朋友。", "社交让生活更有趣。"],
            "default": ["这很有趣。", "我需要仔细想想。", "让我考虑一下。"],
        }

    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        """生成模拟响应"""
        import random

        # 简单的关键词匹配
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["你好", "hello", "嗨", "hi"]):
            response_type = "greeting"
        elif any(word in prompt_lower for word in ["工作", "work", "job"]):
            response_type = "work"
        elif any(word in prompt_lower for word in ["朋友", "friend", "社交", "social"]):
            response_type = "social"
        else:
            response_type = "default"

        content = random.choice(self.responses[response_type])

        # 模拟延迟
        await asyncio.sleep(0.1)

        return LLMResponse(
            content=content,
            confidence=0.8,
            metadata={"provider": "mock", "response_type": response_type},
        )

    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """对话模式"""
        if messages:
            last_message = messages[-1].get("content", "")
            return await self.generate(last_message)
        return await self.generate("hello")


class DeepSeekProvider(LLMProvider):
    """DeepSeek API 提供商（OpenAI 兼容风格）"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}, timeout=60.0
        )

    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        try:
            url = f"{self.base_url}/v1/chat/completions"
            response = await self.client.post(
                url,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return LLMResponse(
                    content=content.strip(),
                    metadata={"model": self.model_name, "provider": "deepseek"},
                )
            else:
                logger.error(f"DeepSeek API error: {response.status_code} {response.text}")
                return LLMResponse(content="[LLM Error: API request failed]")
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return LLMResponse(content="[LLM Error: Connection failed]")

    async def aclose(self):
        try:
            await self.client.aclose()
        except Exception:
            pass


class KimiProvider(LLMProvider):
    """Kimi(Moonshot) 提供商（OpenAI 兼容风格）"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "moonshot-v1-8k",
        base_url: str = "https://api.moonshot.cn",
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}, timeout=60.0
        )

    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        try:
            url = f"{self.base_url}/v1/chat/completions"
            response = await self.client.post(
                url,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return LLMResponse(
                    content=content.strip(),
                    metadata={"model": self.model_name, "provider": "kimi"},
                )
            else:
                logger.error(f"Kimi API error: {response.status_code} {response.text}")
                return LLMResponse(content="[LLM Error: API request failed]")
        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            return LLMResponse(content="[LLM Error: Connection failed]")

    async def aclose(self):
        try:
            await self.client.aclose()
        except Exception:
            pass


class QwenProvider(LLMProvider):
    """Qwen 通义千问提供商（DashScope 兼容模式）"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen-plus",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode",
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}, timeout=60.0
        )

    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        try:
            url = f"{self.base_url}/v1/chat/completions"
            response = await self.client.post(
                url,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return LLMResponse(
                    content=content.strip(),
                    metadata={"model": self.model_name, "provider": "qwen"},
                )
            else:
                logger.error(f"Qwen API error: {response.status_code} {response.text}")
                return LLMResponse(content="[LLM Error: API request failed]")
        except Exception as e:
            logger.error(f"Qwen API error: {e}")
            return LLMResponse(content="[LLM Error: Connection failed]")

    async def aclose(self):
        try:
            await self.client.aclose()
        except Exception:
            pass


class LLMManager:
    """LLM 管理器 - 管理多个 LLM 提供者"""

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider = None
        self.fallback_providers: List[str] = []

    def register_provider(self, name: str, provider: LLMProvider, is_default: bool = False):
        """注册 LLM 提供者"""
        self.providers[name] = provider
        if is_default or self.default_provider is None:
            self.default_provider = name

    def set_fallback_chain(self, provider_names: List[str]):
        """设置故障转移链"""
        self.fallback_providers = provider_names

    async def generate(
        self, prompt: str, provider_name: str = None, context: Dict[str, Any] = None
    ) -> LLMResponse:
        """生成响应（支持故障转移）"""
        providers_to_try = []

        if provider_name and provider_name in self.providers:
            providers_to_try.append(provider_name)

        if self.default_provider:
            providers_to_try.append(self.default_provider)

        providers_to_try.extend(self.fallback_providers)

        # 去重并保持顺序
        providers_to_try = list(dict.fromkeys(providers_to_try))

        for provider_name in providers_to_try:
            if provider_name in self.providers:
                try:
                    response = await self.providers[provider_name].generate(prompt, context)
                    if response.content and not response.content.startswith("[LLM Error"):
                        return response
                except Exception as e:
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    continue

        # 所有提供者都失败了
        return LLMResponse(content="[LLM 提供者都不可用]")

    async def chat(self, messages: List[Dict[str, str]], provider_name: str = None) -> LLMResponse:
        """对话模式（支持故障转移）"""
        providers_to_try = []

        if provider_name and provider_name in self.providers:
            providers_to_try.append(provider_name)

        if self.default_provider:
            providers_to_try.append(self.default_provider)

        providers_to_try.extend(self.fallback_providers)
        providers_to_try = list(dict.fromkeys(providers_to_try))

        for provider_name in providers_to_try:
            if provider_name in self.providers:
                try:
                    response = await self.providers[provider_name].chat(messages)
                    if response.content and not response.content.startswith("[LLM Error"):
                        return response
                except Exception as e:
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    continue

        return LLMResponse(content="[LLM 提供者都不可用]")

    def get_available_providers(self) -> List[str]:
        """获取可用的提供者列表"""
        return list(self.providers.keys())

    async def shutdown(self):
        """关闭所有 provider 的异步客户端"""
        for provider in list(self.providers.values()):
            aclose = getattr(provider, "aclose", None)
            if callable(aclose):
                try:
                    await aclose()
                except Exception:
                    pass


# 全局 LLM 管理器实例
llm_manager = LLMManager()


def setup_default_llm_providers():
    """设置默认的 LLM 提供者"""
    from ai_town.config import LLM_CONFIG
    from ai_town.config_loader import load_env_file

    # 加载配置文件
    load_env_file()

    # 注册模拟提供者（始终可用）
    mock_provider = MockLLMProvider()
    llm_manager.register_provider("mock", mock_provider)

    # 根据配置注册 Ollama
    ollama_config = LLM_CONFIG.get("ollama", {})
    if ollama_config.get("enabled", True):
        try:
            model_name = ollama_config.get("model_name", "deepseek-r1:1.5b")
            base_url = ollama_config.get("base_url", "http://localhost:11434")
            ollama_provider = OllamaProvider(model_name=model_name, base_url=base_url)

            is_default = LLM_CONFIG.get("default_provider") == "ollama"
            llm_manager.register_provider("ollama", ollama_provider, is_default=is_default)
            logger.info(f"Ollama provider registered with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to register Ollama provider: {e}")

    # 根据配置注册 OpenAI
    openai_config = LLM_CONFIG.get("openai", {})
    openai_key = openai_config.get("api_key") or os.getenv("OPENAI_API_KEY")
    if openai_config.get("enabled", False) and openai_key:
        try:
            model_name = openai_config.get("model_name", "gpt-3.5-turbo")
            openai_provider = OpenAIProvider(openai_key, model_name)

            is_default = LLM_CONFIG.get("default_provider") == "openai"
            llm_manager.register_provider("openai", openai_provider, is_default=is_default)
            logger.info(f"OpenAI provider registered with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to register OpenAI provider: {e}")

    # 根据配置注册 DeepSeek
    deepseek_config = LLM_CONFIG.get("deepseek", {})
    deepseek_key = deepseek_config.get("api_key") or os.getenv("DEEPSEEK_API_KEY")
    if deepseek_config.get("enabled", False) and deepseek_key:
        try:
            model_name = deepseek_config.get("model_name", "deepseek-chat")
            base_url = deepseek_config.get("base_url", "https://api.deepseek.com")
            deepseek_provider = DeepSeekProvider(deepseek_key, model_name, base_url)

            is_default = LLM_CONFIG.get("default_provider") == "deepseek"
            llm_manager.register_provider("deepseek", deepseek_provider, is_default=is_default)
            logger.info(f"DeepSeek provider registered with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to register DeepSeek provider: {e}")

    # 根据配置注册 Kimi(Moonshot)
    kimi_config = LLM_CONFIG.get("kimi", {}) or LLM_CONFIG.get("moonshot", {})
    kimi_key = (
        kimi_config.get("api_key") or os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")
    )
    if kimi_config.get("enabled", False) and kimi_key:
        try:
            model_name = kimi_config.get("model_name", "moonshot-v1-8k")
            base_url = kimi_config.get("base_url", "https://api.moonshot.cn")
            kimi_provider = KimiProvider(kimi_key, model_name, base_url)

            is_default = LLM_CONFIG.get("default_provider") == "kimi"
            llm_manager.register_provider("kimi", kimi_provider, is_default=is_default)
            logger.info(f"Kimi provider registered with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to register Kimi provider: {e}")

    # 根据配置注册 Qwen (DashScope 兼容模式)
    qwen_config = LLM_CONFIG.get("qwen", {}) or LLM_CONFIG.get("dashscope", {})
    qwen_key = (
        qwen_config.get("api_key")
        or os.getenv("DASHSCOPE_API_KEY")
        or os.getenv("DASH_SCOPE_API_KEY")
    )
    if qwen_config.get("enabled", False) and qwen_key:
        try:
            model_name = qwen_config.get("model_name", "qwen-plus")
            base_url = qwen_config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode")
            qwen_provider = QwenProvider(qwen_key, model_name, base_url)

            is_default = LLM_CONFIG.get("default_provider") == "qwen"
            llm_manager.register_provider("qwen", qwen_provider, is_default=is_default)
            logger.info(f"Qwen provider registered with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to register Qwen provider: {e}")

    # 设置故障转移链
    fallback_chain = LLM_CONFIG.get(
        "fallback_chain",
        ["ollama", "openai", "deepseek", "kimi", "qwen", "mock"],
    )
    llm_manager.set_fallback_chain(fallback_chain)

    logger.info(f"Available LLM providers: {llm_manager.get_available_providers()}")
    logger.info(f"Default provider: {LLM_CONFIG.get('default_provider', 'ollama')}")
    logger.info(f"Fallback chain: {' -> '.join(fallback_chain)}")


# 便捷函数
async def ask_llm(prompt: str, provider: str = None, context: Dict[str, Any] = None) -> str:
    """便捷的 LLM 查询函数"""
    response = await llm_manager.generate(prompt, provider, context)
    return response.content


async def chat_with_llm(messages: List[Dict[str, str]], provider: str = None) -> str:
    """便捷的 LLM 对话函数"""
    response = await llm_manager.chat(messages, provider)
    return response.content


# 在进程退出时尽量优雅关闭异步客户端，避免 Windows 上的 Unraisable 警告
import atexit as _atexit


def _shutdown_llms_sync():
    try:
        import asyncio as _asyncio

        _asyncio.run(llm_manager.shutdown())
    except Exception:
        # 若事件循环环境不允许，忽略
        pass


_atexit.register(_shutdown_llms_sync)

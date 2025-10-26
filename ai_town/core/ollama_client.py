import subprocess
import json
from typing import Optional, List, Dict

class OllamaClient:
    """简易 Ollama 客户端：优先尝试 HTTP（如果可用），否则回退到 CLI 调用。

    这里实现一个最小封装，仅支持发送 prompt 并接收文本回复。
    """

    def __init__(self, model: str = "llama2"):
        self.model = model

    def chat_cli(self, prompt: str, system: Optional[str] = None) -> str:
        cmd = ["ollama", "generate", self.model, "--prompt", prompt]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return proc.stdout
        except Exception as e:
            raise RuntimeError(f"Ollama CLI 调用失败: {e}")

    def chat(self, prompt: str, system: Optional[str] = None) -> str:
        # 目前仅使用 CLI 方式；后续可扩展为 HTTP
        return self.chat_cli(prompt, system)

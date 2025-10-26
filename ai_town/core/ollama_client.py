import subprocess
import json
import shutil
from typing import Optional

import httpx


class OllamaClient:
    """Ollama 客户端封装。

    优先尝试本地 HTTP 接口（默认 http://localhost:11434），若不可用则回退到系统中的 ollama CLI。

    用法示例：
        client = OllamaClient(model='llama2')
        resp = client.chat('你好')
    """

    def __init__(self, model: str = "llama2", http_url: str = "http://localhost:11434", cli_cmd: str = "ollama"):
        self.model = model
        self.http_url = http_url.rstrip('/')
        self.cli_cmd = cli_cmd
        self._http_available: Optional[bool] = None

    def _check_http(self, timeout: float = 1.0) -> bool:
        if self._http_available is not None:
            return self._http_available
        try:
            # 尝试访问根路径，若有运行中的 Ollama 会返回某些信息或可达
            httpx.get(self.http_url, timeout=timeout)
            self._http_available = True
        except Exception:
            self._http_available = False
        return self._http_available

    def chat_http(self, prompt: str, system: Optional[str] = None, history: Optional[list] = None, temperature: float = 0.0, timeout: int = 30) -> str:
        """通过 HTTP 调用 Ollama。本函数尝试常见的两个路径（/api/generate, /generate），并返回文本响应."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
        }
        # 有些 Ollama 版本使用 /api/generate 或 /generate
        candidates = [f"{self.http_url}/api/generate", f"{self.http_url}/generate"]
        for url in candidates:
            try:
                r = httpx.post(url, json=payload, timeout=timeout)
            except Exception:
                continue
            if r is None:
                continue
            if r.status_code != 200:
                # 非 200 继续尝试其它 endpoint
                continue
            # 尝试解析 json 格式，否则返回文本
            try:
                body = r.json()
            except Exception:
                return r.text
            # 常见返回可能为字符串或包含 text/content 字段
            if isinstance(body, str):
                return body
            if isinstance(body, dict):
                # 尝试常见字段
                for key in ("text", "content", "response", "result"):
                    if key in body and isinstance(body[key], str):
                        return body[key]
                # 否则返回序列化后的 json
                return json.dumps(body)
        raise RuntimeError("没有可用的 Ollama HTTP 接口（尝试 /api/generate 和 /generate）或请求失败")

    def _has_cli(self) -> bool:
        return shutil.which(self.cli_cmd) is not None

    def chat_cli(self, prompt: str, system: Optional[str] = None, history: Optional[list] = None) -> str:
        """通过 ollama CLI 调用模型。返回 stdout（字符串）。"""
        if not self._has_cli():
            raise RuntimeError("Ollama CLI 未在 PATH 中找到")
        cmd = [self.cli_cmd, "generate", self.model, "--prompt", prompt]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return proc.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ollama CLI 调用失败: {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"调用 Ollama CLI 出错: {e}") from e

    def chat(self, prompt: str, system: Optional[str] = None, history: Optional[list] = None, temperature: float = 0.0, timeout: int = 30) -> str:
        """统一入口：优先 HTTP，失败后回退到 CLI；两者均失败时抛出异常."""
        # 优先使用 HTTP
        try:
            if self._check_http():
                return self.chat_http(prompt, system=system, history=history, temperature=temperature, timeout=timeout)
        except Exception:
            # 忽略 HTTP 错误，回退到 CLI
            pass

        # 回退到 CLI
        try:
            return self.chat_cli(prompt, system=system, history=history)
        except Exception as e:
            raise RuntimeError("HTTP 和 CLI 调用均失败，请检查 Ollama 是否在本机启动或 ollama CLI 是否安装并在 PATH 中") from e


__all__ = ["OllamaClient"]

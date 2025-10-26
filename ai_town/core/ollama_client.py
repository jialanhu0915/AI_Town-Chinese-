import subprocess
import json
import shutil
import os
from typing import Optional, List, Union

import httpx


class OllamaClient:
    """Ollama 客户端封装。

    优先尝试本地 HTTP 接口（默认 http://localhost:11434），若不可用则回退到系统中的 ollama CLI。

    支持 chat(...) 与 embeddings(...)（best-effort：优先 HTTP，回退 CLI，若都不可用则抛出异常）。

    环境变量支持：
    - OLLAMA_FORCE_CLI=1    强制使用 CLI（跳过 HTTP 检测），适合离线或不想等待 HTTP 超时的场景
    - OLLAMA_HTTP_TIMEOUT   调整 HTTP 检测/请求的超时时间（秒，默认 0.5）
    """

    def __init__(self, model: str = "llama2", http_url: str = "http://localhost:11434", cli_cmd: str = "ollama"):
        self.model = model
        self.http_url = http_url.rstrip('/')
        self.cli_cmd = cli_cmd
        self._http_available: Optional[bool] = None
        # 从环境读取配置
        self.force_cli = os.environ.get('OLLAMA_FORCE_CLI', '').lower() in ('1', 'true', 'yes')
        try:
            self.http_timeout = float(os.environ.get('OLLAMA_HTTP_TIMEOUT', '0.5'))
        except Exception:
            self.http_timeout = 0.5

    def _check_http(self, timeout: float = None) -> bool:
        """快速检测本地 Ollama HTTP 服务是否可用。尊重 self.force_cli 并使用短超时，避免离线时长时间阻塞。"""
        if self.force_cli:
            self._http_available = False
            return False
        if self._http_available is not None:
            return self._http_available
        if timeout is None:
            timeout = self.http_timeout
        try:
            # 使用短超时；只用于检测服务是否在本地运行
            httpx.get(self.http_url, timeout=timeout)
            self._http_available = True
        except Exception:
            self._http_available = False
        return self._http_available

    # ----------------- Chat / Generate -----------------
    def chat_http(self, prompt: str, system: Optional[str] = None, history: Optional[list] = None, temperature: float = 0.0, timeout: int = None) -> str:
        if timeout is None:
            timeout = max(1.0, self.http_timeout)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
        }
        candidates = [f"{self.http_url}/api/generate", f"{self.http_url}/generate"]
        for url in candidates:
            try:
                r = httpx.post(url, json=payload, timeout=timeout)
            except Exception:
                continue
            if r is None:
                continue
            if r.status_code != 200:
                continue
            try:
                body = r.json()
            except Exception:
                return r.text
            if isinstance(body, str):
                return body
            if isinstance(body, dict):
                for key in ("text", "content", "response", "result"):
                    if key in body and isinstance(body[key], str):
                        return body[key]
                return json.dumps(body)
        raise RuntimeError("没有可用的 Ollama HTTP 接口（尝试 /api/generate 和 /generate）或请求失败")

    def chat_cli(self, prompt: str, system: Optional[str] = None, history: Optional[list] = None) -> str:
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

    def chat(self, prompt: str, system: Optional[str] = None, history: Optional[list] = None, temperature: float = 0.0, timeout: int = None) -> str:
        # 优先使用 HTTP（除非 force_cli）
        try:
            if not self.force_cli and self._check_http(timeout=self.http_timeout):
                return self.chat_http(prompt, system=system, history=history, temperature=temperature, timeout=timeout)
        except Exception:
            pass
        # 回退到 CLI
        try:
            return self.chat_cli(prompt, system=system, history=history)
        except Exception as e:
            raise RuntimeError("HTTP 和 CLI 调用均失败，请检查 Ollama 是否在本机启动或 ollama CLI 是否安装并在 PATH 中") from e

    # ----------------- Embeddings -----------------
    def embeddings_http(self, inputs: Union[str, List[str]], timeout: int = None) -> List[List[float]]:
        if timeout is None:
            timeout = max(1.0, self.http_timeout)
        if isinstance(inputs, str):
            payload_input = inputs
        else:
            payload_input = inputs
        payload = {
            "model": self.model,
            "input": payload_input,
        }
        candidates = [f"{self.http_url}/api/embeddings", f"{self.http_url}/embeddings", f"{self.http_url}/api/embedding"]
        for url in candidates:
            try:
                r = httpx.post(url, json=payload, timeout=timeout)
            except Exception:
                continue
            if r is None or r.status_code != 200:
                continue
            try:
                body = r.json()
            except Exception:
                continue
            if isinstance(body, dict):
                if 'embeddings' in body and isinstance(body['embeddings'], list):
                    return body['embeddings']
                if 'data' in body and isinstance(body['data'], list):
                    out = []
                    for item in body['data']:
                        if isinstance(item, dict) and 'embedding' in item:
                            out.append(item['embedding'])
                    if out:
                        return out
                if 'embedding' in body and isinstance(body['embedding'], list):
                    return [body['embedding']]
            if isinstance(body, list):
                if len(body) > 0 and isinstance(body[0], list):
                    return body
                if len(body) > 0 and isinstance(body[0], (int, float)):
                    return [body]
        raise RuntimeError("没有可用的 Ollama embedding HTTP 接口或返回格式不支持（尝试 /api/embeddings, /embeddings）")

    def embeddings_cli(self, inputs: Union[str, List[str]]) -> List[List[float]]:
        if not self._has_cli():
            raise RuntimeError("Ollama CLI 未在 PATH 中找到")
        try:
            if isinstance(inputs, str):
                inp = inputs
                cmd = [self.cli_cmd, "embed", self.model, "--text", inp]
                proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
                body = proc.stdout
                try:
                    parsed = json.loads(body)
                    return parsed if isinstance(parsed, list) else [parsed]
                except Exception:
                    raise RuntimeError("无法解析 Ollama CLI embed 输出")
            else:
                cmd = [self.cli_cmd, "embed", self.model, "--json"]
                proc = subprocess.run(cmd, input=json.dumps(inputs), capture_output=True, text=True, check=True)
                body = proc.stdout
                parsed = json.loads(body)
                return parsed
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ollama CLI embed 调用失败: {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"调用 Ollama CLI embed 出错: {e}") from e

    def embeddings(self, inputs: Union[str, List[str]], timeout: int = None) -> List[List[float]]:
        # 优先 HTTP（除非 force_cli）
        try:
            if not self.force_cli and self._check_http(timeout=self.http_timeout):
                return self.embeddings_http(inputs, timeout=timeout)
        except Exception:
            pass
        try:
            return self.embeddings_cli(inputs)
        except Exception as e:
            raise RuntimeError("Ollama HTTP/CLI embedding 均不可用") from e

    def _has_cli(self) -> bool:
        return shutil.which(self.cli_cmd) is not None


__all__ = ["OllamaClient"]

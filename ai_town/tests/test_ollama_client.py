import pytest

from ai_town.core.ollama_client import OllamaClient


def test_ollama_client_init():
    c = OllamaClient(model="test-model")
    assert c.model == "test-model"


@pytest.mark.skip("需要本地 Ollama 服务或 CLI，默认跳过")
def test_ollama_client_chat():
    c = OllamaClient()
    resp = c.chat("Hello")
    assert isinstance(resp, str)

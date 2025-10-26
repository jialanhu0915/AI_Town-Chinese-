# AI 小镇 - 开发说明

本目录保存 AI 小镇项目的 Python 实现。下面包含快速上手、模型配置与常用命令示例（Windows cmd.exe）。

## 环境配置

1. 在 Windows cmd.exe 中创建虚拟环境并激活：

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. 安装依赖：

   ```cmd
   pip install -r ai_town\requirements.txt
   ```

如果有 GPU (CUDA 11.8)，建议安装对应 PyTorch：

```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers sentence-transformers accelerate
```

## 模型准备（离线使用）

- 嵌入模型（推荐小型）：`all-MiniLM-L6-v2`。

  在联网机器上下载并保存（示例）：

  ```cmd
  python ai_town\scripts\save_model.py --model all-MiniLM-L6-v2 --out D:\models\all-MiniLM-L6-v2
  ```

  将保存目录拷贝到离线机，例如：`B:\OllamaModels\LLM_models`。

- 生成模型（RAG 回退，推荐小型）：`distilgpt2`。

  在联网机器上下载并保存（示例）：

  ```cmd
  python ai_town\scripts\save_gen_model.py --model distilgpt2 --out D:\models\distilgpt2
  ```

  将保存目录拷贝到离线机，例如：`B:\OllamaModels\distilgpt2`。

## 配置

默认在 `ai_town/config.py` 中配置了模型路径与默认后端：

- `EMBED_MODEL_PATH`（本地嵌入模型路径）
- `GEN_MODEL_PATH`（本地生成模型路径）
- `DEFAULT_EMBED_METHOD`（默认嵌入后端，默认为 `hf`）
- `DEFAULT_GEN_MODEL`（默认生成模型，默认为本地 `GEN_MODEL_PATH`）

你可以直接编辑 `ai_town/config.py` 或通过环境变量覆盖：

- `AI_TOWN_EMBED_MODEL`
- `AI_TOWN_GEN_MODEL`
- `AI_TOWN_EMBED_METHOD`
- `AI_TOWN_GEN_MODEL_NAME`
- `AI_TOWN_ENABLE_OLLAMA`

## 使用示例

1) 文档导入（ingest）

   ```cmd
   .venv\Scripts\activate
   python -m ai_town.scripts.ingest_docs path\to\doc.txt --embed-method hf --embed-model B:\\OllamaModels\\LLM_models --verbose
   ```

2) 本地检索示例（query_demo）

   ```cmd
   python -m ai_town.scripts.query_demo "你的查询文本" --model B:\\OllamaModels\\LLM_models --embed-method hf --topk 3
   ```

3) 启动后端（FastAPI）

   ```cmd
   python -m uvicorn ai_town.api.main:app --reload --port 8000
   ```

4) 调用检索 API（cmd.exe）：

   ```cmd
   curl -X POST "http://127.0.0.1:8000/api/retrieve" -H "Content-Type: application/json" -d "{\"query\":\"sample query text\"}"
   ```

5) 调用 RAG API（使用本地生成模型路径）：

   ```cmd
   curl -X POST "http://127.0.0.1:8000/api/rag" -H "Content-Type: application/json" -d "{\"query\":\"请基于证据回答：sample question\",\"gen_model\":\"B:\\\\OllamaModels\\\\distilgpt2\"}"
   ```

## 调试与注意事项

- 若使用 HF 模型且首次运行会从 Hugging Face 下载模型，请在联网环境提前下载并拷贝到离线机以避免超时。
- 若使用 Ollama，请确保 Ollama 服务/CLI 可用。默认项目不强制使用 Ollama；可在 `ai_town/config.py` 中修改 `DEFAULT_ENABLE_OLLAMA` 为 `True` 来启用。

## 下一步功能（待办）

- 更完善的 UI（Streamlit）
- Agent 工具集成（网页搜索、代码执行沙箱等）
- CI 与更多测试覆盖

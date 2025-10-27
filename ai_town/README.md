# AI Town - 智能体小镇模拟系统

基于斯坦福大学 AI Town 论文的本地化实现，创建一个多智能体生活模拟系统。

## 🏘️ 项目概述

AI Town 是一个多智能体生活模拟系统，其中多个 AI 角色在虚拟小镇中自主生活、互动和发展关系。

### 核心特性

- **多智能体系统**: 多个 AI 角色同时存在并互动
- **持续生活模拟**: 角色有记忆、计划、社交关系
- **自主行为**: 角色会自主决定行动、对话、移动
- **记忆系统**: 实现记忆流、反思机制
- **社交互动**: 角色间会形成友谊、讨论话题

## 🚀 快速开始

### 使用启动脚本 (推荐)

1. 双击运行 `run_ai_town.bat` 启动脚本
2. 选择选项 1 "运行 AI Town 模拟 (交互式)"
3. 观察智能体的自主行为和互动

### 手动启动

1. 创建虚拟环境并激活：
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. 安装依赖：
   ```cmd
   pip install -r ai_town\requirements.txt
   ```

3. 运行模拟：
   ```cmd
   python ai_town\simulation_runner.py
   ```

## 🏗️ 项目架构

```
ai_town/
├── agents/              # 智能体系统
│   ├── base_agent.py   # 基础智能体类
│   ├── memory/         # 记忆系统
│   ├── planning/       # 行为规划
│   └── characters/     # 角色实现
├── core/               # 核心系统
│   ├── world.py        # 世界状态管理
│   └── time_manager.py # 时间系统
├── environment/        # 环境系统
│   └── map.py         # 地图和物理
└── simulation/         # 模拟引擎
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

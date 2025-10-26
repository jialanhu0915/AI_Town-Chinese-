# AI小镇 项目总览与开发流程

本文件为“AI小镇”项目的整体流程文档，便于后续开发参考与任务分配。内容涵盖项目目标、架构、模块划分、最小可行产品（MVP）、开发步骤、关键技术栈、目录建议、常用命令与下一步计划。

---

## 1. 项目目标（简洁）
- 构建一个本地运行的交互式 AI 小镇平台，支持：对话问答、知识库检索（RAG）、场景化 agent（可调用工具）与简单前端界面。
- 严格使用 Python 实现，优先使用本地 LLM（已安装 Ollama）。

## 2. 整体架构（分层）
- 接入层：Ollama 客户端封装（优先本地 HTTP 或 CLI）。
- 应用层：FastAPI 提供后端接口（聊天、检索、文档管理、工具调用）。
- 检索层：向量化嵌入 + 向量搜索（Faiss 或 SQLite + ANN），文档持久化（sqlite 或文件）。
- 前端/交互：Streamlit（快速开发）或简单的静态 HTML + JS。
- Agent/工具层：网页搜索、文件读取、代码执行沙箱等工具集合。

## 3. 模块划分（代码目录建议）
建议目录（根目录：`ai_town/`）：

- ai_town/
  - core/
    - ollama_client.py        # Ollama 调用封装
    - llm_interface.py       # LLM 抽象层，统一调用方法
  - api/
    - main.py                # FastAPI app
    - endpoints_chat.py
    - endpoints_docs.py
  - retrieval/
    - embedder.py            # 嵌入生成（sentence-transformers 或 Ollama embeddings）
    - indexer.py             # Faiss / ANN 封装
    - storage.py             # 文档元数据与持久化（sqlite）
  - agent/
    - router.py              # 指令解析与工具路由
    - tools/
      - web_search.py
      - file_reader.py
  - ui/
    - streamlit_app.py       # Streamlit 前端（可选）
  - scripts/
    - ingest_docs.py         # 文档导入与分段脚本
    - start_server.bat       # 启动脚本（Windows）
  - config.py
  - requirements.txt
  - README.md

## 4. MVP（最小可行产品）功能清单
1. 用 Python 能调用本地 Ollama 做一次对话。
2. 能把文档（txt/pdf）导入、分段、生成嵌入并构建向量索引，支持 top-k 检索。
3. 实现 RAG：将检索到的段落拼接到 prompt，返回带证据的回答。
4. 简单前端（Streamlit）：支持对话、上传文档、查看检索结果与对话历史。
5. 提供基本测试（pytest）与 README，能在本地运行。

## 5. 关键技术与推荐库
- Web/API：FastAPI + uvicorn
- 前端（轻量）：Streamlit
- 向量检索：sentence-transformers（embeddings）+ faiss-cpu（或 SQLite + ANN 备选）
- 数据库存储：sqlite + SQLAlchemy（或 TinyDB）
- 并发/HTTP：httpx / asyncio
- 测试：pytest
- 配置：python-dotenv
- 日志：loguru 或 logging

示例 requirements.txt（MVP）：
```
fastapi
uvicorn[standard]
streamlit
sentence-transformers
faiss-cpu
sqlalchemy
python-dotenv
httpx
pytest
pydantic
```

## 6. 核心流程说明（RAG）
1. 接收用户 query（API/前端）。
2. 用 embedder 将 query 向量化。
3. 在向量索引中检索 top-k 段落（按相似度）。
4. 用模板把检索到的段落与 user query 拼接成系统提示或上下文（注意长度控制）。
5. 调用 Ollama（LLM）生成答案，并返回同时包含检索证据（段落 id、原文片段）。

提示模板示例（简略）:
- System: 你是一个基于文档的问答助理，请仅基于下面提供的证据回答。
- Context: [检索到的段落列表]
- User: [用户问题]

## 7. 文档处理策略
- 支持格式：txt、md、pdf（pdf 采用 pdfminer / pypdf 提取文本）。
- 分段策略：按段落或固定 token 窗口（例如 512 tokens，滑动窗口可重叠 50%）。
- 存储：每个片段保存原始来源、页码/位置、hash、embedding、text。

## 8. 开发步骤与时间建议（估计）
阶段 A — 环境与基础（1-3 天）
- 创建 venv、安装基础依赖。
- 实现 `ollama_client.py` 并验证本地调用。

阶段 B — 检索系统（3-5 天）
- 编写文档导入与分段脚本。
- 实现 embedder 与 Faiss 索引建立/查询。

阶段 C — RAG 聊天后端（4-7 天）
- 使用 FastAPI 实现聊天 endpoint，整合检索与 LLM。
- 实现对话管理（session、历史）。

阶段 D — 前端（2-4 天）
- 用 Streamlit 做基础 UI（对话、上传、检索展示）。

阶段 E — Agent 与工具（可选，持续）
- 添加网页搜索、代码执行等工具并集成到 Agent 路由中。

## 9. Windows (cmd.exe) 常用命令示例
- 创建并激活 venv：
  - python -m venv .venv
  - .venv\Scripts\activate
- 安装依赖：
  - pip install -r requirements.txt
- 运行 FastAPI：
  - python -m uvicorn ai_town.api.main:app --reload --port 8000
- 运行 Streamlit：
  - streamlit run ai_town\ui\streamlit_app.py

## 10. 示例代码要点（简短）
- Ollama 封装（思路）:
  - 优先尝试本地 HTTP endpoint；若不可用，使用 subprocess 调用 `ollama` CLI。
  - 提供统一方法：chat(prompt, system=None, history=None, temperature=0.0) -> response_text

- 向量检索（思路）:
  - 使用 sentence-transformers 生成 embedding（或 Ollama 的 embedding 接口）。
  - 用 Faiss 建索引并保存到磁盘（索引 + 元数据分离）。

## 11. 测试与部署建议
- 编写 pytest 测试：包括检索准确性、Ollama 调用、API 响应。
- 本地 CI：GitHub Actions（运行 pytest、lint）。
- 若需要对外演示可用 ngrok 暂时内网穿透（注意安全）。

## 12. 风险与注意事项
- 本地模型资源消耗（内存、GPU）与延迟问题。
- 数据隐私：注意不要将敏感数据发往外部服务。
- 模型与第三方库的许可问题（遵守授权）。

## 13. 下一步建议（可选操作）
请选择一项让我开始：
- A. 实现并提交 `core/ollama_client.py`（我将写出代码与使用示例）。
- B. 创建项目骨架与 `requirements.txt`（我将生成初始文件结构）。
- C. 实现一个最小 FastAPI + RAG 示例（包含检索与 Ollama 调用）。

---

最后更新：2025-10-26

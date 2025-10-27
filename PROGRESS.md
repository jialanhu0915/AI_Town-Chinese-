# AI_Town — 当前进度与待办（2025-10-26）

## 一、项目概况（目标回顾）

- 本地可运行的 AI 小镇（AI Town），仅用 Python，支持：
  - 本地 LLM（Ollama / HuggingFace Transformers）
  - 文档 ingest（txt/pdf）
  - 向量检索（Faiss RAG 流程）
  - 本地生成（transformers），优先使用本地模型并可在离线环境运行
  - Windows 兼容（GPU/CPU 支持）
  - 可通过配置文件指定本地模型路径，避免每次手动输入

## 二、已完成（功能/代码与重要文件）

- 项目结构与基础文件
  - `ai_town/config.py`（已可配置本地模型路径、数据目录等）
  - `ai_town/requirements.txt`, `ai_town/README.md`, `ai_town/info.md`
- Embedding / Ollama 支持
  - `ai_town/retrieval/embedder.py`：支持 HF / Ollama / auto；默认 HF，优先 GPU
  - `ai_town/core/ollama_client.py`：Ollama HTTP/CLI 支持（默认不启用）
- 文档 ingest 与向量化
  - `ai_town/scripts/ingest_docs.py`：支持 txt/pdf、文本分割、embedding、保存 vectors、调用 Faiss 建索引
  - 支持显式指定本地 embedding 模型（`--embed-model`）
- Faiss 索引与文件编码问题修复
  - `ai_town/retrieval/faiss_utils.py`：
    - 写索引时改为生成 ASCII-safe 名（percent-encode + short md5），并先写入临时 ASCII 文件再复制/替换到目标，避免 Faiss 在含中文路径写入失败
    - 修复临时文件前缀会含中文导致的 mojibake（改用 md5 前缀）
- Manifest / 存储管理
  - `ai_town/retrieval/storage.py`：manifest 读取/写入接口
  - manifest 扩展字段：`index_original`（可读名）与 `index_safe`（实际文件名）
  - `ai_town/scripts/ingest_docs.py` 已更新以写入 `index_safe` 与 `index_original`
- 查询 demo
  - `ai_town/scripts/query_demo.py`：兼容 `index_safe` / `index` / `index_original`，加载 Faiss 索引并返回 top-k 片段
  - 本地查询演示：检索结果已在本地测试成功（示例输出已验证）
- 生成模型保存工具
  - `ai_town/scripts/save_gen_model.py`：支持自动检测 causal/seq2seq，支持 `--low-cpu-mem-usage`、`--load-in-8bit`（bitsandbytes）、`--safe-save`（single-file state_dict）、`--device` 等参数
- 清理 / 规范化脚本
  - `ai_town/scripts/normalize_index_names.py`：试图匹配并规范 manifest 与磁盘索引名（已添加但以谨慎操作为主）
  - `ai_town/scripts/clean_data_dir.py`：将未被 manifest 引用的文件移动到备份目录，支持 `--delete` 永久删除
- 小工具 & 改进
  - 打印保存文件大小、safe-save 功能、8-bit 加载检测与友好错误提示
  - 增强日志与异常提示

## 三、关键修复与当前状态说明（已验证）

- Faiss 写入中文/含非 ASCII 路径异常被解决：
  - 现在索引实际以 ASCII-safe 名保存（percent-encode + md5），保证 Faiss 写入成功。
  - manifest 中保留了 `index_original`（可读原名）以便追踪和 UI 展示。
- mojibake / 旧临时文件：
  - 在早期测试中生成的一些“乱码名”文件（mojibake）存在磁盘上。为了安全，先不直接删除，提供了 `clean_data_dir.py` 进行备份与清理（已运行并删除了旧备份）。
- 检索流程已本地验证：
  - `python -m ai_town.scripts.query_demo "你的问题" --embed-method hf --model "本地模型路径" --topk 3`
  - 已成功返回 top-k 片段（说明 vectors, index, meta 三者一致）。
- 8-bit / bitsandbytes：
  - `save_gen_model.py` 与加载逻辑支持 `--load-in-8bit`（需在联网机器安装 bitsandbytes/accelerate），并在 ingest/save 时有相应保护（safe-save 不支持 8-bit）。

## 四、如何复现 / 常用命令（Windows cmd，项目根目录）

- 激活 venv
  .venv\Scripts\activate
- 安装依赖
  pip install -r ai_town\requirements.txt
- 文档 ingest（示例，显式使用本地 embedding 模型）
  python -m ai_town.scripts.ingest_docs "B:\path\to\doc.pdf" --chunk-size 200 --overlap 50 --embed-method hf --embed-model "D:\models\all-MiniLM-L6-v2" --verbose
- 查询 demo（示例）
  python -m ai_town.scripts.query_demo "什么是神经网络？" --embed-method hf --model "B:\OllamaModels\LLM_models" --topk 3
- 启动 FastAPI（若需要）
  python -m uvicorn ai_town.api.main:app --host 0.0.0.0 --port 8000
- 清理未引用文件（先备份）
  python -m ai_town.scripts.clean_data_dir
- 永久删除备份（谨慎）
  python -m ai_town.scripts.clean_data_dir --delete
- 规范化索引名（仅作检查/修复参考）
  python -m ai_town.scripts.normalize_index_names

## 五、当前未完成 / 待办（按优先级排序）

高优先级（建议尽快处理）
1. 统一索引路径访问 API（推荐实现）
   - 在 `ai_town/retrieval/storage.py` 增加 `get_index_path(dataset_name)`，统一优先使用 `index_safe` 并回退到 `index`/`index_original`，将所有调用处改为使用该函数（提升代码健壮性）。
2. 索引生命周期管理
   - 在 ingest 时处理“旧 safe 文件”的清理或备份策略（避免磁盘累积）。
3. 单元测试 / CI
   - 为 ingest、faiss_utils、query_demo、save_gen_model 添加单元/集成测试并在 CI 中执行（包含 Windows runner）。
4. RAG 端到端验证
   - 用本地生成模型（如本地 `flan-t5-small` 或你已下载的 causal 模型）对 RAG endpoint `/api/rag` 做端到端测试，验证生成质量、prompt 后处理、多证据去重。

中优先级
5. API （FastAPI）完善与负载
   - 增加 `/api/config` 或调试端点；为 8-bit / device_map 的模型加载添加运行时开关与错误处理。
6. 模型兼容性增强
   - 增加对 quantized checkpoints、bitsandbytes 8-bit 的更完整支持（尤其在 API 中）并记录依赖说明（安装方式、Windows 特殊注意）。
7. 增强 manifest 管理
   - manifest 版本字段、索引创建时间、原始文件校验（如向量数与 meta 长度一致）等检查工具。

低优先级 / 可选
8. 前端（Streamlit / 简易 UI）以便浏览索引、查询与 RAG 调用。
9. Agent / 工具集成（多轮对话、检索增强流程）。
10. 增量 ingest、索引合并、索引压缩/分片管理。

## 六、建议的下一步（短期行动）

- 实现 storage.get_index_path 并替换所有直接读取 manifest 的调用（增加一个小 PR）。可立刻由我实现（快速且影响面小）。
- 针对 RAG：在本地用 flan-t5-small 或 distilgpt2 做一次端到端测试（ingest → query → /api/rag），确认生成提示与后处理。
- 在 CI 或本地增加简单 pytest 测试覆盖 ingest 与 query 流程（确保不会回归）。

## 七、重要文件清单（快速参考）

- core / 模型
  - `ai_town/core/ollama_client.py`
  - `ai_town/scripts/save_gen_model.py`
- 检索 / 向量
  - `ai_town/retrieval/embedder.py`
  - `ai_town/retrieval/splitter.py`
  - `ai_town/retrieval/faiss_utils.py`
  - `ai_town/retrieval/storage.py`
- 脚本
  - `ai_town/scripts/ingest_docs.py`
  - `ai_town/scripts/query_demo.py`
  - `ai_town/scripts/normalize_index_names.py`
  - `ai_town/scripts/clean_data_dir.py`
- API
  - `ai_town/api/main.py`
  - `ai_town/api/endpoints_retrieval.py`
  - `ai_town/api/endpoints_rag.py`
- 数据
  - `ai_town/data/index_manifest.json`（manifest）
  - `ai_town/data/*.index`, `*.npy`（向量/索引）

## 八、注意事项（Windows / 离线）

- Faiss 写入中文路径在某些构建下会失败 —— 已采用 ASCII-safe 索引名作为稳定方案。不要依赖 Faiss 能直接写入中文名（除非确认底层环境支持）。
- bitsandbytes/8-bit 在 Windows 下对 CUDA/CPU 支持有版本与兼容性要求，安装时需参考 bitsandbytes 官方说明与 CUDA 版本匹配。
- offline 运行需确保 embedding 与生成模型已提前下载并在 `config.py` 中配置本地路径。


---

若需要我把这份文档放到其它位置或用不同格式（如 `docs/PROGRESS.md`、简体/繁体或提炼为短版 TODO），告诉我我会替你调整。

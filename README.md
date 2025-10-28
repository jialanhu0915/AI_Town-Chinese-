# 🏘️ AI Town - 多智能体生活模拟系统

![CI Status](https://github.com/jialanhu0915/AI_Town-Chinese-/workflows/AI%20Town%20CI%2FCD%20Pipeline/badge.svg)
![Branch Protection](https://github.com/jialanhu0915/AI_Town-Chinese-/workflows/Branch%20Protection%20Validation/badge.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)
![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

一个基于大语言模型（LLM）驱动的多智能体生活模拟系统，灵感来源于斯坦福 AI Town 项目。智能体们拥有记忆、规划和反思能力，能在虚拟小镇中进行自然的社交互动和生活模拟。

## 🎯 **项目特色**

### 🤖 **真正的 AI 驱动**

- **DeepSeek-R1** 等先进 LLM 提供智能推理
- **智能决策** - 基于时间、环境、记忆的行为规划
- **自然对话** - 丰富的角色扮演和情感表达
- **个性化** - 每个智能体都有独特的性格和背景

### 🏗️ **完整的架构**

- **记忆流** (Memory Stream) - 模拟人类记忆机制
- **行为规划** (Action Planning) - 智能体的目标导向行为
- **反思机制** (Reflection) - 从经历中学习和成长
- **社交网络** - 智能体间的关系和互动

### 🔧 **灵活配置**

- **配置文件驱动** - 通过 `.env` 文件轻松调整设置
- **多 LLM 支持** - Ollama、OpenAI、Mock LLM 等
- **故障转移** - 自动在不同 LLM 提供商间切换
- **本地优先** - 完全离线运行，保护隐私

### 🎨 **可视化界面**

- **Web 前端** - 实时观察智能体活动
- **地图显示** - 智能体位置和移动轨迹
- **聊天记录** - 智能体间的对话历史
- **状态监控** - 智能体的当前状态和行为

## 🚀 **快速开始**

### 📋 **环境要求**

- Python 3.9+
- 2GB+ 内存（推荐 4GB+）
- （可选）Ollama + LLM 模型

### 🛠️ **安装步骤**

1. **克隆项目**

   ```bash
   git clone <repository-url>
   cd AI_Town
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置 LLM（可选）**

   ```bash
   # 安装 Ollama (https://ollama.ai)
   ollama pull deepseek-r1:1.5b
   ollama serve
   ```

### ⚡ **运行方式**

#### **方式 1: 交互式启动**

```bash
run_ai_town.bat
# 选择 1: 交互式模拟
```

#### **方式 2: 直接运行**

```bash
python ai_town/simulation_runner.py
```

#### **方式 3: Web 可视化**

```bash
python ai_town/ui/visualization_server.py
# 打开 http://localhost:8000
```

#### **方式 4: 配置管理**

```bash
python config_manager.py
# 快速切换 LLM 模型和设置
```

## 🗺️ **小镇地图**

```text
🏡 Houses        🍵 Coffee Shop    📚 Bookstore
🏢 Offices       🍽️ Restaurant     🌳 Park
```

智能体们会根据时间和需求在不同区域间移动：

- **工作时间** → 各自工作场所
- **休息时间** → 咖啡店、公园社交
- **夜晚** → 回家休息

## 🔧 **配置选项**

### **LLM 提供商**

```env
# 主要配置 (.env 文件)
AI_TOWN_LLM_PROVIDER=ollama
OLLAMA_MODEL=deepseek-r1:1.5b

# 可选模型
# OLLAMA_MODEL=tinyllama           # 轻量级
# OLLAMA_MODEL=deepseek-r1:8b      # 高性能
# OLLAMA_MODEL=qwen:7b-chat        # 中文友好
```

#### 第三方厂商（新）

- DeepSeek（OpenAI 兼容风格）

```env
# 必填：API Key（读取 DEEPSEEK_API_KEY）
DEEPSEEK_API_KEY=your_deepseek_key
# 可选：默认 base_url/model 已内置
# （如需自定义，请在配置中设置 deepseek.base_url / deepseek.model_name）
```

- Kimi / Moonshot（OpenAI 兼容风格）

```env
# 必填：API Key（读取 MOONSHOT_API_KEY 或 KIMI_API_KEY）
MOONSHOT_API_KEY=your_moonshot_key
# 或 KIMI_API_KEY=your_kimi_key
# 可选：默认 base_url/model 已内置
# （如需自定义，请在配置中设置 kimi.base_url / kimi.model_name）
```

- Qwen / DashScope 兼容模式（/v1/chat/completions）

```env
# 必填：API Key（读取 DASHSCOPE_API_KEY 或 DASH_SCOPE_API_KEY）
DASHSCOPE_API_KEY=your_dashscope_key
# 可选：默认 base_url/model 已内置
# （如需自定义，请在配置中设置 qwen.base_url / qwen.model_name）
```

- 选择默认与回退链（在配置中设置）

```env
# 示例（概念）：
# LLM_CONFIG.default_provider=deepseek
# LLM_CONFIG.fallback_chain=["ollama","openai","deepseek","kimi","qwen","mock"]
```

> 提示：未配置的 base_url / model_name 将使用代码中的默认值（DeepSeek: deepseek-chat；Kimi: moonshot-v1-8k；Qwen: qwen-plus）。

### **智能体设置**

```env
# 各角色 LLM 配置
ALICE_LLM_PROVIDER=ollama
BOB_LLM_PROVIDER=ollama  
CHARLIE_LLM_PROVIDER=ollama

# LLM 功能开关
ALICE_LLM_PLANNING=true
ALICE_LLM_CONVERSATION=true
ALICE_LLM_REFLECTION=true
```

### **模拟参数**

```env
AI_TOWN_TIME_MULTIPLIER=10.0     # 时间加速
AI_TOWN_STEP_INTERVAL=1.0        # 步骤间隔
AI_TOWN_MAX_AGENTS=20            # 最大智能体数
```

### **记忆持久化（新）**

```env
# 是否将记忆写入磁盘（默认开启）
AI_TOWN_MEMORY_PERSIST=1   # 1/true/yes/on 开启；0/false/no/off 关闭

# 是否在启动时加载历史记忆（默认开启，且仅在 PERSIST 开启时生效）
AI_TOWN_MEMORY_LOAD=1
```

- 关闭示例（仅本次进程）：
  - Windows CMD
    - `set AI_TOWN_MEMORY_PERSIST=0 && python ai_town\ui\visualization_server.py`
  - 仅禁用“加载”但继续写入：
    - `set AI_TOWN_MEMORY_PERSIST=1 && set AI_TOWN_MEMORY_LOAD=0 && python ai_town\ui\visualization_server.py`

## 🐛 **故障排除**

### **常见问题**

#### Q: Ollama 连接失败

```bash
# 确保 Ollama 服务运行
ollama serve

# 检查模型是否下载
ollama list

# 测试模型
ollama run deepseek-r1:1.5b "Hello"
```

#### Q: 智能体决策失败

- 检查 LLM 响应格式
- 启用 Mock LLM 作为后备
- 查看日志获取详细错误信息

#### Q: 配置不生效

- 确保 `.env` 文件在项目根目录
- 重启应用以应用新配置
- 使用 `config_manager.py` 验证设置

#### Q: 每次运行都会带入历史记忆，如何“干净启动”？

- 临时禁用加载：设置 `AI_TOWN_MEMORY_LOAD=0`。
- 完全禁用持久化：设置 `AI_TOWN_MEMORY_PERSIST=0`（也不会加载）。
- 清理磁盘历史：删除 `ai_town/data/memories/<agent_id>/*.json`（例如 alice/bob/charlie）。

## 🔮 **未来规划**

### **短期目标**

- [ ] 优化 JSON 解析稳定性
- [ ] 添加更多智能体角色
- [ ] 增强可视化界面
- [ ] 完善记忆和反思机制

### **中期目标**

- [ ] 支持多模态交互（图像、语音）
- [ ] 实现智能体间的协作任务
- [ ] 添加经济系统和资源管理
- [ ] 支持用户自定义事件

### **长期愿景**

- [ ] 大规模智能体社区模拟
- [ ] 真实世界数据集成
- [ ] 跨平台部署支持
- [ ] 开放 API 和插件系统

## 📄 **许可证**

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 **贡献指南**

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙏 **致谢**

- [斯坦福 AI Town](https://github.com/a16z-infra/ai-town) - 原始灵感来源
- [DeepSeek](https://www.deepseek.com/) - 优秀的开源 LLM
- [Ollama](https://ollama.ai/) - 简化本地 LLM 部署
- 所有贡献者和测试者

## 📞 **联系方式**

- **项目地址**: [GitHub Repository](.)
- **问题反馈**: [Issues](./issues)
- **讨论交流**: [Discussions](./discussions)

---

**🌟 如果这个项目对你有帮助，请给一个 Star！**

*让 AI 智能体在虚拟世界中自由生活和成长* 🤖✨

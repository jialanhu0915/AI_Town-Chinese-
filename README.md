# 🏘️ AI Town - 多智能体生活模拟系统

<p align="center">
  <img src="https://github.com/your-username/AI_Town/workflows/AI%20Town%20CI%2FCD%20Pipeline/badge.svg" alt="CI Status">
  <img src="https://github.com/your-username/AI_Town/workflows/Branch%20Protection%20Validation/badge.svg" alt="Branch Protection">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/security-bandit-yellow.svg" alt="Security: bandit">
  <img src="https://img.shields.io/badge/%20imports-isort-%231674b1" alt="Imports: isort">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT">
</p>

一个基于大语言模型（LLM）驱动的多智能体生活模拟系统，灵感来源于斯坦福 AI Town 项目。智能体们拥有记忆、规划和反思能力，能在虚拟小镇中进行自然的社交互动和生活模拟。

> **⚠️ 注意**: 请将上面的 `your-username` 替换为实际的GitHub用户名或组织名

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

## 👥 **智能体角色**

### 🍵 **Alice - 咖啡店老板**
- **年龄**: 32岁
- **性格**: 友好外向，热爱社交
- **职业**: 经营镇上最受欢迎的咖啡店
- **特点**: 喜欢与顾客聊天，了解每个人的故事

### 📚 **Bob - 书店老板**
- **年龄**: 47岁  
- **性格**: 内向博学，热爱知识
- **职业**: 经营古朴的书店
- **特点**: 喜欢深度对话，推荐好书

### 💼 **Charlie - 上班族**
- **年龄**: 28岁
- **性格**: 勤奋有抱负，适应力强
- **职业**: 办公室职员，新来镇上
- **特点**: 努力融入社区，寻找工作生活平衡

## 🗺️ **小镇地图**

```
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

## 📊 **系统架构**

```
AI_Town/
├── 📁 ai_town/
│   ├── 🤖 agents/           # 智能体实现
│   │   ├── base_agent.py    # 基础智能体类
│   │   ├── llm_enhanced_agent.py # LLM 增强智能体
│   │   └── characters/      # 具体角色
│   ├── ⚡ core/             # 核心系统
│   │   ├── world.py         # 世界管理
│   │   └── time_manager.py  # 时间系统
│   ├── 🌍 environment/      # 环境模拟
│   │   └── map.py           # 地图系统
│   ├── 🧠 llm/              # LLM 集成
│   │   └── llm_integration.py
│   ├── 🎨 ui/               # 用户界面
│   │   └── visualization_server.py
│   └── 📊 data/             # 数据存储
├── 🔧 config_manager.py     # 配置管理器
├── ⚙️ .env                 # 环境配置
└── 🚀 run_ai_town.bat      # 启动脚本
```

## 🎛️ **LLM 集成**

### **支持的提供商**

| 提供商 | 类型 | 优点 | 缺点 | 推荐场景 |
|--------|------|------|------|----------|
| **Ollama** | 本地 | 免费、隐私、离线 | 需要安装 | 日常使用 |
| **OpenAI** | 云端 | 效果最佳 | 付费、需网络 | 高质量需求 |
| **Mock** | 模拟 | 零配置 | 功能有限 | 测试演示 |

### **推荐模型**

| 模型 | 大小 | 内存需求 | 特点 | 适用场景 |
|------|------|----------|------|----------|
| `deepseek-r1:1.5b` | 1.1GB | 2GB | 平衡效果和速度 | **推荐** |
| `tinyllama` | 637MB | 1GB | 超轻量 | 低配置设备 |
| `deepseek-r1:8b` | 4.9GB | 6GB | 高性能 | 高端设备 |
| `qwen:7b-chat` | 4GB | 5GB | 中文优化 | 中文场景 |

## 📈 **功能展示**

### **智能决策示例**
```json
{
  "type": "work",
  "description": "整理书架", 
  "reason": "现在是工作时间，需要维护好书店"
}
```

### **自然对话示例**
```
Alice: "我是Alice，32岁，从5年前搬到这个小镇，开了一个温暖的咖啡店。欢迎来到我的故事里吧！"

Bob: "欢迎来到我的故事里"

Charlie: "Charlie 工作繁忙，刚搬进镇上，适应新环境确实有难度。但新朋友的到来让他觉得有趣许多..."
```

## 🔄 **工作流程**

1. **初始化** - 加载配置，创建智能体和世界
2. **时间循环** - 游戏时间推进（可加速）
3. **智能体思考** - 基于当前状态和记忆进行决策
4. **执行行为** - 移动、工作、社交等
5. **更新状态** - 记录新的记忆和经历
6. **反思学习** - 定期从经历中提取洞察
7. **持续循环** - 形成持续的生活模拟

## 🧪 **测试和验证**

### **运行测试**
```bash
# 基础功能测试
python test_basic.py

# LLM 智能体测试  
python test_llm_agents.py

# 完整系统测试
python test_complete.py

# 快速验证
python quick_test.py
```

### **配置验证**
```bash
# 查看当前配置
python config_manager.py
# 选择 1: 查看当前配置

# 测试 LLM 连接
python test_deepseek.py
```

## 📚 **开发指南**

### **添加新角色**
1. 在 `ai_town/agents/characters/` 创建新文件
2. 继承 `LLMEnhancedAgent` 类
3. 定义性格、背景和特殊行为
4. 在配置文件中添加 LLM 设置

### **扩展环境**
1. 修改 `ai_town/environment/map.py`
2. 添加新的区域和建筑物
3. 定义区域间的连接关系
4. 更新智能体的导航逻辑

### **集成新 LLM**
1. 在 `ai_town/llm/llm_integration.py` 添加新提供商
2. 实现 `LLMProvider` 接口
3. 在配置文件中添加相关设置
4. 注册到 LLM 管理器

## 🐛 **故障排除**

### **常见问题**

**Q: Ollama 连接失败**
```bash
# 确保 Ollama 服务运行
ollama serve

# 检查模型是否下载
ollama list

# 测试模型
ollama run deepseek-r1:1.5b "Hello"
```

**Q: 智能体决策失败**
- 检查 LLM 响应格式
- 启用 Mock LLM 作为后备
- 查看日志获取详细错误信息

**Q: 配置不生效**
- 确保 `.env` 文件在项目根目录
- 重启应用以应用新配置
- 使用 `config_manager.py` 验证设置

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

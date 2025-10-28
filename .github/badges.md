# GitHub 状态徽章配置

本文档说明如何为 AI Town 项目添加状态徽章，展示项目的健康状态和质量指标。

## 🏷️ 建议的徽章

将以下徽章添加到 README.md 的顶部：

```markdown
![CI Status](https://github.com/[owner]/AI_Town/workflows/AI%20Town%20CI%2FCD%20Pipeline/badge.svg)
![Security Scan](https://github.com/[owner]/AI_Town/workflows/Security%20Scan/badge.svg)
![Branch Protection](https://github.com/[owner]/AI_Town/workflows/Branch%20Protection%20Validation/badge.svg)
[![codecov](https://codecov.io/gh/[owner]/AI_Town/branch/main/graph/badge.svg)](https://codecov.io/gh/[owner]/AI_Town)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
```

## 📊 徽章类型说明

### CI/CD 状态徽章
- **CI Status**: 显示主要CI流水线状态
- **Security Scan**: 显示安全扫描状态  
- **Branch Protection**: 显示分支保护验证状态

### 代码质量徽章
- **Test Coverage**: 显示测试覆盖率
- **Code Style**: 显示代码格式化状态
- **Import Sorting**: 显示导入排序状态
- **Security**: 显示安全检查状态

### 项目信息徽章
- **Python Version**: 支持的Python版本
- **License**: 项目许可证
- **PRs Welcome**: 欢迎贡献

## 🔧 自定义徽章

### 动态状态徽章
可以通过 shields.io 创建自定义徽章：

```markdown
<!-- 项目版本 -->
![Version](https://img.shields.io/github/v/tag/[owner]/AI_Town?label=version)

<!-- 最后提交 -->
![Last Commit](https://img.shields.io/github/last-commit/[owner]/AI_Town)

<!-- 问题数量 -->
![Issues](https://img.shields.io/github/issues/[owner]/AI_Town)

<!-- PR数量 -->
![Pull Requests](https://img.shields.io/github/issues-pr/[owner]/AI_Town)

<!-- 贡献者数量 -->
![Contributors](https://img.shields.io/github/contributors/[owner]/AI_Town)

<!-- 仓库大小 -->
![Repo Size](https://img.shields.io/github/repo-size/[owner]/AI_Town)

<!-- 下载次数 -->
![Downloads](https://img.shields.io/github/downloads/[owner]/AI_Town/total)
```

### 技术栈徽章
展示使用的技术：

```markdown
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socketdotio&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
```

## 📋 README 徽章模板

```markdown
<!-- 项目标题和描述 -->
# 🏘️ AI Town - 多智能体生活模拟系统

<!-- 主要徽章行 -->
<p align="center">
  <img src="https://github.com/[owner]/AI_Town/workflows/AI%20Town%20CI%2FCD%20Pipeline/badge.svg" alt="CI Status">
  <img src="https://github.com/[owner]/AI_Town/workflows/Security%20Scan/badge.svg" alt="Security">
  <img src="https://codecov.io/gh/[owner]/AI_Town/branch/main/graph/badge.svg" alt="Coverage">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python">
</p>

<!-- 代码质量徽章行 -->
<p align="center">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
  <img src="https://img.shields.io/badge/%20imports-isort-%231674b1" alt="isort">
  <img src="https://img.shields.io/badge/security-bandit-yellow.svg" alt="Bandit">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

<!-- 项目信息徽章行 -->
<p align="center">
  <img src="https://img.shields.io/github/v/tag/[owner]/AI_Town?label=version" alt="Version">
  <img src="https://img.shields.io/github/last-commit/[owner]/AI_Town" alt="Last Commit">
  <img src="https://img.shields.io/github/contributors/[owner]/AI_Town" alt="Contributors">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>
```

## 🎨 徽章样式

### 样式选项
- `flat` - 扁平样式（默认）
- `flat-square` - 方形扁平
- `for-the-badge` - 大型徽章
- `plastic` - 塑料风格
- `social` - 社交媒体风格

### 颜色选项
- `brightgreen`, `green`, `yellowgreen`, `yellow`, `orange`, `red`
- `lightgrey`, `blue`, `lightblue`, `purple`, `pink`
- 自定义颜色：`#RGB` 或 `#RRGGBB`

## 📈 监控和维护

### 自动更新
大多数徽章会自动更新，但某些需要手动配置：

1. **Codecov**: 需要在 Codecov.io 注册项目
2. **Security**: 配合 GitHub 安全功能
3. **Custom**: 需要定期检查和更新

### 徽章失效处理
- 定期检查徽章链接有效性
- 更新过时的服务链接
- 移除不再维护的服务徽章

## 🔗 有用链接

- [Shields.io](https://shields.io/) - 徽章生成服务
- [GitHub Badges](https://github.com/badges/shields) - 开源徽章项目
- [Codecov](https://codecov.io/) - 代码覆盖率服务
- [GitHub Actions Badges](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge)

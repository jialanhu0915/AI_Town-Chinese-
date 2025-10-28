# AI Town 分支保护规则 - 完整配置指南

## 🎯 概述

本文档提供了为 AI Town 公共仓库配置 GitHub 分支保护规则的完整指南。所有必需的文件和工作流已创建完成，可立即部署使用。

## 📁 已创建的文件

### 1. 核心配置文件
```
.github/
├── workflows/
│   ├── ci.yml                    # 主要CI/CD流水线
│   ├── branch-protection.yml     # 分支保护验证
│   └── setup-branch-protection.yml # 自动化分支保护设置
├── ISSUE_TEMPLATE/
│   ├── bug_report.md             # Bug报告模板
│   └── feature_request.md        # 功能请求模板
├── pull_request_template.md      # PR模板
├── CODEOWNERS                    # 代码审查者配置
├── branch-protection.md          # 分支保护说明文档
└── badges.md                     # 状态徽章配置指南
```

### 2. 状态检查工作流
所有工作流都已配置完成，包括：
- ✅ 代码质量检查 (black, isort, flake8)
- ✅ 安全扫描 (bandit, safety)
- ✅ 多平台兼容性测试
- ✅ 文档完整性验证
- ✅ 项目结构验证

## 🚀 快速部署步骤

### 步骤 1: 推送文件到仓库
```bash
# 提交所有新创建的文件
git add .github/
git commit -m "Add comprehensive branch protection configuration"
git push origin main
```

### 步骤 2: 手动设置分支保护（推荐）
访问 GitHub 仓库设置页面：
```
https://github.com/[用户名]/AI_Town/settings/branches
```

点击 "Add rule" 为主分支配置保护：

#### 主分支 (main) 配置：
- **Branch name pattern**: `main`
- ✅ **Require pull request reviews before merging**
  - Required approving reviews: `2`
  - ✅ Dismiss stale reviews when new commits are pushed
  - ✅ Require review from code owners
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - 添加状态检查：
    - `test`
    - `security` 
    - `build-and-validate`
    - `documentation`
    - `compatibility / ubuntu-latest (3.9)`
    - `compatibility / ubuntu-latest (3.11)`
    - `compatibility / windows-latest (3.9)`
    - `compatibility / windows-latest (3.11)`
    - `compatibility / macos-latest (3.9)`
    - `compatibility / macos-latest (3.11)`
- ✅ **Require conversation resolution before merging**
- ✅ **Restrict pushes that create files that exceed 100MB**
- ✅ **Do not allow bypassing the above settings**

#### 开发分支 (develop) 配置：
- **Branch name pattern**: `develop`
- ✅ **Require pull request reviews before merging**
  - Required approving reviews: `1`
- ✅ **Require status checks to pass before merging**
  - 添加状态检查：
    - `test`
    - `security`
    - `build-and-validate`

### 步骤 3: 自动化设置（可选）
使用自动化工作流设置分支保护：

1. 前往 Actions 页面
2. 找到 "Setup Branch Protection" 工作流
3. 点击 "Run workflow"
4. 选择分支和保护级别
5. 执行工作流

### 步骤 4: 验证配置
创建一个测试PR来验证保护规则：
```bash
git checkout -b test/branch-protection
echo "# Test" > test_file.md
git add test_file.md
git commit -m "Test branch protection"
git push origin test/branch-protection
```

在GitHub上创建PR，验证：
- ✅ 必需的状态检查显示
- ✅ 需要审查者批准
- ✅ 所有CI检查通过

## 🛡️ 状态检查详情

### 必需检查项目
每个PR必须通过以下检查才能合并：

1. **test** - 代码测试和质量
   - 代码格式检查 (black)
   - 导入排序 (isort)  
   - 代码质量 (flake8)
   - 单元测试 (pytest)
   - 测试覆盖率报告

2. **security** - 安全检查
   - 安全漏洞扫描 (bandit)
   - 依赖项安全检查 (safety)

3. **build-and-validate** - 构建验证
   - 项目结构完整性
   - 模块导入测试
   - 可视化服务器验证

4. **documentation** - 文档检查
   - README存在性验证
   - 文档完整性检查

5. **compatibility** - 兼容性测试
   - 多平台测试 (Ubuntu, Windows, macOS)
   - 多Python版本测试 (3.9, 3.11)

## 👥 团队权限配置

### CODEOWNERS 团队
需要在GitHub仓库设置中创建以下团队：

- `@core-team` - 核心开发团队
- `@event-system-team` - 事件系统专家
- `@frontend-team` - 前端开发团队  
- `@devops-team` - DevOps和基础设施团队
- `@qa-team` - 质量保证团队
- `@docs-team` - 文档维护团队
- `@character-team` - 角色设计团队
- `@llm-team` - LLM集成团队
- `@data-team` - 数据和持久化团队

### 权限分配建议
- **Admin**: 项目维护者
- **Maintain**: 核心团队成员
- **Write**: 活跃贡献者
- **Triage**: 社区管理员
- **Read**: 一般用户

## 🔧 自定义配置

### 调整保护级别
根据项目需求，可以调整保护级别：

#### 严格模式（生产环境）
- 2个审查者
- 所有状态检查
- 代码所有者审查
- 管理员强制执行

#### 中等模式（开发环境）
- 1个审查者
- 核心状态检查
- 清除过时审查

#### 基础模式（个人项目）
- 1个审查者
- 基本CI检查
- 允许管理员绕过

### 添加自定义检查
要添加新的状态检查：

1. 在 `.github/workflows/` 中创建新工作流
2. 确保工作流有明确的job名称
3. 在分支保护设置中添加状态检查名称
4. 测试工作流执行

## 📊 监控和维护

### 定期检查项目
- ✅ CI工作流执行状况
- ✅ 分支保护规则有效性
- ✅ 团队权限配置
- ✅ 代码审查质量
- ✅ 安全扫描结果

### 更新和优化
- 定期更新CI工作流
- 优化状态检查性能
- 调整保护规则设置
- 培训团队成员

## 🎉 完成确认

配置完成后，您的仓库将拥有：

- ✅ 企业级分支保护规则
- ✅ 全面的CI/CD流水线
- ✅ 安全扫描和质量检查
- ✅ 标准化的贡献流程
- ✅ 自动化的项目管理
- ✅ 专业的状态徽章显示

现在您的 AI Town 项目已准备好接受开源社区的贡献！

## 📞 支持和帮助

如果在配置过程中遇到问题：
1. 检查GitHub Actions日志
2. 验证分支保护设置
3. 确认团队权限配置
4. 查阅GitHub官方文档
5. 提交Issue寻求帮助

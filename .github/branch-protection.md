# GitHub 分支保护规则配置

本文档说明了 AI Town 项目的分支保护规则配置，确保代码质量和项目安全性。

## 🔒 主分支保护 (main)

### 必需状态检查 (Required Status Checks)

- `test` - 测试工作流
- `security` - 安全检查工作流
- `build-and-validate` - 构建验证工作流
- `documentation` - 文档检查工作流
- `compatibility / ubuntu-latest (3.9)` - Ubuntu Python 3.9 兼容性
- `compatibility / ubuntu-latest (3.11)` - Ubuntu Python 3.11 兼容性
- `compatibility / windows-latest (3.9)` - Windows Python 3.9 兼容性
- `compatibility / windows-latest (3.11)` - Windows Python 3.11 兼容性
- `compatibility / macos-latest (3.9)` - macOS Python 3.9 兼容性
- `compatibility / macos-latest (3.11)` - macOS Python 3.11 兼容性

### 主分支保护规则

- ✅ **需要Pull Request审查** - 至少1个审查者批准
- ✅ **消除过时审查** - 新提交时清除之前的批准
- ✅ **需要代码所有者审查** - CODEOWNERS文件指定的审查者
- ✅ **限制推送** - 只允许管理员和维护者直接推送
- ✅ **需要状态检查通过** - 所有必需检查必须通过
- ✅ **需要分支为最新** - 合并前必须与主分支同步
- ✅ **需要解决对话** - 所有PR评论必须解决
- ✅ **限制强制推送** - 禁止强制推送
- ✅ **不允许删除** - 禁止删除主分支

## 🔒 开发分支保护 (develop)

### 必需状态检查

- `test` - 基本测试工作流
- `security` - 安全检查工作流
- `build-and-validate` - 构建验证工作流

### 开发分支保护规则

- ✅ **需要Pull Request审查** - 至少1个审查者批准
- ✅ **需要状态检查通过** - 关键检查必须通过
- ✅ **限制强制推送** - 禁止强制推送

## 📋 配置步骤

1. **前往仓库设置**

   ```text
   Repository → Settings → Branches → Add rule
   ```

2. **配置主分支规则**
   - Branch name pattern: `main`
   - 启用上述所有保护选项
   - 添加所有必需状态检查

3. **配置开发分支规则**
   - Branch name pattern: `develop`
   - 启用基本保护选项
   - 添加核心状态检查

4. **设置CODEOWNERS文件**

   ```text
   # 全局代码审查者
   * @project-maintainer
   
   # 核心系统文件
   /ai_town/core/ @core-team
   /ai_town/events/ @event-system-team
   /.github/ @devops-team
   
   # 文档
   *.md @docs-team
   ```

## 🚦 状态检查说明

### `test` 工作流

- 代码格式检查 (black, isort)
- 代码质量检查 (flake8)
- 单元测试 (pytest)
- 测试覆盖率报告
- 统一事件系统测试

### `security` 工作流

- 安全漏洞扫描 (bandit)
- 依赖项安全检查 (safety)
- 代码安全最佳实践检查

### `build-and-validate` 工作流

- 项目结构验证
- 模块导入完整性测试
- 可视化服务器配置验证

### `documentation` 工作流

- README.md 存在性检查
- 文档完整性验证
- 链接有效性检查

### `compatibility` 工作流

- 多平台兼容性 (Ubuntu, Windows, macOS)
- 多Python版本支持 (3.9, 3.11)
- 基本功能导入测试

## 🔧 本地开发配置

开发者应确保本地环境符合CI检查要求：

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort bandit safety

# 运行本地检查
black --check .
isort --check-only .  
flake8 .
pytest test/ -v --cov=ai_town
bandit -r ai_town/
safety check

# 格式化代码
black .
isort .
```

## 🎯 合规检查清单

在提交PR前，请确保：

- [ ] 所有测试通过 (`pytest test/`)
- [ ] 代码格式正确 (`black --check .`)
- [ ] 导入排序正确 (`isort --check-only .`)
- [ ] 没有lint错误 (`flake8 .`)
- [ ] 没有安全问题 (`bandit -r ai_town/`)
- [ ] 依赖项安全 (`safety check`)
- [ ] 文档更新完整
- [ ] 提交信息清晰

## 🚨 紧急情况处理

如需紧急修复绕过某些检查：

1. **联系项目维护者** - 获得临时权限
2. **创建hotfix分支** - 使用 `hotfix/` 前缀
3. **最小化更改** - 只修复紧急问题
4. **事后补强** - 在后续PR中完善测试和文档

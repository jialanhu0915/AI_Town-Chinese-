# 分支保护设置指南

## 🔧 在GitHub上设置分支保护

1. 前往仓库设置: `Settings → Branches → Add rule`

2. 配置主分支保护:
   - Branch name: `main`
   - ✅ Require pull request reviews (1个审查者)
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require conversation resolution before merging

3. 在"Require status checks"中添加:
   - `test (3.9)` - Python 3.9 测试
   - `test (3.11)` - Python 3.11 测试
   - `security` - 安全检查
   - `build-and-validate` - 构建验证
   - `documentation` - 文档检查

4. 保存设置

## 📋 CI检查说明

**test** - 代码质量和测试 (Python 3.9 & 3.11)
- 代码格式检查 (black)
- 导入排序 (isort) 
- 语法检查 (flake8)
- 单元测试 (pytest)

**security** - 安全扫描
- 代码安全检查 (bandit)
- 依赖项漏洞检查 (safety)

**build-and-validate** - 构建验证
- 核心模块导入测试

**documentation** - 文档检查
- README.md 存在性验证

## 💡 使用建议

推送代码前在本地运行:
```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8 . --select=E9,F63,F7,F82

# 运行测试
pytest test/ -v
```

## 📁 包含的文件

- `.github/workflows/ci.yml` - 简化的CI/CD流水线
- `.github/CODEOWNERS` - 代码审查分配
- `.github/pull_request_template.md` - PR模板
- `.github/ISSUE_TEMPLATE/` - Issue模板

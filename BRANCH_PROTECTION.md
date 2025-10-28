# 分支保护设置指南

## 🔧 在GitHub上设置分支保护

1. 前往仓库设置: `Settings → Branches → Add rule`

2. 配置主分支保护:
   - Branch name: `main`
   - ✅ Require pull request reviews (1个审查者)
   - ✅ Require status checks: `test`, `security`, `build-and-validate`  
   - ✅ Require conversation resolution

3. 保存设置

## 📋 状态检查说明

- `test` - 代码质量和测试
- `security` - 安全扫描
- `build-and-validate` - 构建验证

## � 包含的文件

- `.github/workflows/ci.yml` - CI/CD流水线
- `.github/CODEOWNERS` - 代码审查分配
- `.github/pull_request_template.md` - PR模板
- `.github/ISSUE_TEMPLATE/` - Issue模板

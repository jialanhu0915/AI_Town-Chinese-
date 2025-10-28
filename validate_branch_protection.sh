#!/bin/bash

# AI Town 分支保护验证脚本
# 用于验证所有必需的文件和配置是否正确设置

echo "🔍 AI Town 分支保护配置验证"
echo "================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 验证函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1 存在${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 缺失${NC}"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $1 目录存在${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 目录缺失${NC}"
        return 1
    fi
}

echo "📁 检查核心配置文件..."
missing_files=0

# 检查必需的配置文件
files=(
    ".github/workflows/ci.yml"
    ".github/workflows/branch-protection.yml" 
    ".github/workflows/setup-branch-protection.yml"
    ".github/ISSUE_TEMPLATE/bug_report.md"
    ".github/ISSUE_TEMPLATE/feature_request.md"
    ".github/pull_request_template.md"
    ".github/CODEOWNERS"
    ".github/branch-protection.md"
    ".github/badges.md"
    "BRANCH_PROTECTION_GUIDE.md"
    "requirements.txt"
    "pyproject.toml"
    ".flake8"
    "pytest.ini"
)

for file in "${files[@]}"; do
    if ! check_file "$file"; then
        ((missing_files++))
    fi
done

echo ""
echo "📋 检查项目结构..."

# 检查目录结构
dirs=(
    "ai_town"
    "ai_town/core"
    "ai_town/agents"
    "ai_town/events" 
    "ai_town/ui"
    "test"
    ".github"
    ".github/workflows"
    ".github/ISSUE_TEMPLATE"
)

missing_dirs=0
for dir in "${dirs[@]}"; do
    if ! check_dir "$dir"; then
        ((missing_dirs++))
    fi
done

echo ""
echo "🔧 检查Python模块完整性..."

# 检查核心Python文件
python_files=(
    "ai_town/__init__.py"
    "ai_town/core/world.py"
    "ai_town/agents/base_agent.py"
    "ai_town/events/event_registry.py"
    "ai_town/events/event_formatter.py"
    "ai_town/ui/visualization_server.py"
)

missing_python=0
for file in "${python_files[@]}"; do
    if ! check_file "$file"; then
        ((missing_python++))
    fi
done

echo ""
echo "🚦 检查CI工作流语法..."

# 验证GitHub Actions工作流语法
if command -v yamllint &> /dev/null; then
    echo "运行YAML语法检查..."
    for workflow in .github/workflows/*.yml; do
        if yamllint "$workflow" &> /dev/null; then
            echo -e "${GREEN}✅ $(basename $workflow) 语法正确${NC}"
        else
            echo -e "${YELLOW}⚠️ $(basename $workflow) 可能有语法问题${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠️ yamllint 未安装，跳过语法检查${NC}"
fi

echo ""
echo "🔒 检查分支保护相关配置..."

# 检查CODEOWNERS语法
if [ -f ".github/CODEOWNERS" ]; then
    if grep -q "^[^#].*@" ".github/CODEOWNERS"; then
        echo -e "${GREEN}✅ CODEOWNERS 包含有效的审查者配置${NC}"
    else
        echo -e "${YELLOW}⚠️ CODEOWNERS 可能缺少审查者配置${NC}"
    fi
fi

# 检查PR模板
if [ -f ".github/pull_request_template.md" ]; then
    if grep -q "检查清单" ".github/pull_request_template.md"; then
        echo -e "${GREEN}✅ PR模板包含检查清单${NC}"
    else
        echo -e "${YELLOW}⚠️ PR模板缺少检查清单${NC}"
    fi
fi

echo ""
echo "🧪 运行快速测试..."

# 运行基础Python导入测试
if command -v python &> /dev/null; then
    echo "测试Python模块导入..."
    
    python -c "
try:
    import sys
    sys.path.append('.')
    from ai_town.events.event_registry import event_registry
    print('✅ event_registry 导入成功')
except ImportError as e:
    print(f'❌ event_registry 导入失败: {e}')
    
try:
    from ai_town.events.event_formatter import event_formatter
    print('✅ event_formatter 导入成功')
except ImportError as e:
    print(f'❌ event_formatter 导入失败: {e}')
" 2>/dev/null || echo -e "${YELLOW}⚠️ Python模块导入测试失败${NC}"

else
    echo -e "${YELLOW}⚠️ Python未安装，跳过模块测试${NC}"
fi

echo ""
echo "📊 验证总结"
echo "=============="

total_issues=$((missing_files + missing_dirs + missing_python))

if [ $total_issues -eq 0 ]; then
    echo -e "${GREEN}🎉 所有配置都已正确设置！${NC}"
    echo ""
    echo "✅ 下一步操作："
    echo "   1. 提交所有更改到Git"
    echo "   2. 推送到GitHub仓库"  
    echo "   3. 在GitHub设置中配置分支保护规则"
    echo "   4. 创建测试PR验证配置"
else
    echo -e "${RED}⚠️ 发现 $total_issues 个问题需要解决${NC}"
    echo ""
    echo "🔧 修复建议："
    if [ $missing_files -gt 0 ]; then
        echo "   - 缺失 $missing_files 个必需文件"
    fi
    if [ $missing_dirs -gt 0 ]; then
        echo "   - 缺失 $missing_dirs 个必需目录"
    fi
    if [ $missing_python -gt 0 ]; then
        echo "   - 缺失 $missing_python 个Python模块文件"
    fi
fi

echo ""
echo "📚 更多信息请参考："
echo "   - BRANCH_PROTECTION_GUIDE.md - 完整配置指南"
echo "   - .github/branch-protection.md - 分支保护说明"  
echo "   - .github/badges.md - 状态徽章配置"

exit $total_issues

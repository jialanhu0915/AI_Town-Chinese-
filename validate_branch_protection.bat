@echo off
REM AI Town 分支保护验证脚本 (Windows版本)
REM 用于验证所有必需的文件和配置是否正确设置

echo 🔍 AI Town 分支保护配置验证
echo =================================

setlocal enabledelayedexpansion
set "missing_count=0"

echo 📁 检查核心配置文件...

REM 定义必需文件列表
set files=.github\workflows\ci.yml .github\workflows\branch-protection.yml .github\workflows\setup-branch-protection.yml .github\ISSUE_TEMPLATE\bug_report.md .github\ISSUE_TEMPLATE\feature_request.md .github\pull_request_template.md .github\CODEOWNERS .github\branch-protection.md .github\badges.md BRANCH_PROTECTION_GUIDE.md requirements.txt pyproject.toml .flake8 pytest.ini

for %%f in (%files%) do (
    if exist "%%f" (
        echo ✅ %%f 存在
    ) else (
        echo ❌ %%f 缺失
        set /a missing_count+=1
    )
)

echo.
echo 📋 检查项目结构...

REM 检查目录结构
set dirs=ai_town ai_town\core ai_town\agents ai_town\events ai_town\ui test .github .github\workflows .github\ISSUE_TEMPLATE

for %%d in (%dirs%) do (
    if exist "%%d\" (
        echo ✅ %%d 目录存在
    ) else (
        echo ❌ %%d 目录缺失
        set /a missing_count+=1
    )
)

echo.
echo 🔧 检查Python模块完整性...

REM 检查核心Python文件
set python_files=ai_town\__init__.py ai_town\core\world.py ai_town\agents\base_agent.py ai_town\events\event_registry.py ai_town\events\event_formatter.py ai_town\ui\visualization_server.py

for %%p in (%python_files%) do (
    if exist "%%p" (
        echo ✅ %%p 存在
    ) else (
        echo ❌ %%p 缺失
        set /a missing_count+=1
    )
)

echo.
echo 🔒 检查分支保护相关配置...

REM 检查CODEOWNERS文件内容
if exist ".github\CODEOWNERS" (
    findstr /C:"@" ".github\CODEOWNERS" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ CODEOWNERS 包含有效的审查者配置
    ) else (
        echo ⚠️ CODEOWNERS 可能缺少审查者配置
    )
) else (
    echo ❌ CODEOWNERS 文件缺失
    set /a missing_count+=1
)

REM 检查PR模板
if exist ".github\pull_request_template.md" (
    findstr /C:"检查清单" ".github\pull_request_template.md" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ PR模板包含检查清单
    ) else (
        echo ⚠️ PR模板缺少检查清单
    )
)

echo.
echo 🧪 运行快速测试...

REM 测试Python模块导入
where python >nul 2>&1
if !errorlevel! equ 0 (
    echo 测试Python模块导入...
    python -c "try: from ai_town.events.event_registry import event_registry; print('✅ event_registry 导入成功'); except: print('❌ event_registry 导入失败')" 2>nul
    python -c "try: from ai_town.events.event_formatter import event_formatter; print('✅ event_formatter 导入成功'); except: print('❌ event_formatter 导入失败')" 2>nul
) else (
    echo ⚠️ Python未安装，跳过模块测试
)

echo.
echo 📊 验证总结
echo ==============

if !missing_count! equ 0 (
    echo 🎉 所有配置都已正确设置！
    echo.
    echo ✅ 下一步操作：
    echo    1. 提交所有更改到Git
    echo    2. 推送到GitHub仓库
    echo    3. 在GitHub设置中配置分支保护规则
    echo    4. 创建测试PR验证配置
    set exit_code=0
) else (
    echo ⚠️ 发现 !missing_count! 个问题需要解决
    echo.
    echo 🔧 请检查上述缺失的文件和目录
    set exit_code=1
)

echo.
echo 📚 更多信息请参考：
echo    - BRANCH_PROTECTION_GUIDE.md - 完整配置指南
echo    - .github\branch-protection.md - 分支保护说明
echo    - .github\badges.md - 状态徽章配置

pause
exit /b !exit_code!

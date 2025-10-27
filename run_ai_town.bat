@echo off
REM AI Town 模拟启动脚本

echo ========================================
echo           AI Town 模拟系统
echo ========================================
echo.

REM 检查虚拟环境
if not exist ".venv\" (
    echo 错误: 未找到虚拟环境 .venv
    echo 请先创建虚拟环境: python -m venv .venv
    echo 然后激活并安装依赖: .venv\Scripts\activate ^&^& pip install -r ai_town\requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate

REM 检查依赖
echo 检查依赖包...
python -c "import fastapi, pydantic, sqlalchemy" 2>nul
if %errorlevel% neq 0 (
    echo 警告: 部分依赖包未安装，尝试安装...
    pip install -r ai_town\requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 设置环境变量
set PYTHONPATH=%CD%

REM 启动选项菜单
:menu
echo.
echo 请选择启动选项:
echo 1. 运行 AI Town 模拟 (交互式)
echo 2. 运行 AI Town 模拟 (指定时长)
echo 3. 启动 FastAPI 服务器
echo 4. 测试基本功能
echo 5. 查看项目信息
echo 6. 退出
echo.
set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto run_interactive
if "%choice%"=="2" goto run_timed
if "%choice%"=="3" goto start_api
if "%choice%"=="4" goto test_basic
if "%choice%"=="5" goto show_info
if "%choice%"=="6" goto exit
echo 无效选项，请重新选择
goto menu

:run_interactive
echo.
echo 启动交互式 AI Town 模拟...
echo 按 Ctrl+C 停止模拟
echo.
python ai_town\simulation_runner.py
goto menu

:run_timed
echo.
set /p duration=请输入模拟时长(分钟): 
if "%duration%"=="" (
    echo 时长不能为空
    goto menu
)
echo.
echo 启动 AI Town 模拟，运行 %duration% 分钟...
echo 按 Ctrl+C 提前停止
echo.
python -c "
import asyncio
import sys
sys.path.append('.')
from ai_town.simulation_runner import main
from ai_town.core.world import World
from ai_town.core.time_manager import GameTime
from ai_town.agents.characters.alice import Alice

async def timed_simulation():
    GameTime.initialize(time_multiplier=10.0)
    world = World()
    alice = Alice()
    world.add_agent(alice)
    print(f'🏃 Running simulation for %duration% minutes...')
    await world.run_simulation(duration_minutes=%duration%)

asyncio.run(timed_simulation())
"
goto menu

:start_api
echo.
echo 启动 FastAPI 服务器...
echo 服务地址: http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.
python -m uvicorn ai_town.api.main:app --reload --host 0.0.0.0 --port 8000
goto menu

:test_basic
echo.
echo 运行基本功能测试...
echo.
python -c "
from ai_town.core.time_manager import GameTime
from ai_town.core.world import World
from ai_town.agents.characters.alice import Alice

print('🧪 Testing AI Town components...')
print('⏰ Testing GameTime...')
GameTime.initialize()
print(f'   Current game time: {GameTime.format_time()}')
print(f'   Time of day: {GameTime.get_time_of_day()}')

print('🗺️  Testing World...')
world = World()
print(f'   Map size: {world.map.width}x{world.map.height}')
print(f'   Buildings: {len(world.map.buildings)}')

print('👤 Testing Alice agent...')
alice = Alice()
print(f'   Name: {alice.name}, Age: {alice.age}')
print(f'   Position: ({alice.position.x}, {alice.position.y}) in {alice.position.area}')

world.add_agent(alice)
print(f'   Added to world. Total agents: {len(world.agents)}')

print('✅ All basic tests passed!')
"
echo.
echo 测试完成！
pause
goto menu

:show_info
echo.
echo ========================================
echo           AI Town 项目信息
echo ========================================
echo.
echo 🏘️ AI Town - 智能体小镇模拟系统
echo.
echo 📁 项目结构:
echo   ai_town/
echo   ├── agents/          # 智能体系统
echo   ├── core/            # 核心组件 (世界、时间)
echo   ├── environment/     # 环境系统 (地图、物理)
echo   ├── social/          # 社交系统
echo   ├── api/             # API 接口
echo   └── simulation/      # 模拟引擎
echo.
echo 🤖 当前智能体:
echo   - Alice: 咖啡店老板，友好外向
echo   - Bob: 书店老板，内向博学 (可扩展)
echo   - Charlie: 办公室职员，新来镇上 (可扩展)
echo.
echo 🌟 核心特性:
echo   - 多智能体自主生活模拟
echo   - 记忆系统和反思机制
echo   - 社交互动和关系管理
echo   - 分层行为规划
echo   - 虚拟小镇环境
echo.
echo 📚 基于斯坦福大学 AI Town 论文实现
echo.
pause
goto menu

:exit
echo.
echo 感谢使用 AI Town 模拟系统！
echo 🏘️ 再见！
echo.
pause
exit /b 0

@echo off
REM AI Town ģ�������ű�

echo ========================================
echo           AI Town ģ��ϵͳ
echo ========================================
echo.

REM ������⻷��
if not exist ".venv\" (
    echo ����: δ�ҵ����⻷�� .venv
    echo ���ȴ������⻷��: python -m venv .venv
    echo Ȼ�󼤻��װ����: .venv\Scripts\activate ^&^& pip install -r ai_town\requirements.txt
    pause
    exit /b 1
)

REM �������⻷��
echo �������⻷��...
call .venv\Scripts\activate

REM �������
echo ���������...
python -c "import fastapi, pydantic, sqlalchemy" 2>nul
if %errorlevel% neq 0 (
    echo ����: ����������δ��װ�����԰�װ...
    pip install -r ai_town\requirements.txt
    if %errorlevel% neq 0 (
        echo ����: ������װʧ��
        pause
        exit /b 1
    )
)

REM ���û�������
set PYTHONPATH=%CD%

REM ����ѡ��˵�
:menu
echo.
echo ��ѡ������ѡ��:
echo 1. ���� AI Town ģ�� (�����а�)
echo 2. ���� AI Town ģ�� (ָ��ʱ��)
echo 3. �������ӻ����� (�Ƽ�!)
echo 4. ���Ի�������
echo 5. �鿴��Ŀ��Ϣ
echo 6. �˳�
echo.
set /p choice=������ѡ�� (1-6): 

if "%choice%"=="1" goto run_interactive
if "%choice%"=="2" goto run_timed
if "%choice%"=="3" goto start_visualization_direct
if "%choice%"=="4" goto test_basic
if "%choice%"=="5" goto show_info
if "%choice%"=="6" goto exit

:start_visualization_direct
echo.
echo ? ���� AI С����ӻ�����...
echo ? ��������ʵ�ַ: http://localhost:8000
echo ? ���ӻ��������������
echo ??  �� Ctrl+C ֹͣ����
echo.
echo ����������������д�: http://localhost:8000
echo.
python ai_town\ui\visualization_server.py
goto menu
echo ��Чѡ�������ѡ��
goto menu

:run_interactive
echo.
echo ��������ʽ AI Town ģ��...
echo �� Ctrl+C ֹͣģ��
echo.
python ai_town\simulation_runner.py
goto menu

:run_timed
echo.
set /p duration=������ģ��ʱ��(����): 
if "%duration%"=="" (
    echo ʱ������Ϊ��
    goto menu
)
echo.
echo ���� AI Town ģ�⣬���� %duration% ����...
echo �� Ctrl+C ��ǰֹͣ
echo.
python -c "
import asyncio
import sys
sys.path.append('.')
from ai_town.core.world import World
from ai_town.core.time_manager import GameTime
from ai_town.agents.agent_manager import agent_manager

async def timed_simulation():
    GameTime.initialize(time_multiplier=10.0)
    world = World()
    
    # ʹ�����������������������
    created_agents = agent_manager.create_default_agents()
    for agent in created_agents:
        world.add_agent(agent)
    
    print(f'? ģ������ %duration% ���ӣ����� {len(created_agents)} ��������...')
    await world.run_simulation(duration_minutes=%duration%)

asyncio.run(timed_simulation())
"
goto menu

:start_api
echo.
echo ��ѡ������ģʽ:
echo 1. �������ӻ����� (�Ƽ�)
echo 2. ���� API ������
echo.
set /p api_choice=��ѡ�� (1-2): 

if "%api_choice%"=="1" goto start_visualization
if "%api_choice%"=="2" goto start_basic_api

:start_visualization
echo.
echo ? ���� AI С����ӻ�����...
echo ? ��������ʵ�ַ: http://localhost:8000
echo ? ���ӻ��������������
echo ??  �� Ctrl+C ֹͣ����
echo.
python ai_town\ui\visualization_server.py
goto menu

:start_basic_api
echo.
echo �������� API ������...
echo �����ַ: http://localhost:8000
echo API �ĵ�: http://localhost:8000/docs
echo �� Ctrl+C ֹͣ����
echo.
python -m uvicorn ai_town.api.main:app --reload --host 0.0.0.0 --port 8000
goto menu

:test_basic
echo.
echo ���л������ܲ���...
echo.
python test_basic.py
echo.
echo ������ɣ�
pause
goto menu

:show_info
echo.
echo ========================================
echo           AI Town ��Ŀ��Ϣ
echo ========================================
echo.
echo ?? AI Town - ������С��ģ��ϵͳ
echo.
echo ? ��Ŀ�ṹ:
echo   ai_town/
echo   ������ agents/          # ������ϵͳ
echo   ������ core/            # ������� (���硢ʱ��)
echo   ������ environment/     # ����ϵͳ (��ͼ������)
echo   ������ social/          # �罻ϵͳ
echo   ������ api/             # API �ӿ�
echo   ������ simulation/      # ģ������
echo.
echo ? ��ǰ������:
echo   - Alice: ���ȵ��ϰ壬�Ѻ�����
echo   - Bob: ����ϰ壬����ѧ (����չ)
echo   - Charlie: �칫��ְԱ���������� (����չ)
echo.
echo ? ��������:
echo   - ����������������ģ��
echo   - ����ϵͳ�ͷ�˼����
echo   - �罻�����͹�ϵ����
echo   - �ֲ���Ϊ�滮
echo   - ����С�򻷾�
echo.
echo ? ����˹̹����ѧ AI Town ����ʵ��
echo.
pause
goto menu

:exit
echo.
echo ��лʹ�� AI Town ģ��ϵͳ��
echo ?? �ټ���
echo.
pause
exit /b 0

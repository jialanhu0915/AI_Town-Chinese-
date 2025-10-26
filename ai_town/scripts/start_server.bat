@echo off
REM 启动 FastAPI 开发服务器（开发模式）
call .venv\Scripts\activate
python -m uvicorn ai_town.api.main:app --reload --port 8000

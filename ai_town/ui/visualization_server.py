"""
AI Town 可视化 WebSocket 服务
提供实时数据传输和模拟控制
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Set

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ai_town.agents.agent_manager import agent_manager
from ai_town.core.time_manager import GameTime
from ai_town.core.world import World
from ai_town.events.event_formatter import event_formatter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 先声明管理器变量
manager = None

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("AI Town 可视化服务启动")
    yield
    # 关闭时的清理
    global manager
    if manager and manager.is_running:
        await manager.pause_simulation()
    logger.info("AI Town 可视化服务关闭")


app = FastAPI(title="AI Town 可视化服务", lifespan=lifespan)

# 挂载静态文件
static_dir = Path(__file__).parent / "templates"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# 直接提供JavaScript文件
@app.get("/visualization.js")
async def get_js():
    """返回JavaScript文件"""
    from fastapi.responses import Response

    js_file = static_dir / "visualization.js"
    with open(js_file, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content=content, media_type="application/javascript")


class VisualizationManager:
    """可视化管理器 - 处理模拟状态和WebSocket连接"""

    def __init__(self):
        self.world: World = None
        self.is_running = False
        self.connections: Set[WebSocket] = set()
        self.simulation_task: asyncio.Task = None

    async def add_connection(self, websocket: WebSocket):
        """添加WebSocket连接"""
        self.connections.add(websocket)
        logger.info(f"新的WebSocket连接，当前连接数: {len(self.connections)}")

        # 发送当前世界状态
        if self.world:
            await self.broadcast_world_state()

    async def remove_connection(self, websocket: WebSocket):
        """移除WebSocket连接"""
        self.connections.discard(websocket)
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.connections)}")

    async def broadcast_message(self, message: dict):
        """广播消息给所有连接的客户端"""
        if not self.connections:
            return

        disconnected = set()
        for websocket in self.connections:
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.warning(f"发送消息失败: {e}")
                disconnected.add(websocket)

        # 清理断开的连接
        self.connections -= disconnected

    async def broadcast_world_state(self):
        """广播世界状态"""
        if not self.world:
            return

        world_state = self.world.get_world_state()

        # 添加额外的统计信息
        stats = self.world.get_simulation_stats()
        world_state.update(
            {
                "step_count": stats.get("step_count", 0),
                "total_interactions": stats.get("total_interactions", 0),
                "total_movements": stats.get("total_movements", 0),
                "events": [
                    self._serialize_event(event) for event in self.world.current_events[-10:]
                ],  # 最近10个事件
            }
        )

        message = {"type": "world_state", "data": world_state}
        await self.broadcast_message(message)

    def _serialize_event(self, event):
        """序列化事件对象"""
        # 使用统一的事件格式化器
        raw_event_data = {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type,
            "description": event.description,
            "participants": event.participants,
            "duration": event.duration,
        }

        # 添加格式化后的显示信息
        display_info = event_formatter.format_event_display(raw_event_data)
        raw_event_data.update(display_info)

        return raw_event_data

    async def start_simulation(self):
        """开始模拟"""
        if self.is_running:
            return

        # 初始化世界（如果还没有）
        if not self.world:
            await self.initialize_world()

        self.is_running = True

        # 启动模拟任务
        self.simulation_task = asyncio.create_task(self._simulation_loop())

        await self.broadcast_message(
            {"type": "simulation_started", "data": {"message": "模拟已开始"}}
        )

        logger.info("模拟已开始")

    async def pause_simulation(self):
        """暂停模拟"""
        if not self.is_running:
            return

        self.is_running = False

        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass

        await self.broadcast_message(
            {"type": "simulation_paused", "data": {"message": "模拟已暂停"}}
        )

        logger.info("模拟已暂停")

    async def reset_simulation(self):
        """重置模拟"""
        await self.pause_simulation()

        await self.initialize_world()

        await self.broadcast_message(
            {"type": "simulation_reset", "data": {"message": "模拟已重置"}}
        )

        logger.info("模拟已重置")

    async def initialize_world(self):
        """初始化世界"""
        # 初始化游戏时间
        GameTime.initialize(time_multiplier=10.0)

        # 创建世界
        self.world = World()

        # 使用智能体管理器创建并添加智能体
        created_agents = agent_manager.create_default_agents()

        for agent in created_agents:
            self.world.add_agent(agent)

        logger.info(f"世界初始化完成，共有 {len(self.world.agents)} 个智能体")

    async def _simulation_loop(self):
        """模拟主循环"""
        try:
            while self.is_running:
                # 执行一步
                await self.world.step()

                # 广播世界状态
                await self.broadcast_world_state()

                # 等待下一步
                await asyncio.sleep(1.0)  # 1秒一步，便于观察

        except asyncio.CancelledError:
            logger.info("模拟循环已取消")
        except Exception as e:
            logger.error(f"模拟循环错误: {e}")
            self.is_running = False


# 初始化全局管理器实例
manager = VisualizationManager()


@app.get("/api/event-metadata")
async def get_event_metadata():
    """获取事件元数据用于前端显示"""
    return event_formatter.get_all_event_types_for_frontend()


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """返回主页面"""
    html_file = static_dir / "index.html"
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await websocket.accept()
    await manager.add_connection(websocket)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理不同类型的消息
            if message["type"] == "start_simulation":
                await manager.start_simulation()
            elif message["type"] == "pause_simulation":
                await manager.pause_simulation()
            elif message["type"] == "reset_simulation":
                await manager.reset_simulation()
            else:
                logger.warning(f"未知消息类型: {message['type']}")

    except WebSocketDisconnect:
        await manager.remove_connection(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await manager.remove_connection(websocket)


if __name__ == "__main__":
    print("🏘️ 启动 AI 小镇可视化服务...")
    print("📱 请在浏览器中访问: http://localhost:8000")
    print("⏹️  按 Ctrl+C 停止服务")

    uvicorn.run(
        "visualization_server:app", host="0.0.0.0", port=8000, reload=False, log_level="info"
    )

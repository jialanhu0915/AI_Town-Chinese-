"""
测试配置和通用测试工具
"""

import pytest
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_agent_data():
    """提供测试用的智能体数据"""
    return {
        'alice': {
            'agent_id': 'alice',
            'name': 'Alice',
            'position': {'x': 25, 'y': 25, 'area': 'coffee_shop'},
            'occupation': 'coffee_shop_owner'
        },
        'bob': {
            'agent_id': 'bob', 
            'name': 'Bob',
            'position': {'x': 35, 'y': 20, 'area': 'bookstore'},
            'occupation': 'bookstore_owner'
        },
        'charlie': {
            'agent_id': 'charlie',
            'name': 'Charlie', 
            'position': {'x': 60, 'y': 30, 'area': 'office_1'},
            'occupation': 'office_worker'
        }
    }


@pytest.fixture
def sample_event_data():
    """提供测试用的事件数据"""
    return [
        {
            'event_type': 'coffee_making',
            'description': 'Alice is making espresso',
            'participants': ['alice'],
            'coffee_type': 'espresso',
            'timestamp': '2024-01-01T10:00:00'
        },
        {
            'event_type': 'movement',
            'description': 'alice moved from coffee_shop to park',
            'participants': ['alice'],
            'timestamp': '2024-01-01T10:05:00'
        },
        {
            'event_type': 'reading',
            'description': 'Bob is reading a philosophy book',
            'participants': ['bob'],
            'material': 'philosophy book',
            'timestamp': '2024-01-01T10:10:00'
        }
    ]

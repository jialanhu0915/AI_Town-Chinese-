"""
AI Town 环境系统 - 世界地图
"""

import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TerrainType(Enum):
    """地形类型"""

    WALKABLE = "walkable"
    BLOCKED = "blocked"
    WATER = "water"
    BUILDING = "building"
    ROAD = "road"


@dataclass
class MapTile:
    """地图瓦片"""

    x: int
    y: int
    terrain_type: TerrainType
    area_name: str = "unknown"
    building_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Building:
    """建筑物"""

    id: str
    name: str
    building_type: str  # home, shop, office, park, etc.
    entrance_x: int
    entrance_y: int
    width: int
    height: int
    description: str = ""
    capacity: int = 10
    current_occupants: List[str] = None

    def __post_init__(self):
        if self.current_occupants is None:
            self.current_occupants = []


class GameMap:
    """
    游戏地图管理器

    管理整个AI小镇的地图布局、建筑物、路径等
    """

    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height

        # 初始化地图网格
        self.tiles: Dict[Tuple[int, int], MapTile] = {}
        self.buildings: Dict[str, Building] = {}

        # 区域定义
        self.areas: Dict[str, List[Tuple[int, int]]] = {}

        # 路径缓存
        self.path_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], List[Tuple[int, int]]] = {}

        # 初始化默认地图
        self._create_default_map()

    def _create_default_map(self):
        """创建默认的小镇地图"""
        # 首先设置所有瓦片为可行走的草地
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[(x, y)] = MapTile(
                    x=x, y=y, terrain_type=TerrainType.WALKABLE, area_name="outdoors"
                )

        # 创建建筑物和区域
        self._create_buildings()
        self._create_roads()
        self._create_areas()

    def _create_buildings(self):
        """创建建筑物"""
        buildings_config = [
            # 住宅区
            {
                "id": "house_1",
                "name": "Alice's House",
                "type": "home",
                "x": 5,
                "y": 5,
                "w": 8,
                "h": 6,
            },
            {
                "id": "house_2",
                "name": "Bob's House",
                "type": "home",
                "x": 5,
                "y": 15,
                "w": 8,
                "h": 6,
            },
            {
                "id": "house_3",
                "name": "Charlie's House",
                "type": "home",
                "x": 5,
                "y": 25,
                "w": 8,
                "h": 6,
            },
            # 商业区
            {
                "id": "coffee_shop",
                "name": "Alice's Coffee Shop",
                "type": "shop",
                "x": 20,
                "y": 20,
                "w": 10,
                "h": 8,
            },
            {
                "id": "bookstore",
                "name": "The Book Corner",
                "type": "shop",
                "x": 35,
                "y": 20,
                "w": 8,
                "h": 6,
            },
            {
                "id": "grocery",
                "name": "Town Grocery",
                "type": "shop",
                "x": 20,
                "y": 35,
                "w": 12,
                "h": 8,
            },
            # 办公区
            {
                "id": "office_1",
                "name": "Town Office",
                "type": "office",
                "x": 60,
                "y": 30,
                "w": 15,
                "h": 10,
            },
            {
                "id": "library",
                "name": "Public Library",
                "type": "office",
                "x": 60,
                "y": 15,
                "w": 12,
                "h": 8,
            },
            # 娱乐设施
            {
                "id": "park",
                "name": "Central Park",
                "type": "park",
                "x": 45,
                "y": 45,
                "w": 20,
                "h": 15,
            },
            {
                "id": "restaurant",
                "name": "Town Restaurant",
                "type": "restaurant",
                "x": 25,
                "y": 50,
                "w": 10,
                "h": 8,
            },
        ]

        for config in buildings_config:
            building = Building(
                id=config["id"],
                name=config["name"],
                building_type=config["type"],
                entrance_x=config["x"],
                entrance_y=config["y"],
                width=config["w"],
                height=config["h"],
                description=f"A {config['type']} in the town",
            )

            self.buildings[building.id] = building

            # 在地图上标记建筑物区域
            for x in range(config["x"], config["x"] + config["w"]):
                for y in range(config["y"], config["y"] + config["h"]):
                    if (x, y) in self.tiles:
                        self.tiles[(x, y)].terrain_type = TerrainType.BUILDING
                        self.tiles[(x, y)].area_name = config["id"]
                        self.tiles[(x, y)].building_id = config["id"]

            # 设置入口为可行走
            entrance = (config["x"], config["y"])
            if entrance in self.tiles:
                self.tiles[entrance].terrain_type = TerrainType.WALKABLE

    def _create_roads(self):
        """创建道路网络"""
        # 主要街道 (水平)
        for x in range(0, self.width):
            for y in [12, 32, 52]:
                if (x, y) in self.tiles:
                    self.tiles[(x, y)].terrain_type = TerrainType.ROAD
                    self.tiles[(x, y)].area_name = "road"

        # 主要街道 (垂直)
        for y in range(0, self.height):
            for x in [18, 42, 58]:
                if (x, y) in self.tiles:
                    self.tiles[(x, y)].terrain_type = TerrainType.ROAD
                    self.tiles[(x, y)].area_name = "road"

    def _create_areas(self):
        """定义区域"""
        self.areas = {
            "residential": [(x, y) for x in range(0, 20) for y in range(0, 40)],
            "commercial": [(x, y) for x in range(20, 50) for y in range(15, 45)],
            "office": [(x, y) for x in range(50, 80) for y in range(10, 50)],
            "park": [(x, y) for x in range(45, 65) for y in range(45, 60)],
            "downtown": [(x, y) for x in range(20, 50) for y in range(20, 40)],
        }

    def is_walkable(self, x: int, y: int) -> bool:
        """检查位置是否可行走"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        tile = self.tiles.get((x, y))
        if not tile:
            return False

        return tile.terrain_type in [TerrainType.WALKABLE, TerrainType.ROAD]

    def get_tile(self, x: int, y: int) -> Optional[MapTile]:
        """获取指定位置的瓦片"""
        return self.tiles.get((x, y))

    def get_building_at(self, x: int, y: int) -> Optional[Building]:
        """获取指定位置的建筑物"""
        tile = self.get_tile(x, y)
        if tile and tile.building_id:
            return self.buildings.get(tile.building_id)
        return None

    def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        使用 A* 算法寻找路径

        Args:
            start: 起始位置 (x, y)
            end: 目标位置 (x, y)

        Returns:
            路径点列表
        """
        # 检查缓存
        cache_key = (start, end)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]

        # A* 算法实现
        from heapq import heappop, heappush

        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = pos
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if self.is_walkable(nx, ny):
                    neighbors.append((nx, ny))
            return neighbors

        # A* 主算法
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}

        while open_set:
            current = heappop(open_set)[1]

            if current == end:
                # 重建路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()

                # 缓存路径
                self.path_cache[cache_key] = path
                return path

            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    heappush(open_set, (f_score[neighbor], neighbor))

        # 无法找到路径，返回空列表
        return []

    def get_nearby_agents(
        self, center_x: float, center_y: float, radius: float, agent_positions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """获取指定范围内的其他智能体"""
        nearby = []

        for agent_id, agent_data in agent_positions.items():
            agent_x = agent_data.get("x", 0)
            agent_y = agent_data.get("y", 0)

            distance = math.sqrt((agent_x - center_x) ** 2 + (agent_y - center_y) ** 2)

            if distance <= radius:
                nearby.append(
                    {
                        "id": agent_id,
                        "name": agent_data.get("name", agent_id),
                        "x": agent_x,
                        "y": agent_y,
                        "area": self.get_area_name(int(agent_x), int(agent_y)),
                        "distance": distance,
                    }
                )

        return nearby

    def get_area_name(self, x: int, y: int) -> str:
        """获取指定位置的区域名称"""
        tile = self.get_tile(x, y)
        if tile:
            return tile.area_name
        return "unknown"

    def get_buildings_in_area(self, area_name: str) -> List[Building]:
        """获取指定区域的所有建筑物"""
        return [
            building
            for building in self.buildings.values()
            if any(
                self.get_tile(building.entrance_x + dx, building.entrance_y + dy)
                and self.get_tile(building.entrance_x + dx, building.entrance_y + dy).area_name
                == area_name
                for dx in range(building.width)
                for dy in range(building.height)
            )
        ]

    def add_agent_to_building(self, agent_id: str, building_id: str) -> bool:
        """将智能体添加到建筑物中"""
        building = self.buildings.get(building_id)
        if building and len(building.current_occupants) < building.capacity:
            if agent_id not in building.current_occupants:
                building.current_occupants.append(agent_id)
            return True
        return False

    def remove_agent_from_building(self, agent_id: str, building_id: str):
        """从建筑物中移除智能体"""
        building = self.buildings.get(building_id)
        if building and agent_id in building.current_occupants:
            building.current_occupants.remove(agent_id)

    def get_map_data(self) -> Dict[str, Any]:
        """获取地图数据用于前端渲染"""
        return {
            "width": self.width,
            "height": self.height,
            "buildings": [
                {
                    "id": building.id,
                    "name": building.name,
                    "type": building.building_type,
                    "x": building.entrance_x,
                    "y": building.entrance_y,
                    "width": building.width,
                    "height": building.height,
                    "occupants": building.current_occupants,
                }
                for building_id, building in self.buildings.items()
            ],
            "areas": self.areas,
        }

    def save_map(self, filepath: str):
        """保存地图到文件"""
        map_data = self.get_map_data()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)

    def load_map(self, filepath: str):
        """从文件加载地图"""
        with open(filepath, "r", encoding="utf-8") as f:
            map_data = json.load(f)

        self.width = map_data["width"]
        self.height = map_data["height"]

        # 重建建筑物
        self.buildings.clear()
        for building_data in map_data["buildings"].values():
            building = Building(
                id=building_data["id"],
                name=building_data["name"],
                building_type=building_data["type"],
                entrance_x=building_data["x"],
                entrance_y=building_data["y"],
                width=building_data["width"],
                height=building_data["height"],
                current_occupants=building_data["occupants"],
            )
            self.buildings[building.id] = building

        self.areas = map_data["areas"]

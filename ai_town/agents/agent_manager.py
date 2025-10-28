"""
智能体管理器
负责智能体的创建、注册和管理
"""

from typing import Dict, List, Optional, Type

from ai_town.agents.base_agent import BaseAgent
from ai_town.agents.characters import Alice, Bob, Charlie


class AgentRegistry:
    """智能体注册表"""
    
    _agents: Dict[str, Type[BaseAgent]] = {}
    _default_agents = {
        'alice': Alice,
        'bob': Bob,
        'charlie': Charlie
    }
    
    @classmethod
    def register_agent(cls, agent_id: str, agent_class: Type[BaseAgent]):
        """注册新的智能体类型"""
        cls._agents[agent_id] = agent_class
    
    @classmethod
    def get_agent_class(cls, agent_id: str) -> Optional[Type[BaseAgent]]:
        """获取智能体类"""
        # 先查找自定义注册的智能体
        if agent_id in cls._agents:
            return cls._agents[agent_id]
        # 再查找默认智能体
        return cls._default_agents.get(agent_id)
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """获取所有可用的智能体ID"""
        all_agents = set(cls._default_agents.keys())
        all_agents.update(cls._agents.keys())
        return list(all_agents)
    
    @classmethod
    def create_agent(cls, agent_id: str) -> Optional[BaseAgent]:
        """创建智能体实例"""
        agent_class = cls.get_agent_class(agent_id)
        if agent_class:
            return agent_class()
        return None


class AgentManager:
    """智能体管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.registry = AgentRegistry()
    
    def create_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """创建并添加智能体"""
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        agent = self.registry.create_agent(agent_id)
        if agent:
            self.agents[agent_id] = agent
        return agent
    
    def add_agent(self, agent: BaseAgent):
        """添加已创建的智能体"""
        self.agents[agent.agent_id] = agent
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除智能体"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """获取智能体"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """获取所有智能体"""
        return self.agents.copy()
    
    def get_agent_count(self) -> int:
        """获取智能体数量"""
        return len(self.agents)
    
    def create_default_agents(self) -> List[BaseAgent]:
        """创建默认的智能体集合"""
        default_agent_ids = ['alice', 'bob', 'charlie']
        created_agents = []
        
        for agent_id in default_agent_ids:
            agent = self.create_agent(agent_id)
            if agent:
                created_agents.append(agent)
        
        return created_agents
    
    def get_agents_by_area(self, area: str) -> List[BaseAgent]:
        """获取指定区域的所有智能体"""
        return [agent for agent in self.agents.values() 
                if agent.position.area == area]
    
    def get_agents_by_occupation(self, occupation: str) -> List[BaseAgent]:
        """获取指定职业的所有智能体"""
        return [agent for agent in self.agents.values() 
                if agent.occupation == occupation]


# 全局智能体管理器实例
agent_manager = AgentManager()


def register_custom_agent(agent_id: str, agent_class: Type[BaseAgent]):
    """注册自定义智能体（便捷函数）"""
    AgentRegistry.register_agent(agent_id, agent_class)


def create_agent(agent_id: str) -> Optional[BaseAgent]:
    """创建智能体（便捷函数）"""
    return agent_manager.create_agent(agent_id)


def get_available_agent_types() -> List[str]:
    """获取可用的智能体类型（便捷函数）"""
    return AgentRegistry.get_available_agents()

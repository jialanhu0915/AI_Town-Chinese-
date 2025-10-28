"""
事件格式化工具
基于事件注册表提供统一的事件描述生成和显示格式化
"""

from typing import Dict, Any, Optional
from ai_town.events.event_registry import event_registry, EventMetadata


class EventFormatter:
    """统一事件格式化器"""
    
    def __init__(self, language: str = "zh"):
        self.language = language
        self.registry = event_registry
    
    def format_event_display(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化事件显示信息
        
        Args:
            event_data: 事件数据，包含 event_type, description, participants 等
            
        Returns:
            格式化后的显示数据
        """
        event_type = event_data.get('event_type', 'unknown')
        metadata = self.registry.get_event_metadata(event_type)
        
        if not metadata:
            # fallback to default formatting
            return self._format_unknown_event(event_data)
        
        # 提取事件参数
        params = self._extract_event_params(event_data, metadata)
        
        # 生成描述
        description = self._generate_description(metadata, params)
        
        return {
            'type': event_type,
            'icon': metadata.icon,
            'typeLabel': metadata.display_names.get(self.language, metadata.display_names.get('en', event_type)),
            'description': description,
            'participants': self._format_participants(event_data.get('participants', [])),
            'color': metadata.color,
            'category': metadata.category.value,
            'tags': metadata.tags
        }
    
    def _extract_event_params(self, event_data: Dict[str, Any], metadata: EventMetadata) -> Dict[str, str]:
        """从事件数据中提取参数"""
        params = {}
        
        # 基础参数
        participants = event_data.get('participants', [])
        if participants:
            params['agent_name'] = self._get_agent_display_name(participants[0])
            if len(participants) > 1:
                params['target_name'] = self._get_agent_display_name(participants[1])
        
        # 从描述中提取位置信息
        description = event_data.get('description', '')
        
        # 移动事件特殊处理
        if metadata.event_id == 'movement':
            import re
            move_match = re.search(r'moved from\s+(\w+)\s+to\s+(\w+)', description)
            if move_match:
                params['from_area'] = self._get_area_display_name(move_match.group(1))
                params['to_area'] = self._get_area_display_name(move_match.group(2))
        
        # 从事件数据中提取其他参数
        for key in ['coffee_type', 'meeting_type', 'exercise_type', 'skill', 'topic', 'material']:
            if key in event_data:
                params[key] = str(event_data[key])
        
        # 设置默认值
        params.setdefault('agent_name', '某人')
        params.setdefault('target_name', '其他人')
        params.setdefault('coffee_type', '咖啡')
        params.setdefault('meeting_type', '会议')
        params.setdefault('exercise_type', '运动')
        params.setdefault('skill', '新技能')
        params.setdefault('topic', '相关内容')
        params.setdefault('material', '资料')
        params.setdefault('from_area', '某处')
        params.setdefault('to_area', '另一处')
        
        return params
    
    def _generate_description(self, metadata: EventMetadata, params: Dict[str, str]) -> str:
        """生成事件描述"""
        template = metadata.description_template.get(
            self.language, 
            metadata.description_template.get('en', '{agent_name} performed {event_type}')
        )
        
        try:
            return template.format(**params)
        except KeyError as e:
            # 如果参数缺失，使用简化描述
            return f"{params.get('agent_name', '某人')} {metadata.display_names.get(self.language, metadata.event_id)}"
    
    def _format_participants(self, participants: list) -> str:
        """格式化参与者列表"""
        if not participants:
            return ""
        
        names = [self._get_agent_display_name(p) for p in participants]
        if len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return f"{names[0]} 和 {names[1]}"
        else:
            return f"{names[0]} 等 {len(names)} 人"
    
    def _get_agent_display_name(self, agent_id: str) -> str:
        """获取智能体显示名称"""
        names = {
            'alice': 'Alice (咖啡店老板)',
            'bob': 'Bob (书店老板)', 
            'charlie': 'Charlie (上班族)'
        }
        return names.get(agent_id, agent_id.title())
    
    def _get_area_display_name(self, area: str) -> str:
        """获取区域显示名称"""
        area_names = {
            'coffee_shop': '咖啡店',
            'bookstore': '书店',
            'office_1': '办公室1',
            'office_2': '办公室2',
            'house_1': '住宅1',
            'house_2': '住宅2', 
            'house_3': '住宅3',
            'park': '公园',
            'market': '市场',
            'restaurant': '餐厅'
        }
        return area_names.get(area, area.replace('_', ' ').title())
    
    def _format_unknown_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化未知事件类型"""
        return {
            'type': 'unknown',
            'icon': '❓',
            'typeLabel': '未知事件',
            'description': event_data.get('description', '发生了某个事件'),
            'participants': self._format_participants(event_data.get('participants', [])),
            'color': '#6c757d',
            'category': 'unknown',
            'tags': ['unknown']
        }
    
    def get_all_event_types_for_frontend(self) -> Dict[str, Any]:
        """获取所有事件类型的前端显示信息"""
        result = {}
        
        for event_id, metadata in self.registry.get_all_events().items():
            result[event_id] = {
                'icon': metadata.icon,
                'displayName': metadata.display_names.get(self.language, event_id),
                'color': metadata.color,
                'category': metadata.category.value,
                'tags': metadata.tags
            }
        
        return result


# 全局事件格式化器实例
event_formatter = EventFormatter()

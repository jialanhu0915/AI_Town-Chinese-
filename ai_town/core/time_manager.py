"""
游戏时间管理器
管理 AI Town 中的时间流逝和调度
"""

from datetime import datetime, timedelta
from typing import Optional
import asyncio


class GameTime:
    """
    游戏时间管理器
    
    支持加速时间流逝，便于快速模拟长期行为
    """
    
    _start_time: Optional[datetime] = None
    _time_multiplier: float = 1.0  # 时间加速倍数
    _paused: bool = False
    
    @classmethod
    def initialize(cls, start_time: Optional[datetime] = None, time_multiplier: float = 1.0):
        """
        初始化游戏时间
        
        Args:
            start_time: 游戏开始时间，默认为当前时间
            time_multiplier: 时间加速倍数，1.0为正常速度
        """
        cls._start_time = start_time or datetime.now()
        cls._time_multiplier = time_multiplier
        cls._paused = False
    
    @classmethod
    def now(cls) -> datetime:
        """获取当前游戏时间"""
        if cls._start_time is None:
            cls.initialize()
        
        if cls._paused:
            return cls._start_time
        
        real_elapsed = datetime.now() - cls._start_time
        game_elapsed = timedelta(seconds=real_elapsed.total_seconds() * cls._time_multiplier)
        return cls._start_time + game_elapsed
    
    @classmethod
    def set_multiplier(cls, multiplier: float):
        """设置时间加速倍数"""
        current_time = cls.now()
        cls._start_time = current_time
        cls._time_multiplier = multiplier
    
    @classmethod
    def pause(cls):
        """暂停时间"""
        cls._paused = True
    
    @classmethod
    def resume(cls):
        """恢复时间"""
        if cls._paused:
            cls._start_time = datetime.now()
            cls._paused = False
    
    @classmethod
    def get_time_of_day(cls) -> str:
        """获取一天中的时间段"""
        current_time = cls.now()
        hour = current_time.hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    @classmethod
    def get_day_of_week(cls) -> str:
        """获取星期几"""
        current_time = cls.now()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[current_time.weekday()]
    
    @classmethod
    def minutes_since(cls, past_time: datetime) -> float:
        """计算从过去某个时间到现在的分钟数"""
        return (cls.now() - past_time).total_seconds() / 60
    
    @classmethod
    def hours_since(cls, past_time: datetime) -> float:
        """计算从过去某个时间到现在的小时数"""
        return cls.minutes_since(past_time) / 60
    
    @classmethod
    def format_time(cls, dt: Optional[datetime] = None) -> str:
        """格式化时间显示"""
        time_to_format = dt or cls.now()
        return time_to_format.strftime("%Y-%m-%d %H:%M:%S")


class TimeScheduler:
    """
    时间调度器
    
    用于安排定时任务和事件
    """
    
    def __init__(self):
        self.scheduled_events = []
        self.running = False
    
    def schedule_event(self, event_time: datetime, callback, *args, **kwargs):
        """安排一个定时事件"""
        self.scheduled_events.append({
            'time': event_time,
            'callback': callback,
            'args': args,
            'kwargs': kwargs
        })
        
        # 按时间排序
        self.scheduled_events.sort(key=lambda x: x['time'])
    
    async def start(self):
        """开始运行调度器"""
        self.running = True
        
        while self.running:
            current_time = GameTime.now()
            
            # 执行到期的事件
            while (self.scheduled_events and 
                   self.scheduled_events[0]['time'] <= current_time):
                
                event = self.scheduled_events.pop(0)
                try:
                    if asyncio.iscoroutinefunction(event['callback']):
                        await event['callback'](*event['args'], **event['kwargs'])
                    else:
                        event['callback'](*event['args'], **event['kwargs'])
                except Exception as e:
                    print(f"Error executing scheduled event: {e}")
            
            # 等待一小段时间再检查
            await asyncio.sleep(0.1)
    
    def stop(self):
        """停止调度器"""
        self.running = False
    
    def clear_events(self):
        """清除所有待执行事件"""
        self.scheduled_events.clear()

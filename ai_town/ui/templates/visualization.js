class AITownVisualizer {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.ws = null;
        this.isRunning = false;
        this.selectedAgent = null;
        this.worldState = null;
        
        // 颜色配置
        this.colors = {
            background: '#e8f5e8',
            grid: '#d0d0d0',
            buildings: {
                coffee_shop: '#4CAF50',
                bookstore: '#2196F3', 
                office_1: '#FF9800',
                office_2: '#FF9800',
                house_1: '#E91E63',
                house_2: '#E91E63',
                house_3: '#E91E63',
                park: '#8BC34A',
                market: '#9C27B0',
                restaurant: '#F44336'
            },
            agents: {
                alice: '#FF6B6B',
                bob: '#4ECDC4',
                charlie: '#45B7D1'
            }
        };
        
        this.initEventListeners();
        this.setupCanvas();
        this.connectWebSocket();
    }
    
    initEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.startSimulation());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pauseSimulation());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetSimulation());
        
        // 画布点击事件
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        
        // 窗口大小调整
        window.addEventListener('resize', () => this.setupCanvas());
    }
    
    setupCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // 设置画布大小
        this.canvas.width = rect.width - 40;
        this.canvas.height = rect.height - 40;
        
        // 计算缩放比例
        this.scaleX = this.canvas.width / 100;  // 假设世界是100x100
        this.scaleY = this.canvas.height / 100;
        
        this.redraw();
    }
    
    connectWebSocket() {
        try {
            this.ws = new WebSocket('ws://localhost:8000/ws');
            
            this.ws.onopen = () => {
                console.log('WebSocket 连接成功');
                this.updateConnectionStatus(true);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket 连接关闭');
                this.updateConnectionStatus(false);
                // 5秒后重连
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket 错误:', error);
                this.updateConnectionStatus(false);
            };
        } catch (error) {
            console.error('WebSocket 连接失败:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'world_state':
                this.worldState = data.data;
                this.updateUI();
                this.redraw();
                break;
            case 'simulation_started':
                this.isRunning = true;
                this.updateControlButtons();
                break;
            case 'simulation_paused':
                this.isRunning = false;
                this.updateControlButtons();
                break;
            case 'simulation_reset':
                this.worldState = null;
                this.selectedAgent = null;
                this.updateUI();
                this.redraw();
                break;
        }
    }
    
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connectionStatus');
        if (connected) {
            statusEl.className = 'connection-status connected';
            statusEl.textContent = '● 已连接';
        } else {
            statusEl.className = 'connection-status disconnected';
            statusEl.textContent = '● 未连接';
        }
    }
    
    sendWebSocketMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    
    startSimulation() {
        this.sendWebSocketMessage({ type: 'start_simulation' });
    }
    
    pauseSimulation() {
        this.sendWebSocketMessage({ type: 'pause_simulation' });
    }
    
    resetSimulation() {
        this.sendWebSocketMessage({ type: 'reset_simulation' });
    }
    
    updateControlButtons() {
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (this.isRunning) {
            startBtn.classList.remove('active');
            pauseBtn.classList.add('active');
        } else {
            startBtn.classList.add('active');
            pauseBtn.classList.remove('active');
        }
    }
    
    updateUI() {
        if (!this.worldState) return;
        
        // 更新时间
        const gameTimeEl = document.getElementById('gameTime');
        const timeOfDayEl = document.getElementById('timeOfDay');
        
        if (this.worldState.current_time) {
            gameTimeEl.textContent = this.worldState.current_time;
            timeOfDayEl.textContent = this.getTimeOfDayText(this.worldState.time_of_day);
        }
        
        // 更新统计数据
        document.getElementById('stepCount').textContent = this.worldState.step_count || 0;
        document.getElementById('agentCount').textContent = Object.keys(this.worldState.agent_positions || {}).length;
        document.getElementById('interactionCount').textContent = this.worldState.total_interactions || 0;
        document.getElementById('movementCount').textContent = this.worldState.total_movements || 0;
        
        // 更新智能体列表
        this.updateAgentList();
        
        // 更新事件列表
        this.updateEventsList();
    }
    
    getTimeOfDayText(timeOfDay) {
        const timeTexts = {
            morning: '🌅 早晨',
            afternoon: '☀️ 下午',
            evening: '🌆 傍晚',
            night: '🌙 夜晚'
        };
        return timeTexts[timeOfDay] || timeOfDay;
    }
    
    updateAgentList() {
        const agentListEl = document.getElementById('agentList');
        
        if (!this.worldState || !this.worldState.agent_positions) {
            agentListEl.innerHTML = '<div class="loading">暂无智能体数据</div>';
            return;
        }
        
        const agents = this.worldState.agent_positions;
        let html = '';
        
        for (const [agentId, position] of Object.entries(agents)) {
            const isSelected = this.selectedAgent === agentId;
            const statusClass = this.getAgentStatusClass(agentId);
            
            html += `
                <div class="agent-card ${isSelected ? 'selected' : ''}" 
                     onclick="visualizer.selectAgent('${agentId}')">
                    <div class="agent-name">
                        <span class="status-indicator ${statusClass}"></span>
                        ${this.getAgentDisplayName(agentId)}
                    </div>
                    <div class="agent-status">
                        位置: (${Math.round(position.x)}, ${Math.round(position.y)})
                        <br>区域: ${this.getAreaDisplayName(position.area)}
                    </div>
                </div>
            `;
        }
        
        agentListEl.innerHTML = html;
    }
    
    getAgentDisplayName(agentId) {
        const names = {
            alice: 'Alice (咖啡店老板)',
            bob: 'Bob (书店老板)',
            charlie: 'Charlie (上班族)'
        };
        return names[agentId] || agentId;
    }
    
    getAreaDisplayName(area) {
        const areaNames = {
            coffee_shop: '咖啡店',
            bookstore: '书店',
            office_1: '办公室1',
            office_2: '办公室2',
            house_1: '住宅1',
            house_2: '住宅2',
            house_3: '住宅3',
            park: '公园',
            market: '市场',
            restaurant: '餐厅'
        };
        return areaNames[area] || area;
    }
    
    getAgentStatusClass(agentId) {
        // 这里可以根据智能体的实际状态返回不同的样式
        return 'status-active';  // 默认为活跃状态
    }
    
    updateEventsList() {
        const eventsListEl = document.getElementById('eventsList');
        
        if (!this.worldState || !this.worldState.events) {
            eventsListEl.innerHTML = '<div class="loading">暂无事件数据</div>';
            return;
        }
        
        const events = this.worldState.events.slice(-10);  // 显示最近10个事件
        let html = '';
        
        events.reverse().forEach(event => {
            html += `
                <div class="event-item">
                    <div class="event-time">${this.formatEventTime(event.timestamp)}</div>
                    <div>${this.translateEventDescription(event.description)}</div>
                </div>
            `;
        });
        
        eventsListEl.innerHTML = html || '<div>暂无事件</div>';
    }
    
    formatEventTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('zh-CN');
    }
    
    translateEventDescription(description) {
        // 简单的事件描述翻译
        return description
            .replace(/moved from/g, '从')
            .replace(/to/g, '移动到')
            .replace(/started conversation with/g, '开始与')
            .replace(/conversation/g, '对话')
            .replace(/coffee_shop/g, '咖啡店')
            .replace(/bookstore/g, '书店')
            .replace(/office/g, '办公室')
            .replace(/house/g, '住宅')
            .replace(/park/g, '公园');
    }
    
    selectAgent(agentId) {
        this.selectedAgent = this.selectedAgent === agentId ? null : agentId;
        this.updateAgentList();
        this.redraw();
    }
    
    handleCanvasClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left) / this.scaleX;
        const y = (event.clientY - rect.top) / this.scaleY;
        
        console.log(`点击位置: (${Math.round(x)}, ${Math.round(y)})`);
        
        // 检查是否点击了智能体
        if (this.worldState && this.worldState.agent_positions) {
            for (const [agentId, position] of Object.entries(this.worldState.agent_positions)) {
                const distance = Math.sqrt(
                    Math.pow(x - position.x, 2) + Math.pow(y - position.y, 2)
                );
                
                if (distance < 3) {  // 3个单位范围内
                    this.selectAgent(agentId);
                    return;
                }
            }
        }
        
        // 如果没有点击智能体，取消选择
        this.selectedAgent = null;
        this.updateAgentList();
        this.redraw();
    }
    
    redraw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制背景
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制网格
        this.drawGrid();
        
        // 绘制建筑物
        this.drawBuildings();
        
        // 绘制智能体
        this.drawAgents();
        
        // 绘制选中智能体的路径或信息
        if (this.selectedAgent) {
            this.drawSelectedAgentInfo();
        }
    }
    
    drawGrid() {
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 0.5;
        
        // 垂直线
        for (let x = 0; x <= 100; x += 10) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.scaleX, 0);
            this.ctx.lineTo(x * this.scaleX, this.canvas.height);
            this.ctx.stroke();
        }
        
        // 水平线
        for (let y = 0; y <= 100; y += 10) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.scaleY);
            this.ctx.lineTo(this.canvas.width, y * this.scaleY);
            this.ctx.stroke();
        }
    }
    
    drawBuildings() {
        if (!this.worldState || !this.worldState.map_data || !this.worldState.map_data.buildings) {
            return;
        }
        
        this.worldState.map_data.buildings.forEach(building => {
            const color = this.colors.buildings[building.id] || '#888888';
            
            this.ctx.fillStyle = color;
            this.ctx.fillRect(
                building.x * this.scaleX,
                building.y * this.scaleY,
                building.width * this.scaleX,
                building.height * this.scaleY
            );
            
            // 绘制建筑物名称
            this.ctx.fillStyle = 'white';
            this.ctx.font = '12px Microsoft YaHei';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                this.getAreaDisplayName(building.id),
                (building.x + building.width / 2) * this.scaleX,
                (building.y + building.height / 2) * this.scaleY + 4
            );
        });
    }
    
    drawAgents() {
        if (!this.worldState || !this.worldState.agent_positions) {
            return;
        }
        
        for (const [agentId, position] of Object.entries(this.worldState.agent_positions)) {
            const color = this.colors.agents[agentId] || '#333333';
            const isSelected = this.selectedAgent === agentId;
            
            const x = position.x * this.scaleX;
            const y = position.y * this.scaleY;
            const radius = isSelected ? 8 : 6;
            
            // 绘制智能体圆圈
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fillStyle = color;
            this.ctx.fill();
            
            // 选中智能体的边框
            if (isSelected) {
                this.ctx.strokeStyle = '#FFD700';
                this.ctx.lineWidth = 3;
                this.ctx.stroke();
            }
            
            // 绘制智能体名称
            this.ctx.fillStyle = '#333';
            this.ctx.font = 'bold 11px Microsoft YaHei';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                agentId.charAt(0).toUpperCase() + agentId.slice(1),
                x,
                y - radius - 5
            );
        }
    }
    
    drawSelectedAgentInfo() {
        if (!this.selectedAgent || !this.worldState.agent_positions) return;
        
        const position = this.worldState.agent_positions[this.selectedAgent];
        if (!position) return;
        
        const x = position.x * this.scaleX;
        const y = position.y * this.scaleY;
        
        // 绘制信息面板
        const panelWidth = 200;
        const panelHeight = 80;
        const panelX = Math.min(x + 20, this.canvas.width - panelWidth);
        const panelY = Math.max(y - panelHeight, 10);
        
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(panelX, panelY, panelWidth, panelHeight);
        
        this.ctx.fillStyle = 'white';
        this.ctx.font = '14px Microsoft YaHei';
        this.ctx.textAlign = 'left';
        
        const lines = [
            `${this.getAgentDisplayName(this.selectedAgent)}`,
            `位置: (${Math.round(position.x)}, ${Math.round(position.y)})`,
            `区域: ${this.getAreaDisplayName(position.area)}`
        ];
        
        lines.forEach((line, index) => {
            this.ctx.fillText(line, panelX + 10, panelY + 20 + index * 18);
        });
    }
}

// 初始化可视化器
let visualizer;
document.addEventListener('DOMContentLoaded', () => {
    visualizer = new AITownVisualizer();
});

// 全局函数供HTML调用
function selectAgent(agentId) {
    if (visualizer) {
        visualizer.selectAgent(agentId);
    }
}

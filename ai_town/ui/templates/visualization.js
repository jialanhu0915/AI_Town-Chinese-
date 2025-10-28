class AITownVisualizer {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.ws = null;
        this.isRunning = false;
        this.selectedAgent = null;
        this.worldState = null;
        
        // 动画相关
        this.animationFrame = null;
        this.agentPositions = {}; // 当前显示位置（用于动画）
        this.targetPositions = {}; // 目标位置
        this.animationSpeed = 50; // 动画速度（像素每秒）
        this.lastUpdateTime = Date.now();
        this.needsRedraw = true; // 优化：仅在需要时重绘
        
        // 位置历史追踪
        this.positionHistory = {}; // 每个智能体的位置历史
        this.maxHistoryLength = 15; // 最大历史记录数
        this.trailFadeTime = 3000; // 轨迹淡出时间（毫秒）
        this.showTrails = true; // 是否显示轨迹
        
        // 颜色配置
        this.colors = {
            background: '#f0f8ff',
            grid: '#e0e0e0',
            gridMajor: '#c0c0c0',
            buildings: {
                coffee_shop: '#8B4513',
                bookstore: '#4169E1', 
                office_1: '#FF8C00',
                office_2: '#FF8C00',
                house_1: '#DC143C',
                house_2: '#DC143C',
                house_3: '#DC143C',
                park: '#228B22',
                market: '#9370DB',
                restaurant: '#FF4500'
            },
            agents: {
                alice: '#FF1493',
                bob: '#00CED1',
                charlie: '#FFD700'
            },
            trail: {
                alice: 'rgba(255, 20, 147, 0.3)',
                bob: 'rgba(0, 206, 209, 0.3)',
                charlie: 'rgba(255, 215, 0, 0.3)'
            }
        };
        
        this.initEventListeners();
        this.setupCanvas();
        this.connectWebSocket();
        this.startAnimationLoop();
    }
    
    initEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.startSimulation());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pauseSimulation());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetSimulation());
        
        // 动画控制
        const speedSlider = document.getElementById('animationSpeed');
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => {
                this.animationSpeed = parseInt(e.target.value);
                this.needsRedraw = true;
            });
        }
        
        const trailsCheckbox = document.getElementById('showTrails');
        if (trailsCheckbox) {
            trailsCheckbox.addEventListener('change', (e) => {
                this.showTrails = e.target.checked;
                this.needsRedraw = true;
            });
        }
        
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
                console.log('Received world state:', this.worldState);
                
                // 调试建筑物数据
                if (this.worldState.map_data && this.worldState.map_data.buildings) {
                    console.log('Buildings data type:', typeof this.worldState.map_data.buildings);
                    console.log('Buildings data:', this.worldState.map_data.buildings);
                }
                
                this.updateUI();
                // 不要在这里调用redraw()，让动画循环来处理
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
                this.agentPositions = {};
                this.targetPositions = {};
                this.positionHistory = {};
                this.updateUI();
                this.needsRedraw = true;
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
        
        const events = this.worldState.events.slice(-15);  // 显示最近15个事件
        let html = '';
        
        events.reverse().forEach(event => {
            const eventDisplay = this.formatEventDisplay(event);
            html += `
                <div class="event-item ${eventDisplay.type}">
                    <div class="event-header">
                        <span class="event-icon">${eventDisplay.icon}</span>
                        <span class="event-time">${this.formatEventTime(event.timestamp)}</span>
                        <span class="event-type">${eventDisplay.typeLabel}</span>
                    </div>
                    <div class="event-description">${eventDisplay.description}</div>
                    ${eventDisplay.participants ? `<div class="event-participants">参与者: ${eventDisplay.participants}</div>` : ''}
                    ${event.duration ? `<div class="event-duration">持续: ${this.formatDuration(event.duration)}</div>` : ''}
                </div>
            `;
        });
        
        eventsListEl.innerHTML = html || '<div>暂无事件</div>';
    }
    
    formatEventTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    }
    
    formatDuration(duration) {
        if (!duration) return '';
        if (duration < 60) {
            return `${Math.round(duration)}秒`;
        } else if (duration < 3600) {
            return `${Math.round(duration / 60)}分钟`;
        } else {
            return `${Math.round(duration / 3600)}小时`;
        }
    }
    
    formatEventDisplay(event) {
        const eventType = event.event_type || 'unknown';
        let icon = '📝';
        let typeLabel = '事件';
        let description = event.description || '';
        let participants = '';
        
        // 格式化参与者
        if (event.participants && Array.isArray(event.participants)) {
            participants = event.participants.map(p => this.getAgentDisplayName(p)).join(', ');
        }
        
        // 根据事件类型设置图标和标签
        switch (eventType) {
            case 'movement':
                icon = '🚶';
                typeLabel = '移动';
                description = this.formatMovementEvent(event);
                break;
            case 'conversation':
                icon = '💬';
                typeLabel = '对话';
                description = this.formatConversationEvent(event);
                break;
            case 'interaction':
                icon = '🤝';
                typeLabel = '互动';
                description = this.formatInteractionEvent(event);
                break;
            case 'planning':
                icon = '🤔';
                typeLabel = '规划';
                description = this.formatPlanningEvent(event);
                break;
            case 'reflection':
                icon = '💭';
                typeLabel = '思考';
                description = this.formatReflectionEvent(event);
                break;
            case 'work':
                icon = '💼';
                typeLabel = '工作';
                description = this.formatWorkEvent(event);
                break;
            case 'social':
            case 'socialize':
                icon = '👥';
                typeLabel = '社交';
                description = this.formatSocialEvent(event);
                break;
            // Alice 相关行为
            case 'customer_greeting':
                icon = '👋';
                typeLabel = '迎客';
                description = this.formatCustomerServiceEvent(event);
                break;
            case 'coffee_making':
                icon = '☕';
                typeLabel = '制作咖啡';
                description = this.formatCoffeeEvent(event);
                break;
            case 'friendly_chat':
                icon = '😊';
                typeLabel = '闲聊';
                description = this.formatFriendlyChatEvent(event);
                break;
            case 'drink_recommendation':
                icon = '🥤';
                typeLabel = '推荐饮品';
                description = this.formatRecommendationEvent(event);
                break;
            case 'shop_maintenance':
                icon = '🧹';
                typeLabel = '店铺维护';
                description = this.formatMaintenanceEvent(event);
                break;
            // Bob 相关行为
            case 'organizing_books':
                icon = '📚';
                typeLabel = '整理书籍';
                description = this.formatBookOrganizingEvent(event);
                break;
            case 'customer_service':
                icon = '🤝';
                typeLabel = '客户服务';
                description = this.formatCustomerServiceEvent(event);
                break;
            case 'researching':
                icon = '🔍';
                typeLabel = '研究';
                description = this.formatResearchEvent(event);
                break;
            case 'book_recommendation':
                icon = '📖';
                typeLabel = '推荐书籍';
                description = this.formatBookRecommendationEvent(event);
                break;
            case 'reading':
                icon = '📘';
                typeLabel = '阅读';
                description = this.formatReadingEvent(event);
                break;
            case 'creating':
                icon = '✍️';
                typeLabel = '创作';
                description = this.formatCreatingEvent(event);
                break;
            // Charlie 相关行为
            case 'networking':
                icon = '🤝';
                typeLabel = '建立人脉';
                description = this.formatNetworkingEvent(event);
                break;
            case 'meeting_attendance':
                icon = '👔';
                typeLabel = '参加会议';
                description = this.formatMeetingEvent(event);
                break;
            case 'lunch_break':
                icon = '🍽️';
                typeLabel = '午休';
                description = this.formatLunchBreakEvent(event);
                break;
            case 'exercising':
                icon = '💪';
                typeLabel = '锻炼';
                description = this.formatExerciseEvent(event);
                break;
            case 'skill_learning':
                icon = '📚';
                typeLabel = '学习技能';
                description = this.formatSkillLearningEvent(event);
                break;
            case 'town_exploration':
                icon = '🗺️';
                typeLabel = '探索小镇';
                description = this.formatTownExplorationEvent(event);
                break;
            default:
                description = this.translateEventDescription(event.description || '');
                break;
        }
        
        return {
            type: eventType,
            icon,
            typeLabel,
            description,
            participants
        };
    }
    
    formatMovementEvent(event) {
        const desc = event.description || '';
        let formatted = desc;
        
        // 匹配移动模式: "X moved from A to B"
        const moveMatch = desc.match(/(\w+)\s+moved from\s+(\w+)\s+to\s+(\w+)/i);
        if (moveMatch) {
            const [, agent, from, to] = moveMatch;
            const agentName = this.getAgentDisplayName(agent);
            const fromArea = this.getAreaDisplayName(from);
            const toArea = this.getAreaDisplayName(to);
            formatted = `${agentName} 从${fromArea}移动到${toArea}`;
        } else {
            formatted = this.translateEventDescription(desc);
        }
        
        return formatted;
    }
    
    formatConversationEvent(event) {
        const desc = event.description || '';
        let formatted = desc;
        
        // 匹配对话模式: "X started conversation with Y"
        const convMatch = desc.match(/(\w+)\s+started conversation with\s+(\w+)/i);
        if (convMatch) {
            const [, agent1, agent2] = convMatch;
            const name1 = this.getAgentDisplayName(agent1);
            const name2 = this.getAgentDisplayName(agent2);
            formatted = `${name1} 与 ${name2} 开始对话`;
        } else {
            formatted = this.translateEventDescription(desc);
        }
        
        return formatted;
    }
    
    formatInteractionEvent(event) {
        const desc = event.description || '';
        return this.translateEventDescription(desc)
            .replace(/interaction/gi, '互动')
            .replace(/with/gi, '与');
    }
    
    formatPlanningEvent(event) {
        const desc = event.description || '';
        return this.translateEventDescription(desc)
            .replace(/planning/gi, '正在规划')
            .replace(/decided to/gi, '决定')
            .replace(/thinking about/gi, '正在思考');
    }
    
    formatReflectionEvent(event) {
        const desc = event.description || '';
        return this.translateEventDescription(desc)
            .replace(/reflection/gi, '反思')
            .replace(/realized/gi, '意识到')
            .replace(/learned/gi, '学到了');
    }
    
    formatWorkEvent(event) {
        const desc = event.description || '';
        return this.translateEventDescription(desc)
            .replace(/working/gi, '正在工作')
            .replace(/serving/gi, '正在服务')
            .replace(/managing/gi, '正在管理');
    }
    
    formatSocialEvent(event) {
        const desc = event.description || '';
        return this.translateEventDescription(desc)
            .replace(/socializing/gi, '社交')
            .replace(/meeting/gi, '会面')
            .replace(/greeting/gi, '问候');
    }
    
    formatCustomerServiceEvent(event) {
        const desc = event.description || '';
        const agentName = this.getAgentDisplayName(event.participants?.[0] || 'agent');
        return `${agentName} 正在为顾客提供服务`;
    }
    
    formatCoffeeEvent(event) {
        const desc = event.description || '';
        const coffeeType = event.coffee_type || '咖啡';
        return `Alice 正在制作 ${coffeeType}`;
    }
    
    formatFriendlyChatEvent(event) {
        const desc = event.description || '';
        return `Alice 正在与常客友好聊天`;
    }
    
    formatRecommendationEvent(event) {
        const desc = event.description || '';
        return `Alice 正在为顾客推荐饮品`;
    }
    
    formatMaintenanceEvent(event) {
        const desc = event.description || '';
        return `Alice 正在清洁和维护咖啡店`;
    }
    
    formatBookOrganizingEvent(event) {
        const desc = event.description || '';
        return `Bob 正在整理书架上的书籍`;
    }
    
    formatResearchEvent(event) {
        const desc = event.description || '';
        const topic = event.topic || '文学';
        return `Bob 正在研究 ${topic} 相关内容`;
    }
    
    formatBookRecommendationEvent(event) {
        const desc = event.description || '';
        return `Bob 正在为顾客推荐合适的书籍`;
    }
    
    formatReadingEvent(event) {
        const desc = event.description || '';
        const material = event.material || '书籍';
        return `Bob 正在阅读 ${material}`;
    }
    
    formatCreatingEvent(event) {
        const desc = event.description || '';
        const creationType = event.creation_type || '内容';
        return `正在创作 ${creationType}`;
    }
    
    formatNetworkingEvent(event) {
        const desc = event.description || '';
        return `Charlie 正在建立职业人脉关系`;
    }
    
    formatMeetingEvent(event) {
        const desc = event.description || '';
        const meetingType = event.meeting_type || '团队会议';
        return `Charlie 正在参加 ${meetingType}`;
    }
    
    formatLunchBreakEvent(event) {
        const desc = event.description || '';
        return `Charlie 正在享受午休时光`;
    }
    
    formatExerciseEvent(event) {
        const desc = event.description || '';
        const exerciseType = event.exercise_type || '运动';
        return `Charlie 正在进行 ${exerciseType} 锻炼`;
    }
    
    formatSkillLearningEvent(event) {
        const desc = event.description || '';
        const skill = event.skill || '职业技能';
        return `Charlie 正在学习 ${skill}`;
    }
    
    formatTownExplorationEvent(event) {
        const desc = event.description || '';
        return `Charlie 正在探索小镇的新地方`;
    }
    
    translateEventDescription(description) {
        if (!description) return '';
        
        // 基础翻译映射
        const translations = {
            // 动作
            'moved from': '从',
            'to': '到',
            'started conversation with': '开始与',
            'ended conversation with': '结束与',
            'conversation': '的对话',
            'is working at': '正在',
            'is planning': '正在规划',
            'decided to': '决定',
            'thinking about': '正在思考',
            'reflecting on': '正在反思',
            
            // 地点
            'coffee_shop': '咖啡店',
            'bookstore': '书店',
            'office_1': '办公室1',
            'office_2': '办公室2', 
            'house_1': '住宅1',
            'house_2': '住宅2',
            'house_3': '住宅3',
            'park': '公园',
            'market': '市场',
            'restaurant': '餐厅',
            
            // 角色
            'alice': 'Alice',
            'bob': 'Bob', 
            'charlie': 'Charlie'
        };
        
        let result = description;
        
        // 应用翻译
        for (const [english, chinese] of Object.entries(translations)) {
            const regex = new RegExp(english, 'gi');
            result = result.replace(regex, chinese);
        }
        
        return result;
    }
    
    selectAgent(agentId) {
        this.selectedAgent = this.selectedAgent === agentId ? null : agentId;
        this.updateAgentList();
        this.needsRedraw = true;
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
        this.needsRedraw = true;
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
        // 细网格
        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 0.3;
        
        for (let x = 0; x <= 100; x += 5) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.scaleX, 0);
            this.ctx.lineTo(x * this.scaleX, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let y = 0; y <= 100; y += 5) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.scaleY);
            this.ctx.lineTo(this.canvas.width, y * this.scaleY);
            this.ctx.stroke();
        }
        
        // 粗网格
        this.ctx.strokeStyle = this.colors.gridMajor;
        this.ctx.lineWidth = 1;
        
        for (let x = 0; x <= 100; x += 20) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.scaleX, 0);
            this.ctx.lineTo(x * this.scaleX, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let y = 0; y <= 100; y += 20) {
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
        
        // 确保 buildings 是数组
        const buildings = Array.isArray(this.worldState.map_data.buildings) 
            ? this.worldState.map_data.buildings 
            : Object.values(this.worldState.map_data.buildings);
        
        buildings.forEach(building => {
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
        
        // 首先绘制轨迹（如果启用）
        if (this.showTrails) {
            this.drawAgentTrails();
        }
        
        // 然后绘制智能体
        for (const [agentId, targetPos] of Object.entries(this.worldState.agent_positions)) {
            // 更新目标位置
            this.targetPositions[agentId] = { x: targetPos.x, y: targetPos.y, area: targetPos.area };
            
            // 如果是第一次，直接设置当前位置
            if (!this.agentPositions[agentId]) {
                this.agentPositions[agentId] = { x: targetPos.x, y: targetPos.y, area: targetPos.area };
            }
            
            // 使用当前动画位置绘制
            const currentPos = this.agentPositions[agentId];
            const color = this.colors.agents[agentId] || '#333333';
            const isSelected = this.selectedAgent === agentId;
            
            const x = currentPos.x * this.scaleX;
            const y = currentPos.y * this.scaleY;
            const baseRadius = 8;
            const radius = isSelected ? baseRadius + 2 : baseRadius;
            
            // 绘制阴影
            this.ctx.beginPath();
            this.ctx.arc(x + 2, y + 2, radius, 0, 2 * Math.PI);
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            this.ctx.fill();
            
            // 绘制智能体主体
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fillStyle = color;
            this.ctx.fill();
            
            // 绘制边框
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.strokeStyle = isSelected ? '#FFD700' : '#FFFFFF';
            this.ctx.lineWidth = isSelected ? 3 : 2;
            this.ctx.stroke();
            
            // 绘制方向指示器和移动效果
            const dx = targetPos.x - currentPos.x;
            const dy = targetPos.y - currentPos.y;
            const isMoving = Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1;
            
            if (isMoving) {
                const angle = Math.atan2(dy, dx);
                
                // 绘制移动方向箭头
                const arrowLength = radius + 8;
                const arrowX = x + Math.cos(angle) * arrowLength;
                const arrowY = y + Math.sin(angle) * arrowLength;
                
                // 箭头主线
                this.ctx.beginPath();
                this.ctx.moveTo(x, y);
                this.ctx.lineTo(arrowX, arrowY);
                this.ctx.strokeStyle = color;
                this.ctx.lineWidth = 3;
                this.ctx.stroke();
                
                // 箭头头部
                const arrowHeadLength = 6;
                const arrowHeadAngle = Math.PI / 6;
                
                this.ctx.beginPath();
                this.ctx.moveTo(arrowX, arrowY);
                this.ctx.lineTo(
                    arrowX - arrowHeadLength * Math.cos(angle - arrowHeadAngle),
                    arrowY - arrowHeadLength * Math.sin(angle - arrowHeadAngle)
                );
                this.ctx.moveTo(arrowX, arrowY);
                this.ctx.lineTo(
                    arrowX - arrowHeadLength * Math.cos(angle + arrowHeadAngle),
                    arrowY - arrowHeadLength * Math.sin(angle + arrowHeadAngle)
                );
                this.ctx.stroke();
                
                // 添加移动光环效果
                const time = Date.now() / 200;
                const pulseRadius = radius + 3 + Math.sin(time) * 2;
                this.ctx.beginPath();
                this.ctx.arc(x, y, pulseRadius, 0, 2 * Math.PI);
                this.ctx.strokeStyle = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, 0.3)`;
                this.ctx.lineWidth = 1;
                this.ctx.stroke();
            }
            
            // 绘制智能体名称和状态
            this.ctx.fillStyle = '#333';
            this.ctx.font = 'bold 12px Microsoft YaHei';
            this.ctx.textAlign = 'center';
            
            const name = agentId.charAt(0).toUpperCase() + agentId.slice(1);
            this.ctx.fillText(name, x, y - radius - 8);
            
            // 显示当前区域
            if (currentPos.area) {
                this.ctx.font = '10px Microsoft YaHei';
                this.ctx.fillStyle = '#666';
                this.ctx.fillText(
                    this.getAreaDisplayName(currentPos.area),
                    x, y + radius + 15
                );
            }
        }
    }
    
    drawAgentTrails() {
        if (!this.positionHistory) return;
        
        const now = Date.now();
        
        for (const [agentId, history] of Object.entries(this.positionHistory)) {
            if (history.length < 2) continue;
            
            const baseColor = this.colors.agents[agentId] || '#333333';
            
            // 绘制渐变轨迹
            for (let i = 1; i < history.length; i++) {
                const prevPos = history[i - 1];
                const currentPos = history[i];
                
                // 计算透明度（基于时间和位置）
                const age = now - currentPos.timestamp;
                const fadeRatio = Math.max(0, 1 - age / this.trailFadeTime);
                const positionRatio = i / history.length;
                const alpha = fadeRatio * positionRatio * 0.6;
                
                if (alpha > 0.05) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(prevPos.x * this.scaleX, prevPos.y * this.scaleY);
                    this.ctx.lineTo(currentPos.x * this.scaleX, currentPos.y * this.scaleY);
                    
                    // 根据透明度设置颜色
                    const r = parseInt(baseColor.substr(1, 2), 16);
                    const g = parseInt(baseColor.substr(3, 2), 16);
                    const b = parseInt(baseColor.substr(5, 2), 16);
                    this.ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
                    
                    // 线宽也随着时间变化
                    this.ctx.lineWidth = Math.max(1, 4 * positionRatio);
                    this.ctx.lineCap = 'round';
                    this.ctx.stroke();
                }
            }
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
    
    startAnimationLoop() {
        const animate = () => {
            this.updateAnimations();
            
            // 性能优化：仅在需要时重绘
            if (this.needsRedraw) {
                this.redraw();
                this.needsRedraw = false;
            }
            
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
    }
    
    updateAnimations() {
        const now = Date.now();
        const deltaTime = (now - this.lastUpdateTime) / 1000; // 转换为秒
        this.lastUpdateTime = now;
        
        let hasMovement = false;
        
        // 更新智能体位置动画
        for (const agentId in this.targetPositions) {
            if (!this.agentPositions[agentId]) {
                this.agentPositions[agentId] = { ...this.targetPositions[agentId] };
                this.needsRedraw = true;
                continue;
            }
            
            const current = this.agentPositions[agentId];
            const target = this.targetPositions[agentId];
            
            // 计算移动距离
            const dx = target.x - current.x;
            const dy = target.y - current.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance > 0.1) {
                // 平滑移动 - 使用更自然的速度
                const moveSpeed = Math.max(this.animationSpeed * deltaTime, distance * 0.08);
                const moveDistance = Math.min(distance, moveSpeed);
                const ratio = moveDistance / distance;
                
                current.x += dx * ratio;
                current.y += dy * ratio;
                
                // 更新位置历史
                this.updatePositionHistory(agentId, current.x, current.y);
                hasMovement = true;
                this.needsRedraw = true;
            } else if (Math.abs(current.x - target.x) > 0.01 || Math.abs(current.y - target.y) > 0.01) {
                // 足够接近，直接设置为目标位置
                current.x = target.x;
                current.y = target.y;
                current.area = target.area;
                this.needsRedraw = true;
            }
        }
        
        // 清理过期的轨迹点
        this.cleanupTrails(now);
        
        // 如果有世界状态更新但没有动画，也需要重绘
        if (this.worldState && !hasMovement) {
            this.needsRedraw = true;
        }
    }
    
    updatePositionHistory(agentId, x, y) {
        if (!this.positionHistory[agentId]) {
            this.positionHistory[agentId] = [];
        }
        
        const history = this.positionHistory[agentId];
        const lastPos = history[history.length - 1];
        
        // 只有当位置变化足够大时才记录
        if (!lastPos || Math.abs(lastPos.x - x) > 0.8 || Math.abs(lastPos.y - y) > 0.8) {
            history.push({ x, y, timestamp: Date.now() });
            
            // 限制历史长度
            if (history.length > this.maxHistoryLength) {
                history.shift();
            }
        }
    }
    
    cleanupTrails(now) {
        for (const agentId in this.positionHistory) {
            const history = this.positionHistory[agentId];
            // 移除过期的轨迹点
            while (history.length > 0 && now - history[0].timestamp > this.trailFadeTime) {
                history.shift();
                this.needsRedraw = true;
            }
        }
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

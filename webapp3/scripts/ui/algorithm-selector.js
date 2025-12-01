/**
 * 算法选择器
 * 提供直观的算法选择界面
 */

export class AlgorithmSelector {
    constructor() {
        this.algorithms = {
            line: [
                { id: 'bresenham', name: 'Bresenham', description: '整数运算，高效' },
                { id: 'dda', name: 'DDA', description: '增量计算' },
                { id: 'midpoint', name: '中点画线', description: '中点判别' },
                { id: 'canvas', name: 'Canvas API', description: '原生绘制' }
            ],
            circle: [
                { id: 'midpoint', name: '中点画圆', description: '八对称性' },
                { id: 'canvas', name: 'Canvas API', description: '原生绘制' }
            ],
            fill: [
                { id: 'scanline', name: '扫描线填充', description: '多边形填充' },
                { id: 'boundary', name: '边界填充', description: '种子填充' },
                { id: 'canvas', name: 'Canvas API', description: '原生填充' }
            ]
        };
        
        this.currentSelections = {
            line: 'bresenham',
            circle: 'midpoint',
            fill: 'scanline'
        };
        
        this.listeners = new Map();
        this.loadPreferences();
    }
    
    /**
     * 创建下拉选择器
     * @param {string} toolType - 工具类型 (line, circle, fill)
     * @param {string} containerId - 容器元素 ID
     */
    createSelector(toolType, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const select = document.createElement('select');
        select.className = 'algorithm-selector';
        select.id = `algorithm-${toolType}`;
        
        const algorithms = this.algorithms[toolType] || [];
        algorithms.forEach(algo => {
            const option = document.createElement('option');
            option.value = algo.id;
            option.textContent = `${algo.name} - ${algo.description}`;
            if (algo.id === this.currentSelections[toolType]) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        
        select.addEventListener('change', (e) => {
            this.setAlgorithm(toolType, e.target.value);
        });
        
        container.appendChild(select);
    }
    
    /**
     * 设置算法
     * @param {string} toolType - 工具类型
     * @param {string} algorithmId - 算法 ID
     */
    setAlgorithm(toolType, algorithmId) {
        this.currentSelections[toolType] = algorithmId;
        this.savePreferences();
        this.emit('algorithmChanged', { toolType, algorithmId });
    }
    
    /**
     * 获取当前算法
     * @param {string} toolType - 工具类型
     * @returns {string} 算法 ID
     */
    getAlgorithm(toolType) {
        return this.currentSelections[toolType];
    }
    
    /**
     * 保存用户偏好
     */
    savePreferences() {
        try {
            localStorage.setItem('algorithmPreferences', JSON.stringify(this.currentSelections));
        } catch (error) {
            console.error('Failed to save algorithm preferences:', error);
        }
    }
    
    /**
     * 加载用户偏好
     */
    loadPreferences() {
        try {
            const saved = localStorage.getItem('algorithmPreferences');
            if (saved) {
                this.currentSelections = { ...this.currentSelections, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.error('Failed to load algorithm preferences:', error);
        }
    }
    
    /**
     * 监听事件
     * @param {string} event - 事件名称
     * @param {Function} callback - 回调函数
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    /**
     * 触发事件
     * @param {string} event - 事件名称
     * @param {Object} data - 事件数据
     */
    emit(event, data) {
        if (!this.listeners.has(event)) return;
        
        const callbacks = this.listeners.get(event);
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Algorithm selector event error (${event}):`, error);
            }
        });
    }
}

export default AlgorithmSelector;

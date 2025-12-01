/**
 * Canvas 管理器
 * 负责 Canvas 的初始化、渲染和事件处理
 */

import CONFIG from '../config.js';

export class CanvasManager {
    constructor(canvasElement, config = {}) {
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext('2d');
        this.config = { ...CONFIG.CANVAS, ...config };
        
        this.shapes = [];
        this.currentTool = null;
        this.previewShape = null;
        this.selectionBox = null; // 选择框
        this.listeners = new Map();
        
        // 缩放和平移
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.minScale = 0.1;
        this.maxScale = 10.0;
        
        // 网格设置
        this.showGrid = false;
        this.gridSize = 20; // 网格大小（像素）
        this.gridColor = '#e0e0e0';
        this.gridLineWidth = 1;
        
        // 性能优化
        this.animationFrameId = null;
        this.needsRender = true;
        
        this.init();
    }

    init() {
        this.resize();
        this.setupEventListeners();
        this.startRenderLoop();
    }

    resize() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // 设置 Canvas 尺寸
        const width = Math.max(this.config.minWidth, Math.min(rect.width, this.config.maxWidth));
        const height = Math.max(this.config.minHeight, Math.min(rect.height || this.config.defaultHeight, this.config.maxHeight));
        
        // 设置实际像素尺寸（考虑设备像素比）
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = width * dpr;
        this.canvas.height = height * dpr;
        
        // 设置 CSS 尺寸
        this.canvas.style.width = width + 'px';
        this.canvas.style.height = height + 'px';
        
        // 缩放上下文以匹配设备像素比
        this.ctx.scale(dpr, dpr);
        
        this.needsRender = true;
    }

    setupEventListeners() {
        // 鼠标事件
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
        this.canvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
        
        // 滚轮缩放
        this.canvas.addEventListener('wheel', this.handleWheel.bind(this), { passive: false });
        
        // 触摸事件
        this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
        
        // 窗口调整大小
        window.addEventListener('resize', this.debounce(() => this.resize(), 300));
    }

    startRenderLoop() {
        const render = () => {
            if (this.needsRender) {
                this.render(this.shapes);
                this.needsRender = false;
            }
            this.animationFrameId = requestAnimationFrame(render);
        };
        render();
    }

    stopRenderLoop() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    render(shapes) {
        this.clear();
        
        // 保存上下文状态
        this.ctx.save();
        
        // 应用缩放和平移变换
        this.ctx.translate(this.offsetX, this.offsetY);
        this.ctx.scale(this.scale, this.scale);
        
        // 渲染网格（在图形之前）
        if (this.showGrid) {
            this.renderGrid();
        }
        
        // 渲染所有图形
        for (const shape of shapes) {
            this.renderShape(shape);
        }
        
        // 渲染预览图形
        if (this.previewShape) {
            this.renderShape(this.previewShape);
        }
        
        // 渲染选择框
        if (this.selectionBox) {
            this.renderSelectionBox(this.selectionBox);
        }
        
        // 恢复上下文状态
        this.ctx.restore();
    }
    
    renderSelectionBox(box) {
        const ctx = this.ctx;
        ctx.save();
        
        const x = Math.min(box.x1, box.x2);
        const y = Math.min(box.y1, box.y2);
        const width = Math.abs(box.x2 - box.x1);
        const height = Math.abs(box.y2 - box.y1);
        
        // 绘制半透明填充
        ctx.fillStyle = 'rgba(0, 123, 255, 0.1)';
        ctx.fillRect(x, y, width, height);
        
        // 绘制虚线边框
        ctx.strokeStyle = '#007bff';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(x, y, width, height);
        
        ctx.restore();
    }

    renderShape(shape) {
        if (!shape || typeof shape.render !== 'function') {
            console.warn('无效的图形对象:', shape);
            return;
        }
        
        try {
            shape.render(this.ctx);
        } catch (error) {
            console.error('渲染图形失败:', error, shape);
        }
    }

    clear() {
        const width = this.canvas.width / (window.devicePixelRatio || 1);
        const height = this.canvas.height / (window.devicePixelRatio || 1);
        this.ctx.clearRect(0, 0, width, height);
        
        // 绘制背景
        this.ctx.fillStyle = this.config.backgroundColor;
        this.ctx.fillRect(0, 0, width, height);
    }

    renderGrid() {
        if (!this.showGrid) return;
        
        const ctx = this.ctx;
        const width = this.canvas.width / (window.devicePixelRatio || 1);
        const height = this.canvas.height / (window.devicePixelRatio || 1);
        
        ctx.save();
        
        // 计算可见区域在世界坐标中的范围
        const startX = Math.floor((-this.offsetX / this.scale) / this.gridSize) * this.gridSize;
        const startY = Math.floor((-this.offsetY / this.scale) / this.gridSize) * this.gridSize;
        const endX = startX + Math.ceil(width / this.scale / this.gridSize) * this.gridSize + this.gridSize;
        const endY = startY + Math.ceil(height / this.scale / this.gridSize) * this.gridSize + this.gridSize;
        
        ctx.strokeStyle = this.gridColor;
        ctx.lineWidth = this.gridLineWidth / this.scale; // 线宽随缩放调整
        ctx.beginPath();
        
        // 绘制垂直线
        for (let x = startX; x <= endX; x += this.gridSize) {
            ctx.moveTo(x, startY);
            ctx.lineTo(x, endY);
        }
        
        // 绘制水平线
        for (let y = startY; y <= endY; y += this.gridSize) {
            ctx.moveTo(startX, y);
            ctx.lineTo(endX, y);
        }
        
        ctx.stroke();
        ctx.restore();
    }

    screenToCanvas(clientX, clientY) {
        const rect = this.canvas.getBoundingClientRect();
        const screenX = clientX - rect.left;
        const screenY = clientY - rect.top;
        
        // 转换到世界坐标（考虑缩放和平移）
        return {
            x: (screenX - this.offsetX) / this.scale,
            y: (screenY - this.offsetY) / this.scale
        };
    }

    canvasToScreen(x, y) {
        const rect = this.canvas.getBoundingClientRect();
        // 从世界坐标转换到屏幕坐标
        return {
            x: x * this.scale + this.offsetX + rect.left,
            y: y * this.scale + this.offsetY + rect.top
        };
    }

    handleMouseDown(e) {
        e.preventDefault();
        const pos = this.screenToCanvas(e.clientX, e.clientY);
        
        if (this.currentTool && typeof this.currentTool.onMouseDown === 'function') {
            this.currentTool.onMouseDown(pos.x, pos.y, e);
        }
        
        this.emit('mousedown', { x: pos.x, y: pos.y, event: e });
    }

    handleMouseMove(e) {
        const pos = this.screenToCanvas(e.clientX, e.clientY);
        
        if (this.currentTool && typeof this.currentTool.onMouseMove === 'function') {
            this.currentTool.onMouseMove(pos.x, pos.y, e);
        }
        
        this.emit('mousemove', { x: pos.x, y: pos.y, event: e });
    }

    handleMouseUp(e) {
        const pos = this.screenToCanvas(e.clientX, e.clientY);
        
        if (this.currentTool && typeof this.currentTool.onMouseUp === 'function') {
            this.currentTool.onMouseUp(pos.x, pos.y, e);
        }
        
        this.emit('mouseup', { x: pos.x, y: pos.y, event: e });
    }

    handleMouseLeave(e) {
        this.emit('mouseleave', { event: e });
    }

    handleDoubleClick(e) {
        e.preventDefault();
        const pos = this.screenToCanvas(e.clientX, e.clientY);
        
        if (this.currentTool && typeof this.currentTool.onDoubleClick === 'function') {
            this.currentTool.onDoubleClick(pos.x, pos.y, e);
        }
        
        this.emit('dblclick', { x: pos.x, y: pos.y, event: e });
    }

    handleWheel(e) {
        // 检测是否按住 Ctrl/Cmd 键
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const modifierKey = isMac ? e.metaKey : e.ctrlKey;
        
        // 只有按住 Ctrl/Cmd 时才缩放
        if (!modifierKey) {
            return; // 允许正常滚动
        }
        
        e.preventDefault();
        
        // 获取鼠标在 canvas 上的位置
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // 计算缩放前鼠标在画布坐标系中的位置
        const worldX = (mouseX - this.offsetX) / this.scale;
        const worldY = (mouseY - this.offsetY) / this.scale;
        
        // 计算缩放因子（更平滑的缩放）
        const delta = e.deltaY > 0 ? 0.95 : 1.05;
        const newScale = Math.max(this.minScale, Math.min(this.maxScale, this.scale * delta));
        
        // 更新缩放
        this.scale = newScale;
        
        // 调整偏移，使鼠标位置保持不变
        this.offsetX = mouseX - worldX * this.scale;
        this.offsetY = mouseY - worldY * this.scale;
        
        this.needsRender = true;
        this.emit('scaleChanged', { scale: this.scale, offsetX: this.offsetX, offsetY: this.offsetY });
    }

    handleTouchStart(e) {
        e.preventDefault();
        if (e.touches.length === 0) return;
        
        const touch = e.touches[0];
        const pos = this.screenToCanvas(touch.clientX, touch.clientY);
        
        if (this.currentTool && typeof this.currentTool.onMouseDown === 'function') {
            this.currentTool.onMouseDown(pos.x, pos.y, e);
        }
        
        this.emit('touchstart', { x: pos.x, y: pos.y, event: e });
    }

    handleTouchMove(e) {
        e.preventDefault();
        if (e.touches.length === 0) return;
        
        const touch = e.touches[0];
        const pos = this.screenToCanvas(touch.clientX, touch.clientY);
        
        if (this.currentTool && typeof this.currentTool.onMouseMove === 'function') {
            this.currentTool.onMouseMove(pos.x, pos.y, e);
        }
        
        this.emit('touchmove', { x: pos.x, y: pos.y, event: e });
    }

    handleTouchEnd(e) {
        e.preventDefault();
        
        // 使用最后一个触摸点的位置
        let pos = { x: 0, y: 0 };
        if (e.changedTouches.length > 0) {
            const touch = e.changedTouches[0];
            pos = this.screenToCanvas(touch.clientX, touch.clientY);
        }
        
        if (this.currentTool && typeof this.currentTool.onMouseUp === 'function') {
            this.currentTool.onMouseUp(pos.x, pos.y, e);
        }
        
        this.emit('touchend', { x: pos.x, y: pos.y, event: e });
    }

    setTool(tool) {
        // 停用当前工具
        if (this.currentTool) {
            if (typeof this.currentTool.deactivate === 'function') {
                this.currentTool.deactivate();
            }
            // 移除旧工具的事件监听
            this.currentTool.off('previewStarted');
            this.currentTool.off('previewUpdated');
            this.currentTool.off('previewEnded');
        }
        
        this.currentTool = tool;
        this.previewShape = null;
        
        // 设置鼠标样式
        this.updateCursor();
        
        // 激活新工具
        if (this.currentTool) {
            if (typeof this.currentTool.activate === 'function') {
                this.currentTool.activate();
            }
            
            // 监听工具的预览事件
            this.currentTool.on('previewStarted', (data) => {
                this.previewShape = data.shape;
                this.needsRender = true;
            });
            
            this.currentTool.on('previewUpdated', (data) => {
                this.previewShape = data.shape;
                this.needsRender = true;
            });
            
            this.currentTool.on('previewEnded', () => {
                this.previewShape = null;
                this.needsRender = true;
            });
            
            // 监听框选事件
            this.currentTool.on('boxSelectionStarted', (data) => {
                this.selectionBox = data.box;
                this.needsRender = true;
            });
            
            this.currentTool.on('boxSelectionUpdated', (data) => {
                this.selectionBox = data.box;
                this.needsRender = true;
            });
            
            this.currentTool.on('boxSelectionEnded', () => {
                this.selectionBox = null;
                this.needsRender = true;
            });
        }
        
        this.emit('toolChanged', { tool });
    }

    getCurrentTool() {
        return this.currentTool;
    }

    updateCursor() {
        if (!this.currentTool) {
            this.canvas.style.cursor = 'default';
            return;
        }
        
        // 根据工具类型设置鼠标样式
        const cursorMap = {
            'select': 'pointer',
            'point': 'crosshair',
            'line': 'crosshair',
            'rect': 'crosshair',
            'circle': 'crosshair',
            'polygon': 'crosshair',
            'brush': 'crosshair',
            'fill': 'crosshair',
            'eraser': 'not-allowed',
            'bezierCurve': 'crosshair',
            'bsplineCurve': 'crosshair',
            'bezierSurface': 'crosshair'
        };
        
        const cursor = cursorMap[this.currentTool.name] || 'crosshair';
        this.canvas.style.cursor = cursor;
    }

    resetView() {
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.needsRender = true;
    }

    zoomIn() {
        this.scale = Math.min(this.maxScale, this.scale * 1.2);
        this.needsRender = true;
    }

    zoomOut() {
        this.scale = Math.max(this.minScale, this.scale / 1.2);
        this.needsRender = true;
    }

    toggleGrid() {
        this.showGrid = !this.showGrid;
        this.needsRender = true;
        return this.showGrid;
    }

    setGridSize(size) {
        this.gridSize = Math.max(5, Math.min(100, size));
        this.needsRender = true;
    }

    setShapes(shapes) {
        this.shapes = shapes;
        this.needsRender = true;
    }

    requestRender() {
        this.needsRender = true;
    }

    exportToPNG() {
        return this.canvas.toDataURL('image/png');
    }

    exportToBlob(callback, type = 'image/png', quality = 1.0) {
        this.canvas.toBlob(callback, type, quality);
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    off(event, callback) {
        if (!this.listeners.has(event)) return;
        
        if (callback) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        } else {
            this.listeners.delete(event);
        }
    }

    emit(event, data) {
        if (!this.listeners.has(event)) return;
        
        const callbacks = this.listeners.get(event);
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`事件处理器错误 (${event}):`, error);
            }
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    destroy() {
        this.stopRenderLoop();
        this.listeners.clear();
        this.shapes = [];
        this.currentTool = null;
    }
}

export default CanvasManager;

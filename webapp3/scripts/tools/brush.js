/**
 * 画笔工具
 */

import { BaseTool } from './base.js';
import { BrushPath } from '../shapes/path.js';
import CONFIG from '../config.js';

export class BrushTool extends BaseTool {
    constructor(brushType = 'pen') {
        super('brush');
        this.brushType = brushType;
        this.drawing = false;
        this.points = [];
        this.currentPath = null;
        this.lastPoint = null;
        this.minDistance = CONFIG.TOOLS.brush.minDistance;
        this.currentStyle = {
            strokeColor: CONFIG.TOOLS.defaultStrokeColor,
            strokeWidth: CONFIG.TOOLS.brush.defaultWidth,
            opacity: CONFIG.TOOLS.defaultOpacity,
            smoothing: CONFIG.TOOLS.brush.smoothing
        };
    }

    setStyle(style) {
        this.currentStyle = { ...this.currentStyle, ...style };
    }

    setBrushType(type) {
        this.brushType = type;
    }

    setSmoothing(enabled) {
        this.currentStyle.smoothing = enabled;
    }

    onMouseDown(x, y, event) {
        this.drawing = true;
        this.points = [{ x, y }];
        this.lastPoint = { x, y };
        this.currentPath = new BrushPath(this.points, this.brushType, this.currentStyle);
        this.emit('previewStarted', { shape: this.currentPath });
    }

    onMouseMove(x, y, event) {
        if (!this.drawing || !this.currentPath) return;
        
        // 检查最小距离
        if (this.lastPoint) {
            const dx = x - this.lastPoint.x;
            const dy = y - this.lastPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.minDistance) {
                return;
            }
        }
        
        this.points.push({ x, y });
        this.lastPoint = { x, y };
        this.currentPath.points = [...this.points];
        this.emit('previewUpdated', { shape: this.currentPath });
    }

    onMouseUp(x, y, event) {
        if (!this.drawing || !this.currentPath) return;
        
        // 添加最后一个点
        if (this.lastPoint && (this.lastPoint.x !== x || this.lastPoint.y !== y)) {
            this.points.push({ x, y });
        }
        
        // 创建最终路径
        const path = new BrushPath([...this.points], this.brushType, this.currentStyle);
        
        // 应用平滑和简化
        if (this.currentStyle.smoothing) {
            path.smooth();
        }
        path.simplify(CONFIG.TOOLS.brush.simplifyTolerance);
        
        this.emit('shapeCreated', { shape: path });
        this.emit('previewEnded', { shape: this.currentPath });
        
        this.drawing = false;
        this.points = [];
        this.currentPath = null;
        this.lastPoint = null;
    }

    cancel() {
        if (this.drawing) {
            this.emit('previewEnded', { shape: this.currentPath });
        }
        this.drawing = false;
        this.points = [];
        this.currentPath = null;
        this.lastPoint = null;
    }
}

export default BrushTool;

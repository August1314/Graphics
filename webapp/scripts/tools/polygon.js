/**
 * 多边形工具
 */

import { BaseTool } from './base.js';
import { Polygon } from '../shapes/polygon.js';
import CONFIG from '../config.js';

export class PolygonTool extends BaseTool {
    constructor() {
        super('polygon');
        this.drawing = false;
        this.points = [];
        this.previewPolygon = null;
        this.currentStyle = {
            strokeColor: CONFIG.TOOLS.defaultStrokeColor,
            fillColor: CONFIG.TOOLS.defaultFillColor,
            strokeWidth: CONFIG.TOOLS.defaultStrokeWidth,
            opacity: CONFIG.TOOLS.defaultOpacity
        };
    }

    setStyle(style) {
        this.currentStyle = { ...this.currentStyle, ...style };
    }

    onMouseDown(x, y, event) {
        if (!this.drawing) {
            // 开始绘制
            this.drawing = true;
            this.points = [{ x, y }];
            this.previewPolygon = new Polygon(this.points, this.currentStyle);
            this.emit('previewStarted', { shape: this.previewPolygon });
        } else {
            // 添加点
            this.points.push({ x, y });
            this.previewPolygon.setPolygon([...this.points]);
            this.emit('previewUpdated', { shape: this.previewPolygon });
        }
    }

    onMouseMove(x, y, event) {
        if (!this.drawing || this.points.length === 0) return;
        
        // 显示预览线到当前鼠标位置
        const previewPoints = [...this.points, { x, y }];
        this.previewPolygon.setPolygon(previewPoints);
        this.emit('previewUpdated', { shape: this.previewPolygon });
    }

    onDoubleClick(x, y, event) {
        if (!this.drawing || this.points.length < 3) return;
        
        // 完成多边形
        const polygon = new Polygon([...this.points], this.currentStyle);
        this.emit('shapeCreated', { shape: polygon });
        this.emit('previewEnded', { shape: this.previewPolygon });
        
        this.drawing = false;
        this.points = [];
        this.previewPolygon = null;
    }

    cancel() {
        if (this.drawing) {
            this.emit('previewEnded', { shape: this.previewPolygon });
        }
        this.drawing = false;
        this.points = [];
        this.previewPolygon = null;
    }
}

export default PolygonTool;

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
        console.log('Polygon tool mouseDown:', x, y, 'drawing:', this.drawing);
        if (!this.drawing) {
            // 开始绘制
            this.drawing = true;
            this.points = [{ x, y }];
            this.previewPolygon = new Polygon([...this.points], this.currentStyle);
            console.log('Preview polygon created with points:', this.points);
            this.emit('previewStarted', { shape: this.previewPolygon });
        } else {
            // 添加点
            this.points.push({ x, y });
            this.previewPolygon.setPolygon([...this.points]);
            console.log('Polygon points updated:', this.points);
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
        
        // 移除最后一个重复的点（双击时 mousedown 会添加重复点）
        let finalPoints = [...this.points];
        if (finalPoints.length >= 2) {
            const lastPoint = finalPoints[finalPoints.length - 1];
            const secondLastPoint = finalPoints[finalPoints.length - 2];
            // 如果最后两个点相同，移除最后一个
            if (lastPoint.x === secondLastPoint.x && lastPoint.y === secondLastPoint.y) {
                finalPoints.pop();
                console.log('Removed duplicate last point');
            }
        }
        
        // 完成多边形
        const polygon = new Polygon(finalPoints, this.currentStyle);
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

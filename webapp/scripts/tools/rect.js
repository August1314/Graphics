/**
 * 矩形工具
 */

import { BaseTool } from './base.js';
import { Rectangle } from '../shapes/rect.js';
import CONFIG from '../config.js';

export class RectTool extends BaseTool {
    constructor() {
        super('rect');
        this.drawing = false;
        this.startPoint = null;
        this.previewRect = null;
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
        this.drawing = true;
        this.startPoint = { x, y };
        this.previewRect = new Rectangle(x, y, 0, 0, this.currentStyle);
        this.emit('previewStarted', { shape: this.previewRect });
    }

    onMouseMove(x, y, event) {
        if (!this.drawing || !this.previewRect) return;
        
        const width = x - this.startPoint.x;
        const height = y - this.startPoint.y;
        const rectX = width >= 0 ? this.startPoint.x : x;
        const rectY = height >= 0 ? this.startPoint.y : y;
        
        this.previewRect.setGeometry(rectX, rectY, Math.abs(width), Math.abs(height));
        this.emit('previewUpdated', { shape: this.previewRect });
    }

    onMouseUp(x, y, event) {
        if (!this.drawing) return;
        
        const width = x - this.startPoint.x;
        const height = y - this.startPoint.y;
        const rectX = width >= 0 ? this.startPoint.x : x;
        const rectY = height >= 0 ? this.startPoint.y : y;
        
        const rect = new Rectangle(rectX, rectY, Math.abs(width), Math.abs(height), this.currentStyle);
        this.emit('shapeCreated', { shape: rect });
        this.emit('previewEnded', { shape: this.previewRect });
        
        this.drawing = false;
        this.startPoint = null;
        this.previewRect = null;
    }

    cancel() {
        if (this.drawing) {
            this.emit('previewEnded', { shape: this.previewRect });
        }
        this.drawing = false;
        this.startPoint = null;
        this.previewRect = null;
    }
}

export default RectTool;

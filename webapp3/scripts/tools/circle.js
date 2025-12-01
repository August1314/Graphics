/**
 * 圆形工具
 */

import { BaseTool } from './base.js';
import { Circle } from '../shapes/circle.js';
import CONFIG from '../config.js';

export class CircleTool extends BaseTool {
    constructor() {
        super('circle');
        this.drawing = false;
        this.centerPoint = null;
        this.previewCircle = null;
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
        this.centerPoint = { x, y };
        this.previewCircle = new Circle(x, y, 0, this.currentStyle);
        this.emit('previewStarted', { shape: this.previewCircle });
    }

    onMouseMove(x, y, event) {
        if (!this.drawing || !this.previewCircle) return;
        
        const dx = x - this.centerPoint.x;
        const dy = y - this.centerPoint.y;
        const radius = Math.sqrt(dx * dx + dy * dy);
        
        this.previewCircle.setCenterRadius(this.centerPoint.x, this.centerPoint.y, radius);
        this.emit('previewUpdated', { shape: this.previewCircle });
    }

    onMouseUp(x, y, event) {
        if (!this.drawing) return;
        
        const dx = x - this.centerPoint.x;
        const dy = y - this.centerPoint.y;
        const radius = Math.sqrt(dx * dx + dy * dy);
        
        const circle = new Circle(this.centerPoint.x, this.centerPoint.y, radius, this.currentStyle);
        this.emit('shapeCreated', { shape: circle });
        this.emit('previewEnded', { shape: this.previewCircle });
        
        this.drawing = false;
        this.centerPoint = null;
        this.previewCircle = null;
    }

    cancel() {
        if (this.drawing) {
            this.emit('previewEnded', { shape: this.previewCircle });
        }
        this.drawing = false;
        this.centerPoint = null;
        this.previewCircle = null;
    }
}

export default CircleTool;

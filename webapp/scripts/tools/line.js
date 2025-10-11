/**
 * 线工具
 */

import { BaseTool } from './base.js';
import { Line } from '../shapes/line.js';
import CONFIG from '../config.js';

export class LineTool extends BaseTool {
    constructor() {
        super('line');
        this.drawing = false;
        this.startPoint = null;
        this.previewLine = null;
        this.currentStyle = {
            strokeColor: CONFIG.TOOLS.defaultStrokeColor,
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
        this.previewLine = new Line(x, y, x, y, this.currentStyle);
        this.emit('previewStarted', { shape: this.previewLine });
    }

    onMouseMove(x, y, event) {
        if (!this.drawing || !this.previewLine) return;
        this.previewLine.setPoints(this.startPoint.x, this.startPoint.y, x, y);
        this.emit('previewUpdated', { shape: this.previewLine });
    }

    onMouseUp(x, y, event) {
        if (!this.drawing) return;
        
        const line = new Line(this.startPoint.x, this.startPoint.y, x, y, this.currentStyle);
        this.emit('shapeCreated', { shape: line });
        this.emit('previewEnded', { shape: this.previewLine });
        
        this.drawing = false;
        this.startPoint = null;
        this.previewLine = null;
    }

    cancel() {
        if (this.drawing) {
            this.emit('previewEnded', { shape: this.previewLine });
        }
        this.drawing = false;
        this.startPoint = null;
        this.previewLine = null;
    }
}

export default LineTool;

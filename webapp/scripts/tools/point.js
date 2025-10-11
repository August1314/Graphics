/**
 * 点工具
 */

import { BaseTool } from './base.js';
import { Point } from '../shapes/point.js';
import CONFIG from '../config.js';

export class PointTool extends BaseTool {
    constructor() {
        super('point');
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
        const radius = CONFIG.TOOLS.point.defaultRadius;
        const point = new Point(x, y, radius, this.currentStyle);
        this.emit('shapeCreated', { shape: point });
    }
}

export default PointTool;

/**
 * 橡皮擦工具
 */

import { BaseTool } from './base.js';
import CONFIG from '../config.js';

export class EraserTool extends BaseTool {
    constructor(mode = 'object') {
        super('eraser');
        this.mode = mode; // 'object' or 'path'
        this.size = CONFIG.TOOLS.eraser.defaultSize;
        this.erasing = false;
        this.document = null;
        this.erasedShapes = [];
    }

    setDocument(document) {
        this.document = document;
    }

    setMode(mode) {
        this.mode = mode;
    }

    setSize(size) {
        this.size = Math.max(CONFIG.TOOLS.eraser.minSize, Math.min(size, CONFIG.TOOLS.eraser.maxSize));
    }

    onMouseDown(x, y, event) {
        if (!this.document) return;
        
        this.erasing = true;
        this.erasedShapes = [];
        this.eraseAt(x, y);
    }

    onMouseMove(x, y, event) {
        if (!this.erasing) return;
        this.eraseAt(x, y);
    }

    onMouseUp(x, y, event) {
        if (this.erasing && this.erasedShapes.length > 0) {
            // 松开鼠标时，将所有擦除操作作为一次操作保存到历史记录
            if (this.document) {
                this.document.saveState();
            }
            this.emit('shapesErased', { shapes: this.erasedShapes });
        }
        this.erasing = false;
        this.erasedShapes = [];
    }

    eraseAt(x, y) {
        if (!this.document) return;
        
        if (this.mode === 'object') {
            this.eraseObject(x, y);
        } else {
            // 路径擦除模式（简化实现）
            this.eraseObject(x, y);
        }
    }

    eraseObject(x, y) {
        const shapes = this.document.getShapes();
        
        for (let i = shapes.length - 1; i >= 0; i--) {
            const shape = shapes[i];
            
            // 检查橡皮擦区域是否与图形相交
            if (this.intersects(shape, x, y)) {
                if (!this.erasedShapes.includes(shape)) {
                    this.erasedShapes.push(shape);
                    // 移除图形但不立即保存状态
                    this.document.removeShape(shape, false);
                }
            }
        }
    }

    intersects(shape, x, y) {
        // 使用图形自己的 contains 方法进行更精确的检测
        if (typeof shape.contains === 'function') {
            // 检查橡皮擦中心点是否在图形内
            if (shape.contains(x, y)) {
                return true;
            }
            
            // 检查橡皮擦区域的几个点是否与图形相交
            const halfSize = this.size / 2;
            const checkPoints = [
                { x: x - halfSize, y: y },
                { x: x + halfSize, y: y },
                { x: x, y: y - halfSize },
                { x: x, y: y + halfSize }
            ];
            
            for (const point of checkPoints) {
                if (shape.contains(point.x, point.y)) {
                    return true;
                }
            }
        }
        
        return false;
    }

    cancel() {
        this.erasing = false;
        this.erasedShapes = [];
    }
}

export default EraserTool;

/**
 * Bézier 曲面工具
 * 拖出一个矩形生成 4x4 控制网格；再次点击可拖拽控制点编辑
 */

import { BaseTool } from './base.js';
import CONFIG from '../config.js';
import { BezierSurface } from '../shapes/bezier_surface.js';

export class BezierSurfaceTool extends BaseTool {
    constructor() {
        super('bezierSurface');
        this.document = null;
        this.drawing = false;
        this.startPoint = null;
        this.previewSurface = null;
        this.draggingControl = null; // { surface, i, j }
        this.hitTolerance = 10;
        this.surfaceMode = 'grid';
        this.currentStyle = {
            strokeColor: CONFIG.TOOLS.defaultStrokeColor,
            fillColor: '#cccccc',
            strokeWidth: CONFIG.TOOLS.defaultStrokeWidth,
            opacity: CONFIG.TOOLS.defaultOpacity
        };
    }

    setDocument(document) {
        this.document = document;
    }

    setStyle(style) {
        this.currentStyle = { ...this.currentStyle, ...style };
        if (this.previewSurface) {
            this.previewSurface.properties = {
                ...this.previewSurface.properties,
                ...this.currentStyle
            };
        }
    }

    setMode(mode) {
        this.surfaceMode = mode;
        // 填充模式下，确保当前样式有填充色
        if (mode === 'fill' && this.currentStyle.fillColor === 'transparent') {
            this.currentStyle.fillColor = '#cccccc';
        }
        if (this.previewSurface) {
            this.previewSurface.mode = mode;
            if (this.previewSurface.properties) {
                this.previewSurface.properties.mode = mode;
                if (mode === 'fill' && this.previewSurface.properties.fillColor === 'transparent') {
                    this.previewSurface.properties.fillColor = this.currentStyle.fillColor || '#cccccc';
                    this.previewSurface.properties.fillTransparent = false;
                }
            }
            if (mode === 'fill' && this.previewSurface.properties.fillColor === 'transparent') {
                this.previewSurface.properties.fillColor = this.currentStyle.fillColor || '#cccccc';
            }
            this.previewSurface.cacheValid = false;
        }
    }

    onMouseDown(x, y, event) {
        // 优先检查是否拖拽已有控制点
        if (!this.drawing && this.tryStartControlDrag(x, y)) {
            return;
        }

        // 否则开始新曲面
        this.drawing = true;
        this.startPoint = { x, y };
        const controlGrid = this.createGridFromRect(x, y, x + 1, y + 1);
        this.previewSurface = new BezierSurface(controlGrid, {
            ...this.currentStyle,
            stepsU: 10,
            stepsV: 10,
            mode: this.surfaceMode,
            showControlGrid: true
        });
        this.emit('previewStarted', { shape: this.previewSurface });
    }

    onMouseMove(x, y) {
        // 控制点拖拽
        if (this.draggingControl) {
            this.dragControlPoint(x, y);
            return;
        }

        // 预览矩形框生成控制网格
        if (!this.drawing || !this.previewSurface || !this.startPoint) return;
        const grid = this.createGridFromRect(
            this.startPoint.x,
            this.startPoint.y,
            x,
            y
        );
        this.previewSurface.controlGrid = grid;
        this.previewSurface.cacheValid = false;
        this.emit('previewUpdated', { shape: this.previewSurface });
    }

    onMouseUp(x, y) {
        if (this.draggingControl) {
            this.finishControlDrag();
            return;
        }

        if (!this.drawing || !this.previewSurface || !this.startPoint) return;

        const minMove = 3;
        if (Math.abs(x - this.startPoint.x) < minMove && Math.abs(y - this.startPoint.y) < minMove) {
            // 拖动距离太小，不创建
            this.emit('previewEnded', { shape: this.previewSurface });
            this.resetState();
            return;
        }

        const grid = this.createGridFromRect(
            this.startPoint.x,
            this.startPoint.y,
            x,
            y
        );
        const surface = new BezierSurface(grid, {
            ...this.currentStyle,
            stepsU: this.previewSurface.stepsU,
            stepsV: this.previewSurface.stepsV,
            mode: this.previewSurface.mode,
            showControlGrid: true
        });
        this.emit('shapeCreated', { shape: surface });
        this.emit('previewEnded', { shape: this.previewSurface });
        this.resetState();
    }

    onDoubleClick(x, y) {
        // 双击可在该位置切换曲面渲染模式 grid/fill
        if (!this.document) return;
        const shapes = this.document.getShapes();
        for (let i = shapes.length - 1; i >= 0; i--) {
            const shape = shapes[i];
            if (shape instanceof BezierSurface && shape.contains(x, y)) {
                shape.mode = shape.mode === 'grid' ? 'fill' : 'grid';
                this.surfaceMode = shape.mode;
                shape.cacheValid = false;
                this.document.markModified();
                this.document.emit('shapesChanged', { shapes: this.document.getShapes() });
                break;
            }
        }
    }

    tryStartControlDrag(x, y) {
        if (!this.document) return false;
        const shapes = this.document.getShapes();
        for (let s = shapes.length - 1; s >= 0; s--) {
            const shape = shapes[s];
            if (!(shape instanceof BezierSurface)) continue;
            const hit = shape.hitTestControlPoint(x, y, this.hitTolerance);
            if (hit) {
                this.draggingControl = { surface: shape, i: hit.i, j: hit.j };
                this.document.selectShape(shape);
                return true;
            }
        }
        return false;
    }

    dragControlPoint(x, y) {
        if (!this.draggingControl) return;
        const { surface, i, j } = this.draggingControl;
        surface.setControlPoint(i, j, x, y);
        if (this.document) {
            this.document.markModified();
            this.document.emit('shapesChanged', { shapes: this.document.getShapes() });
        }
    }

    finishControlDrag() {
        if (this.document) {
            this.document.saveState();
        }
        this.draggingControl = null;
    }

    /**
     * 由对角线两个点生成 4x4 控制网格
     */
    createGridFromRect(x1, y1, x2, y2) {
        const minX = Math.min(x1, x2);
        const maxX = Math.max(x1, x2);
        const minY = Math.min(y1, y2);
        const maxY = Math.max(y1, y2);
        const grid = [];
        for (let i = 0; i < 4; i++) {
            grid[i] = [];
            const v = i / 3;
            const y = minY + (maxY - minY) * v;
            for (let j = 0; j < 4; j++) {
                const u = j / 3;
                const x = minX + (maxX - minX) * u;
                grid[i][j] = { x, y };
            }
        }
        return grid;
    }

    cancel() {
        if (this.drawing && this.previewSurface) {
            this.emit('previewEnded', { shape: this.previewSurface });
        }
        this.resetState();
        this.draggingControl = null;
    }

    resetState() {
        this.drawing = false;
        this.startPoint = null;
        this.previewSurface = null;
    }
}

export default BezierSurfaceTool;



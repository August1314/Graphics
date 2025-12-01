/**
 * Bézier 曲线工具
 */

import { BaseTool } from './base.js';
import CONFIG from '../config.js';
import { BezierCurve } from '../shapes/bezier_curve.js';

export class BezierCurveTool extends BaseTool {
    constructor() {
        super('bezierCurve');
        this.document = null;
        this.drawing = false;
        this.controlPoints = [];
        this.previewCurve = null;
        this.draggingControl = null;
        this.hitTolerance = 10;
        this.currentStyle = {
            strokeColor: CONFIG.TOOLS.defaultStrokeColor,
            strokeWidth: CONFIG.TOOLS.defaultStrokeWidth,
            opacity: CONFIG.TOOLS.defaultOpacity
        };
    }

    setDocument(document) {
        this.document = document;
    }

    setStyle(style) {
        this.currentStyle = { ...this.currentStyle, ...style };
        if (this.previewCurve) {
            this.previewCurve.properties = { ...this.previewCurve.properties, ...this.currentStyle };
        }
    }

    onMouseDown(x, y, event) {
        if (this.draggingControl) return;

        if (!this.drawing && this.tryStartControlDrag(x, y)) {
            return;
        }

        if (!this.drawing) {
            this.startCurve(x, y);
        } else {
            this.addControlPoint(x, y);
        }
    }

    onMouseMove(x, y, event) {
        if (this.draggingControl) {
            this.dragControlPoint(x, y);
            return;
        }

        if (!this.drawing || !this.previewCurve) return;

        const previewPoints = [...this.controlPoints, { x, y }];
        this.previewCurve.setControlPoints(previewPoints);
        this.emit('previewUpdated', { shape: this.previewCurve });
    }

    onMouseUp(x, y, event) {
        if (this.draggingControl) {
            this.finishControlDrag();
        }
    }

    onDoubleClick(x, y) {
        if (this.drawing && this.controlPoints.length >= 2) {
            this.finishCurve();
        }
    }

    startCurve(x, y) {
        this.drawing = true;
        this.controlPoints = [{ x, y }];
        this.previewCurve = new BezierCurve(this.controlPoints, {
            ...this.currentStyle,
            samples: 64,
            showControlPolygon: true
        });
        this.emit('previewStarted', { shape: this.previewCurve });
    }

    addControlPoint(x, y) {
        this.controlPoints.push({ x, y });
        this.previewCurve.setControlPoints(this.controlPoints);
        this.emit('previewUpdated', { shape: this.previewCurve });
    }

    finishCurve() {
        if (this.controlPoints.length < 2) return;
        const curve = new BezierCurve(this.controlPoints, {
            ...this.currentStyle,
            samples: this.previewCurve.samples,
            showControlPolygon: true
        });
        this.emit('shapeCreated', { shape: curve });
        this.emit('previewEnded', { shape: this.previewCurve });
        this.resetState();
    }

    tryStartControlDrag(x, y) {
        if (!this.document) return false;
        const shapes = this.document.getShapes();
        for (let i = shapes.length - 1; i >= 0; i--) {
            const shape = shapes[i];
            if (!(shape instanceof BezierCurve)) continue;
            const index = shape.hitTestControlPoint(x, y, this.hitTolerance);
            if (index !== -1) {
                this.draggingControl = { shape, index };
                this.document.selectShape(shape);
                return true;
            }
        }
        return false;
    }

    dragControlPoint(x, y) {
        if (!this.draggingControl) return;
        this.draggingControl.shape.updateControlPoint(this.draggingControl.index, x, y);
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

    cancel() {
        if (this.drawing) {
            this.emit('previewEnded', { shape: this.previewCurve });
        }
        this.resetState();
        this.draggingControl = null;
    }

    resetState() {
        this.drawing = false;
        this.controlPoints = [];
        this.previewCurve = null;
    }
}

export default BezierCurveTool;


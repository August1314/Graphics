/**
 * B 样条曲线工具
 */

import { BaseTool } from './base.js';
import CONFIG from '../config.js';
import { BSplineCurve } from '../shapes/bspline_curve.js';

export class BSplineCurveTool extends BaseTool {
    constructor() {
        super('bsplineCurve');
        this.document = null;
        this.drawing = false;
        this.controlPoints = [];
        this.previewCurve = null;
        this.draggingControl = null;
        this.hitTolerance = 10;
        this.degree = 3;
        this.samples = 64;
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
        // 预览模式下，需要至少 degree + 2 个控制点（包括鼠标位置）才显示曲线
        // 这样可以避免当控制点数量 = degree + 1 时显示为直线的问题
        const minPointsForPreview = this.degree + 2;
        
        if (previewPoints.length >= minPointsForPreview) {
            // 更新预览曲线的控制点（包括当前鼠标位置）
            this.previewCurve.setControlPoints(previewPoints);
            // 动态调整预览曲线的 degree，确保不超过控制点数-1
            const effectiveDegree = Math.min(this.degree, previewPoints.length - 1);
            this.previewCurve.setDegree(effectiveDegree);
            this.emit('previewUpdated', { shape: this.previewCurve });
        } else {
            // 控制点不足时，只更新控制点位置（用于显示控制多边形），但不触发曲线渲染
            // 控制多边形会通过 renderControlPolygon 显示
            this.previewCurve.setControlPoints(previewPoints);
            this.emit('previewUpdated', { shape: this.previewCurve });
        }
    }

    onMouseUp() {
        if (this.draggingControl) {
            this.finishControlDrag();
        }
    }

    onDoubleClick() {
        const minPoints = Math.max(2, this.degree + 1);
        if (this.drawing && this.controlPoints.length >= minPoints) {
            this.finishCurve();
        }
    }

    startCurve(x, y) {
        this.drawing = true;
        this.controlPoints = [{ x, y }];
        // 始终创建预览曲线对象，以便显示控制多边形（控制点和连接线）
        this.previewCurve = new BSplineCurve(this.controlPoints, {
            ...this.currentStyle,
            degree: this.degree,
            samples: this.samples,
            showControlPolygon: true
        });
        // 标记为预览模式，控制点不足时只显示控制多边形，不显示曲线
        this.previewCurve._isPreview = true;
        this.emit('previewStarted', { shape: this.previewCurve });
    }

    addControlPoint(x, y) {
        this.controlPoints.push({ x, y });
        // 更新预览曲线的控制点
        if (this.previewCurve) {
            this.previewCurve.setControlPoints(this.controlPoints);
            const effectiveDegree = Math.min(this.degree, this.controlPoints.length - 1);
            this.previewCurve.setDegree(effectiveDegree);
            this.emit('previewUpdated', { shape: this.previewCurve });
        }
    }

    finishCurve() {
        const minPoints = Math.max(2, this.degree + 1); // 至少需要 degree+1 个控制点才能形成真正的 B 样条曲线
        if (this.controlPoints.length < minPoints) {
            // 如果控制点不足，取消绘制
            this.cancel();
            return;
        }
        
        // 计算有效的 degree
        // 如果控制点数量刚好等于 degree + 1，节点向量会变成 [0,0,0,0,1,1,1,1]，导致退化为 Bézier 曲线
        // 为了避免这种情况，当控制点数量 = degree + 1 时，降低 degree
        // 但要确保 degree >= 2，避免退化为分段线性插值（degree=1 时 B 样条就是控制多边形本身）
        let effectiveDegree = Math.min(this.degree, this.controlPoints.length - 1);
        if (this.controlPoints.length === this.degree + 1) {
            // 降低 degree，避免退化，但确保 degree >= 2
            // 如果降低后 degree < 2，说明控制点数量太少，需要更多控制点
            const reducedDegree = Math.max(2, this.controlPoints.length - 2);
            if (reducedDegree < 2 || this.controlPoints.length < reducedDegree + 1) {
                // 控制点数量不足，无法形成有效的 B 样条曲线
                this.cancel();
                return;
            }
            effectiveDegree = reducedDegree;
        }
        
        const curve = new BSplineCurve(this.controlPoints, {
            ...this.currentStyle,
            degree: effectiveDegree,
            samples: this.samples,
            showControlPolygon: true
        });
        this.emit('shapeCreated', { shape: curve });
        if (this.previewCurve) {
            this.emit('previewEnded', { shape: this.previewCurve });
        }

        this.resetState();
    }

    tryStartControlDrag(x, y) {
        if (!this.document) return false;
        const shapes = this.document.getShapes();
        for (let i = shapes.length - 1; i >= 0; i--) {
            const shape = shapes[i];
            if (!(shape instanceof BSplineCurve)) continue;
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
        if (this.drawing && this.previewCurve) {
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

export default BSplineCurveTool;


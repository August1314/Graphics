/**
 * Bézier 曲线图形
 */

import CurveShapeBase from './curve_base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { AlgorithmFactory } from '../algorithms/factory.js';

export class BezierCurve extends CurveShapeBase {
    constructor(controlPoints = [], properties = {}) {
        super('bezier_curve', controlPoints, properties);
        this.algorithm = properties.algorithm || 'bezier';
    }

    render(ctx) {
        try {
            if (this.useRasterization) {
                this.renderWithAlgorithm(ctx);
            } else {
                this.renderWithCanvas(ctx);
            }
        } catch (error) {
            console.error('Bezier curve rasterization failed, fallback to canvas:', error);
            this.renderWithCanvas(ctx);
        }

        if (this.selected || this.showControlPolygon) {
            this.renderControlPolygon(ctx);
        }

        this.renderSelection(ctx);
    }

    renderWithAlgorithm(ctx) {
        if (this.controlPoints.length < 2) return;
        const bounds = this.getBounds();
        const offsetX = bounds.x;
        const offsetY = bounds.y;

        if (this.cacheValid && this.cache) {
            ctx.drawImage(this.cache, offsetX, offsetY);
            return;
        }

        if (!this.cache) {
            this.cache = document.createElement('canvas');
        }
        this.cache.width = Math.max(1, Math.ceil(bounds.width));
        this.cache.height = Math.max(1, Math.ceil(bounds.height));

        const renderer = new PixelRenderer(this.cache);
        renderer.beginPixelMode();

        const algorithm = AlgorithmFactory.createCurveAlgorithm(this.algorithm);
        algorithm.execute({
            controlPoints: this.controlPoints.map(pt => ({
                x: pt.x - offsetX,
                y: pt.y - offsetY
            })),
            steps: this.samples,
            color: this.properties.strokeColor,
            lineWidth: this.properties.strokeWidth || 2
        }, renderer);

        renderer.endPixelMode();
        ctx.drawImage(this.cache, offsetX, offsetY);
        this.cacheValid = true;
        this.lastStats = algorithm.getStats();
    }

    renderWithCanvas(ctx) {
        if (this.controlPoints.length < 2) return;
        ctx.save();
        this.applyStyle(ctx);
        ctx.beginPath();
        const samplePoints = this.getSamplePoints();
        ctx.moveTo(samplePoints[0].x, samplePoints[0].y);
        for (let i = 1; i < samplePoints.length; i++) {
            ctx.lineTo(samplePoints[i].x, samplePoints[i].y);
        }
        ctx.stroke();
        ctx.restore();
    }

    getSamplePoints() {
        const points = [];
        for (let i = 0; i <= this.samples; i++) {
            const t = i / this.samples;
            points.push(this.evaluate(t));
        }
        return points;
    }

    evaluate(t) {
        let pts = this.controlPoints.map(p => ({ ...p }));
        const n = pts.length - 1;
        for (let r = 1; r <= n; r++) {
            for (let i = 0; i <= n - r; i++) {
                pts[i] = {
                    x: (1 - t) * pts[i].x + t * pts[i + 1].x,
                    y: (1 - t) * pts[i].y + t * pts[i + 1].y
                };
            }
        }
        return pts[0];
    }

    rotate(angleRad, cx, cy) {
        if (!this.controlPoints.length) return;
        const center = this.getCenter();
        const ox = cx !== undefined ? cx : center.x;
        const oy = cy !== undefined ? cy : center.y;
        const cosA = Math.cos(angleRad);
        const sinA = Math.sin(angleRad);
        this.controlPoints = this.controlPoints.map(p => {
            const dx = p.x - ox;
            const dy = p.y - oy;
            return {
                x: ox + dx * cosA - dy * sinA,
                y: oy + dx * sinA + dy * cosA
            };
        });
        this.cacheValid = false;
    }

    scale(scaleX, scaleY, cx, cy) {
        if (!this.controlPoints.length) return;
        const sy = scaleY !== undefined ? scaleY : scaleX;
        const center = this.getCenter();
        const ox = cx !== undefined ? cx : center.x;
        const oy = cy !== undefined ? cy : center.y;
        this.controlPoints = this.controlPoints.map(p => ({
            x: ox + (p.x - ox) * scaleX,
            y: oy + (p.y - oy) * sy
        }));
        this.cacheValid = false;
    }

    toDict() {
        const base = super.toDict();
        base.properties = {
            ...base.properties,
            algorithm: this.algorithm
        };
        return base;
    }

    static fromDict(data) {
        const props = data.properties || {};
        const curve = new BezierCurve(props.controlPoints || [], {
            ...props,
            id: data.id
        });
        curve.samples = props.samples || 64;
        curve.algorithm = props.algorithm || 'bezier';
        curve.showControlPolygon = props.showControlPolygon !== false;
        curve.useRasterization = props.useRasterization !== false;
        curve.timestamp = data.timestamp;
        return curve;
    }
}

export default BezierCurve;


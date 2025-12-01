/**
 * B 样条曲线图形
 */

import CurveShapeBase from './curve_base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { AlgorithmFactory } from '../algorithms/factory.js';

export class BSplineCurve extends CurveShapeBase {
    constructor(controlPoints = [], properties = {}) {
        super('bspline_curve', controlPoints, properties);
        this.degree = properties.degree || 3;
        this.knots = Array.isArray(properties.knots) ? [...properties.knots] : null;
        this.algorithm = 'bspline';
    }

    render(ctx) {
        try {
            if (this.useRasterization) {
                this.renderWithAlgorithm(ctx);
            } else {
                this.renderWithCanvas(ctx);
            }
        } catch (error) {
            console.error('B-spline rasterization failed, fallback to canvas:', error);
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

        const algorithm = AlgorithmFactory.createCurveAlgorithm('bspline');
        const knots = this.getEffectiveKnots();
        algorithm.execute({
            controlPoints: this.controlPoints.map(pt => ({
                x: pt.x - offsetX,
                y: pt.y - offsetY
            })),
            degree: this.degree,
            knots,
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

    evaluate(tNorm) {
        const degree = Math.max(1, Math.min(this.degree, this.controlPoints.length - 1));
        const knots = this.getEffectiveKnots();
        const domainStart = knots[degree];
        const domainEnd = knots[knots.length - degree - 1];
        const t = domainStart + tNorm * (domainEnd - domainStart);
        const clampedT = Math.min(Math.max(t, knots[degree]), knots[knots.length - 1]);

        let point = { x: 0, y: 0 };
        for (let i = 0; i < this.controlPoints.length; i++) {
            const basis = this.basisFunction(i, degree, clampedT, knots);
            point.x += basis * this.controlPoints[i].x;
            point.y += basis * this.controlPoints[i].y;
        }
        return point;
    }

    getEffectiveKnots() {
        const needed = this.controlPoints.length + this.degree + 1;
        if (Array.isArray(this.knots) && this.knots.length >= needed) {
            return this.knots;
        }
        return this.generateUniformKnots(this.controlPoints.length, this.degree);
    }

    generateUniformKnots(pointCount, degree) {
        const knotCount = pointCount + degree + 1;
        const knots = [];
        const segments = knotCount - 2 * degree;
        for (let i = 0; i < knotCount; i++) {
            if (i <= degree) {
                knots.push(0);
            } else if (i >= knotCount - degree - 1) {
                knots.push(1);
            } else {
                knots.push((i - degree) / segments);
            }
        }
        return knots;
    }

    basisFunction(i, k, t, knots) {
        if (k === 0) {
            const inRange = (knots[i] <= t && t < knots[i + 1]) ||
                (t === knots[knots.length - 1] && i === knots.length - 2);
            return inRange ? 1 : 0;
        }
        const denom1 = knots[i + k] - knots[i];
        const denom2 = knots[i + k + 1] - knots[i + 1];
        const term1 = denom1 === 0 ? 0 :
            ((t - knots[i]) / denom1) * this.basisFunction(i, k - 1, t, knots);
        const term2 = denom2 === 0 ? 0 :
            ((knots[i + k + 1] - t) / denom2) * this.basisFunction(i + 1, k - 1, t, knots);
        return term1 + term2;
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
        this.invalidateCache();
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
        this.invalidateCache();
    }

    setDegree(degree) {
        this.degree = Math.max(1, degree);
        this.invalidateCache();
    }

    setKnots(knots) {
        this.knots = Array.isArray(knots) ? [...knots] : null;
        this.invalidateCache();
    }

    toDict() {
        const base = super.toDict();
        base.properties = {
            ...base.properties,
            degree: this.degree,
            knots: this.knots
        };
        return base;
    }

    static fromDict(data) {
        const props = data.properties || {};
        const curve = new BSplineCurve(props.controlPoints || [], {
            ...props,
            id: data.id
        });
        curve.samples = props.samples || 64;
        curve.degree = props.degree || 3;
        curve.knots = Array.isArray(props.knots) ? [...props.knots] : null;
        curve.showControlPolygon = props.showControlPolygon !== false;
        curve.useRasterization = props.useRasterization !== false;
        curve.timestamp = data.timestamp;
        return curve;
    }
}

export default BSplineCurve;


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
        // 如果是预览模式，需要更多控制点才能显示真正的 B 样条曲线
        // 当控制点数量 = degree + 1 时，B 样条退化为 Bézier 曲线，节点向量变成 [0,0,0,0,1,1,1,1]
        // 这会导致曲线可能显示为直线（特别是当控制点共线时）
        // 所以预览模式下，需要至少 degree + 2 个控制点才显示曲线
        const minPointsForPreview = this.degree + 2;
        const minPointsForCurve = this.degree + 1;
        let shouldRenderCurve = true;
        
        if (this._isPreview) {
            // 预览模式：需要更多控制点才显示曲线，避免显示为直线
            shouldRenderCurve = this.controlPoints.length >= minPointsForPreview;
        } else {
            // 非预览模式：正常的 B 样条曲线
            // 即使控制点数量 = degree + 1 时退化为 Bézier，也允许显示（这是正常的 B 样条行为）
            shouldRenderCurve = this.controlPoints.length >= minPointsForCurve;
        }
        
        if (shouldRenderCurve) {
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
        }

        // 始终显示控制多边形（如果启用）
        if (this.selected || this.showControlPolygon) {
            this.renderControlPolygon(ctx);
        }

        this.renderSelection(ctx);
    }

    renderWithAlgorithm(ctx) {
        if (this.controlPoints.length < 2) return;
        // 如果是预览模式，需要更多控制点才渲染曲线
        const minPointsForPreview = this.degree + 2;
        const minPointsForCurve = this.degree + 1;
        if (this._isPreview && this.controlPoints.length < minPointsForPreview) {
            return;
        }
        if (!this._isPreview && this.controlPoints.length < minPointsForCurve) {
            return;
        }
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
        // 如果是预览模式，需要更多控制点才渲染曲线
        const minPointsForPreview = this.degree + 2;
        const minPointsForCurve = this.degree + 1;
        if (this._isPreview && this.controlPoints.length < minPointsForPreview) {
            return;
        }
        if (!this._isPreview && this.controlPoints.length < minPointsForCurve) {
            return;
        }
        ctx.save();
        this.applyStyle(ctx);
        ctx.beginPath();
        const samplePoints = this.getSamplePoints();
        if (samplePoints.length === 0) return;
        ctx.moveTo(samplePoints[0].x, samplePoints[0].y);
        for (let i = 1; i < samplePoints.length; i++) {
            ctx.lineTo(samplePoints[i].x, samplePoints[i].y);
        }
        ctx.stroke();
        ctx.restore();
    }

    getSamplePoints() {
        if (this.controlPoints.length < 2) return [];
        const points = [];
        const samples = Math.max(1, this.samples); // 防止除零错误
        for (let i = 0; i <= samples; i++) {
            const t = i / samples;
            const pt = this.evaluate(t);
            // 检查点是否有效（不是 (0,0) 或者与控制点重合）
            // 如果 evaluate 返回 (0,0) 且控制点不在原点，说明计算错误，跳过该点
            const isInvalid = (pt.x === 0 && pt.y === 0) && 
                             this.controlPoints.length > 0 && 
                             (this.controlPoints[0].x !== 0 || this.controlPoints[0].y !== 0);
            if (!isInvalid) {
                points.push(pt);
            }
        }
        return points;
    }

    evaluate(tNorm) {
        if (this.controlPoints.length === 0) {
            return { x: 0, y: 0 };
        }
        if (this.controlPoints.length === 1) {
            return { x: this.controlPoints[0].x, y: this.controlPoints[0].y };
        }
        const degree = Math.max(1, Math.min(this.degree, this.controlPoints.length - 1));
        const knots = this.getEffectiveKnots();
        if (knots.length < degree + 1) {
            return { x: 0, y: 0 };
        }
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

    getBounds() {
        // 对于 B 样条曲线，需要基于实际曲线采样点计算边界框
        // 因为曲线可能超出控制点的边界框
        const samplePoints = this.getSamplePoints();
        if (samplePoints.length === 0) {
            // 如果没有采样点，回退到基于控制点的边界框
            return super.getBounds();
        }
        
        const stroke = Math.max(1, this.properties.strokeWidth || 1);
        let minX = samplePoints[0].x;
        let maxX = samplePoints[0].x;
        let minY = samplePoints[0].y;
        let maxY = samplePoints[0].y;
        
        for (const pt of samplePoints) {
            minX = Math.min(minX, pt.x);
            maxX = Math.max(maxX, pt.x);
            minY = Math.min(minY, pt.y);
            maxY = Math.max(maxY, pt.y);
        }
        
        // 也包含控制点，确保控制多边形在边界框内
        for (const pt of this.controlPoints) {
            minX = Math.min(minX, pt.x);
            maxX = Math.max(maxX, pt.x);
            minY = Math.min(minY, pt.y);
            maxY = Math.max(maxY, pt.y);
        }
        
        const padding = Math.ceil(stroke / 2) + 4;
        return {
            x: minX - padding,
            y: minY - padding,
            width: (maxX - minX) + padding * 2,
            height: (maxY - minY) + padding * 2
        };
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
        const segments = Math.max(1, knotCount - 2 * degree); // 防止除零错误
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


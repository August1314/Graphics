/**
 * B 样条曲线光栅化算法（支持二/三次）
 */

import { BaseAlgorithm } from '../base.js';

export class BSplineCurveAlgorithm extends BaseAlgorithm {
    constructor() {
        super('B-Spline Curve', 'Cox-de Boor 样条采样');
        this.basisCache = new Map();
    }

    execute(params, renderer) {
        const {
            controlPoints = [],
            degree = 3,
            knots = null,
            steps = 64,
            color = '#000000',
            lineWidth = 2
        } = params || {};

        if (!renderer || controlPoints.length < 2) return;

        const clampedDegree = Math.max(1, Math.min(degree, controlPoints.length - 1));
        const knotVector = Array.isArray(knots) && knots.length >= controlPoints.length + clampedDegree + 1
            ? knots
            : this.generateUniformKnots(controlPoints.length, clampedDegree);

        if (knotVector.length < clampedDegree + 1) return; // 无效的节点向量

        this.basisCache.clear();
        this.resetStats();
        const start = (typeof performance !== 'undefined' ? performance.now() : Date.now());
        const rgba = this.parseColor(color);
        const samplePoints = [];
        const numSteps = Math.max(1, steps); // 防止除零错误

        // 计算控制点的边界框，用于检测无效点
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const pt of controlPoints) {
            minX = Math.min(minX, pt.x);
            minY = Math.min(minY, pt.y);
            maxX = Math.max(maxX, pt.x);
            maxY = Math.max(maxY, pt.y);
        }
        const hasValidControlPoints = isFinite(minX) && controlPoints.length > 0;

        for (let i = 0; i <= numSteps; i++) {
            const u = i / numSteps;
            const pt = this.evaluate(controlPoints, clampedDegree, knotVector, u);
            // 过滤无效点：如果点是 (0,0) 且控制点不在原点，说明计算错误
            const isInvalid = (pt.x === 0 && pt.y === 0) && hasValidControlPoints && 
                             (minX !== 0 || minY !== 0 || maxX !== 0 || maxY !== 0);
            if (!isInvalid) {
                samplePoints.push(pt);
            }
        }

        // 只绘制有效的线段
        for (let i = 1; i < samplePoints.length; i++) {
            this.drawSegment(samplePoints[i - 1], samplePoints[i], lineWidth, rgba, renderer);
        }

        const end = (typeof performance !== 'undefined' ? performance.now() : Date.now());
        this.stats.executionTime = end - start;
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

    evaluate(controlPoints, degree, knots, tNorm) {
        if (controlPoints.length === 0) {
            return { x: 0, y: 0 };
        }
        if (controlPoints.length === 1) {
            return { x: controlPoints[0].x, y: controlPoints[0].y };
        }
        if (knots.length < degree + 1) {
            return { x: 0, y: 0 };
        }
        const domainStart = knots[degree];
        const domainEnd = knots[knots.length - degree - 1];
        const t = domainStart + tNorm * (domainEnd - domainStart);
        const lastKnot = knots[knots.length - 1];
        const clampedT = Math.min(Math.max(t, knots[degree]), lastKnot);

        let point = { x: 0, y: 0 };
        for (let i = 0; i < controlPoints.length; i++) {
            const basis = this.basisFunction(i, degree, clampedT, knots);
            point.x += basis * controlPoints[i].x;
            point.y += basis * controlPoints[i].y;
        }
        return point;
    }

    basisFunction(i, k, t, knots) {
        const cacheKey = `${i}-${k}-${t.toFixed(4)}`;
        if (this.basisCache.has(cacheKey)) {
            return this.basisCache.get(cacheKey);
        }

        let value = 0;
        if (k === 0) {
            const inRange = (knots[i] <= t && t < knots[i + 1]) ||
                (t === knots[knots.length - 1] && i === knots.length - 2);
            value = inRange ? 1 : 0;
        } else {
            const denom1 = knots[i + k] - knots[i];
            const denom2 = knots[i + k + 1] - knots[i + 1];

            const term1 = denom1 === 0 ? 0 :
                ((t - knots[i]) / denom1) * this.basisFunction(i, k - 1, t, knots);
            const term2 = denom2 === 0 ? 0 :
                ((knots[i + k + 1] - t) / denom2) * this.basisFunction(i + 1, k - 1, t, knots);

            value = term1 + term2;
        }

        this.basisCache.set(cacheKey, value);
        return value;
    }

    drawSegment(p0, p1, lineWidth, rgba, renderer) {
        const dx = p1.x - p0.x;
        const dy = p1.y - p0.y;
        const steps = Math.max(Math.abs(dx), Math.abs(dy));
        if (steps === 0) {
            this.drawThickPixel(Math.round(p0.x), Math.round(p0.y), lineWidth, rgba, renderer);
            return;
        }

        for (let i = 0; i <= steps; i++) {
            const ratio = i / steps;
            const x = p0.x + dx * ratio;
            const y = p0.y + dy * ratio;
            this.drawThickPixel(Math.round(x), Math.round(y), lineWidth, rgba, renderer);
        }
    }

    drawThickPixel(cx, cy, lineWidth, rgba, renderer) {
        const radius = Math.max(1, Math.ceil(lineWidth / 2));
        for (let dx = -radius; dx <= radius; dx++) {
            for (let dy = -radius; dy <= radius; dy++) {
                renderer.setPixel(cx + dx, cy + dy, rgba.r, rgba.g, rgba.b, rgba.a);
                this.stats.pixelCount++;
            }
        }
    }
}

export default BSplineCurveAlgorithm;


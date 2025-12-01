/**
 * 三次（及更高阶）Bézier 曲线光栅化算法
 * 通过 de Casteljau 递推采样，再用简单线段插值到像素网格
 */

import { BaseAlgorithm } from '../base.js';

export class BezierCurveAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Bezier Curve', 'de Casteljau 曲线采样');
    }

    /**
     * 执行算法
     * @param {Object} params
     * @param {Array<{x:number,y:number}>} params.controlPoints
     * @param {number} params.steps
     * @param {string} params.color
     * @param {number} params.lineWidth
     * @param {Object} renderer
     */
    execute(params, renderer) {
        const {
            controlPoints = [],
            steps = 64,
            color = '#000000',
            lineWidth = 2
        } = params || {};

        if (!renderer || controlPoints.length < 2) {
            return;
        }

        this.resetStats();
        const start = (typeof performance !== 'undefined' ? performance.now() : Date.now());
        const rgba = this.parseColor(color);
        const samplePoints = [];

        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            samplePoints.push(this.evaluate(controlPoints, t));
        }

        for (let i = 1; i < samplePoints.length; i++) {
            this.drawSegment(samplePoints[i - 1], samplePoints[i], lineWidth, rgba, renderer);
        }

        const end = (typeof performance !== 'undefined' ? performance.now() : Date.now());
        this.stats.executionTime = end - start;
    }

    /**
     * de Casteljau 递推
     * @param {Array<{x:number,y:number}>} controlPoints
     * @param {number} t
     * @returns {{x:number,y:number}}
     */
    evaluate(controlPoints, t) {
        let points = controlPoints.map(p => ({ x: p.x, y: p.y }));
        const n = points.length - 1;
        for (let r = 1; r <= n; r++) {
            for (let i = 0; i <= n - r; i++) {
                points[i] = {
                    x: (1 - t) * points[i].x + t * points[i + 1].x,
                    y: (1 - t) * points[i].y + t * points[i + 1].y
                };
            }
        }
        return points[0];
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

export default BezierCurveAlgorithm;


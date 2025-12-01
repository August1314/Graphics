/**
 * 双三次 Bézier 曲面光栅化算法
 * 使用张量积 Bernstein 基函数在参数域上采样，生成网格线或三角形片元
 */

import { BaseAlgorithm } from '../base.js';
import { ScanlineFillAlgorithm } from '../fill/scanline.js';

export class BezierSurfaceAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Bezier Surface', '双三次 Bézier 曲面采样与填充');
        this.fillAlgorithm = new ScanlineFillAlgorithm();
    }

    /**
     * 执行算法
     * @param {Object} params
     * @param {Array<Array<{x:number,y:number}>>} params.controlGrid 4x4 控制点
     * @param {number} params.stepsU  u 方向细分
     * @param {number} params.stepsV  v 方向细分
     * @param {string} params.mode    'grid' | 'fill'
     * @param {string} params.strokeColor
     * @param {string} params.fillColor
     * @param {Object} renderer       PixelRenderer
     */
    execute(params, renderer) {
        const {
            controlGrid,
            stepsU = 12,
            stepsV = 12,
            mode = 'grid',
            strokeColor = '#000000',
            fillColor = '#cccccc'
        } = params || {};

        if (!renderer || !Array.isArray(controlGrid) || controlGrid.length !== 4) {
            return;
        }

        this.resetStats();
        const start = (typeof performance !== 'undefined' ? performance.now() : Date.now());

        // 预采样所有点
        const surfacePoints = [];
        for (let i = 0; i <= stepsU; i++) {
            const u = i / stepsU;
            surfacePoints[i] = [];
            for (let j = 0; j <= stepsV; j++) {
                const v = j / stepsV;
                surfacePoints[i][j] = this.evaluate(controlGrid, u, v);
            }
        }

        const strokeRGBA = this.parseColor(strokeColor);
        const fillRGBA = this.parseColor(fillColor);

        if (mode === 'grid' || !fillColor) {
            // 仅绘制曲面网格线
            for (let i = 0; i <= stepsU; i++) {
                for (let j = 1; j <= stepsV; j++) {
                    this.drawSegment(surfacePoints[i][j - 1], surfacePoints[i][j], strokeRGBA, renderer);
                }
            }
            for (let j = 0; j <= stepsV; j++) {
                for (let i = 1; i <= stepsU; i++) {
                    this.drawSegment(surfacePoints[i - 1][j], surfacePoints[i][j], strokeRGBA, renderer);
                }
            }
        } else if (mode === 'fill') {
            // 填充每个小四边形 -> 两个三角形
            for (let i = 0; i < stepsU; i++) {
                for (let j = 0; j < stepsV; j++) {
                    const p00 = surfacePoints[i][j];
                    const p10 = surfacePoints[i + 1][j];
                    const p01 = surfacePoints[i][j + 1];
                    const p11 = surfacePoints[i + 1][j + 1];

                    this.fillTriangle(p00, p10, p11, fillRGBA, renderer);
                    this.fillTriangle(p00, p11, p01, fillRGBA, renderer);
                }
            }

            // 可选：再勾勒网格线增强结构感
            for (let i = 0; i <= stepsU; i++) {
                for (let j = 1; j <= stepsV; j++) {
                    this.drawSegment(surfacePoints[i][j - 1], surfacePoints[i][j], strokeRGBA, renderer);
                }
            }
            for (let j = 0; j <= stepsV; j++) {
                for (let i = 1; i <= stepsU; i++) {
                    this.drawSegment(surfacePoints[i - 1][j], surfacePoints[i][j], strokeRGBA, renderer);
                }
            }
        }

        const end = (typeof performance !== 'undefined' ? performance.now() : Date.now());
        this.stats.executionTime = end - start;
    }

    /**
     * 双三次 Bézier 曲面点
     */
    evaluate(controlGrid, u, v) {
        const Bu = this.bernstein3(u);
        const Bv = this.bernstein3(v);
        let x = 0;
        let y = 0;
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const b = Bu[i] * Bv[j];
                x += b * controlGrid[i][j].x;
                y += b * controlGrid[i][j].y;
            }
        }
        return { x, y };
    }

    bernstein3(t) {
        const it = 1 - t;
        return [
            it * it * it,
            3 * t * it * it,
            3 * t * t * it,
            t * t * t
        ];
    }

    drawSegment(p0, p1, rgba, renderer) {
        const dx = p1.x - p0.x;
        const dy = p1.y - p0.y;
        const steps = Math.max(Math.abs(dx), Math.abs(dy));
        if (steps === 0) {
            renderer.setPixel(Math.round(p0.x), Math.round(p0.y), rgba.r, rgba.g, rgba.b, rgba.a);
            this.stats.pixelCount++;
            return;
        }
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const x = p0.x + dx * t;
            const y = p0.y + dy * t;
            renderer.setPixel(Math.round(x), Math.round(y), rgba.r, rgba.g, rgba.b, rgba.a);
            this.stats.pixelCount++;
        }
    }

    fillTriangle(p0, p1, p2, rgba, renderer) {
        const vertices = [p0, p1, p2];
        const colorHex = this.rgbaToHex(rgba);
        this.fillAlgorithm.execute({ vertices, color: colorHex }, renderer);
        this.stats.pixelCount += this.fillAlgorithm.getStats().pixelCount || 0;
    }

    rgbaToHex({ r, g, b }) {
        const toHex = (v) => v.toString(16).padStart(2, '0');
        return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
    }
}

export default BezierSurfaceAlgorithm;



/**
 * 双三次 Bézier 曲面图形
 */

import { BaseShape } from './base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { BezierSurfaceAlgorithm } from '../algorithms/surface/bezier_patch.js';

export class BezierSurface extends BaseShape {
    /**
     * @param {Array<Array<{x:number,y:number}>>} controlGrid 4x4 控制点
     * @param {Object} properties
     */
    constructor(controlGrid, properties = {}) {
        super(properties.id, 'bezier_surface', properties);
        this.controlGrid = this.normalizeGrid(controlGrid);
        this.stepsU = properties.stepsU || 12;
        this.stepsV = properties.stepsV || 12;
        this.mode = properties.mode || 'grid'; // 'grid' | 'fill'
        this.showControlGrid = properties.showControlGrid !== false;
        this.useRasterization = properties.useRasterization !== false;

        this.cache = null;
        this.cacheValid = false;
        this.algorithm = new BezierSurfaceAlgorithm();
    }

    normalizeGrid(grid) {
        const result = [];
        for (let i = 0; i < 4; i++) {
            result[i] = [];
            for (let j = 0; j < 4; j++) {
                const g = (grid && grid[i] && grid[i][j]) || { x: 0, y: 0 };
                result[i][j] = { x: g.x, y: g.y };
            }
        }
        return result;
    }

    setControlPoint(i, j, x, y) {
        if (i < 0 || i >= 4 || j < 0 || j >= 4) return;
        this.controlGrid[i][j] = { x, y };
        this.cacheValid = false;
    }

    setFillColor(color) {
        super.setFillColor(color);
        this.cacheValid = false;
    }

    setMode(mode) {
        this.mode = mode;
        if (this.properties) {
            this.properties.mode = mode;
        }
        this.cacheValid = false;
    }

    getControlPoint(i, j) {
        if (i < 0 || i >= 4 || j < 0 || j >= 4) return null;
        return this.controlGrid[i][j];
    }

    /**
     * 命中测试控制点
     */
    hitTestControlPoint(x, y, tolerance = 10) {
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const p = this.controlGrid[i][j];
                const dx = p.x - x;
                const dy = p.y - y;
                if (dx * dx + dy * dy <= tolerance * tolerance) {
                    return { i, j };
                }
            }
        }
        return null;
    }

    render(ctx) {
        // 统一有效模式：显式为 fill 或者有非透明填充色时，强制按填充模式
        const hasFill = this.properties.fillColor && this.properties.fillColor !== 'transparent';
        const effectiveMode = (this.mode === 'fill' || hasFill) ? 'fill' : 'grid';
        this.mode = effectiveMode;
        if (this.properties) {
            this.properties.mode = effectiveMode;
        }
        if (effectiveMode === 'fill' && (!this.properties.fillColor || this.properties.fillColor === 'transparent')) {
            this.properties.fillColor = '#cccccc';
        }
        try {
            if (this.useRasterization) {
                this.renderWithAlgorithm(ctx);
            } else {
                this.renderWithCanvas(ctx);
            }
        } catch (error) {
            console.error('Bezier surface render failed, fallback to canvas:', error);
            this.renderWithCanvas(ctx);
        }

        if (this.showControlGrid || this.selected) {
            this.renderControlGrid(ctx);
        }

        this.renderSelection(ctx);
    }

    renderWithAlgorithm(ctx) {
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

        const localGrid = this.controlGrid.map(row =>
            row.map(p => ({ x: p.x - offsetX, y: p.y - offsetY }))
        );

        const fillForAlgo = this.mode === 'fill'
            ? (this.properties.fillColor && this.properties.fillColor !== 'transparent'
                ? this.properties.fillColor
                : '#cccccc')
            : undefined;

        this.algorithm.execute({
            controlGrid: localGrid,
            stepsU: this.stepsU,
            stepsV: this.stepsV,
            mode: this.mode,
            strokeColor: this.properties.strokeColor,
            fillColor: fillForAlgo
        }, renderer);

        renderer.endPixelMode();
        ctx.drawImage(this.cache, offsetX, offsetY);
        this.cacheValid = true;
    }

    renderWithCanvas(ctx) {
        // 使用 Canvas 路径近似绘制曲面，可选填充
        const stepsU = Math.max(1, this.stepsU);
        const stepsV = Math.max(1, this.stepsV);
        const strokeColor = this.properties.strokeColor || '#000000';
        const fillColor = this.mode === 'fill'
            ? (this.properties.fillColor && this.properties.fillColor !== 'transparent'
                ? this.properties.fillColor
                : '#cccccc')
            : null;

        // 预采样曲面点
        const surfacePoints = [];
        for (let i = 0; i <= stepsU; i++) {
            const u = i / stepsU;
            surfacePoints[i] = [];
            for (let j = 0; j <= stepsV; j++) {
                const v = j / stepsV;
                surfacePoints[i][j] = this.evaluateSurfacePoint(u, v);
            }
        }

        ctx.save();
        ctx.lineWidth = 1;
        ctx.strokeStyle = strokeColor;

        if (this.mode === 'fill' && fillColor) {
            ctx.fillStyle = fillColor;
            // 两个三角形填充一个小面片
            for (let i = 0; i < stepsU; i++) {
                for (let j = 0; j < stepsV; j++) {
                    const p00 = surfacePoints[i][j];
                    const p10 = surfacePoints[i + 1][j];
                    const p01 = surfacePoints[i][j + 1];
                    const p11 = surfacePoints[i + 1][j + 1];

                    // 三角形 p00-p10-p11
                    ctx.beginPath();
                    ctx.moveTo(p00.x, p00.y);
                    ctx.lineTo(p10.x, p10.y);
                    ctx.lineTo(p11.x, p11.y);
                    ctx.closePath();
                    ctx.fill();

                    // 三角形 p00-p11-p01
                    ctx.beginPath();
                    ctx.moveTo(p00.x, p00.y);
                    ctx.lineTo(p11.x, p11.y);
                    ctx.lineTo(p01.x, p01.y);
                    ctx.closePath();
                    ctx.fill();
                }
            }
        }

        // 勾勒网格线（fill 模式下也画，增加结构感）
        for (let i = 0; i <= stepsU; i++) {
            ctx.beginPath();
            for (let j = 0; j <= stepsV; j++) {
                const p = surfacePoints[i][j];
                if (j === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }
            ctx.stroke();
        }
        for (let j = 0; j <= stepsV; j++) {
            ctx.beginPath();
            for (let i = 0; i <= stepsU; i++) {
                const p = surfacePoints[i][j];
                if (i === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }
            ctx.stroke();
        }

        ctx.restore();
    }

    evaluateSurfacePoint(u, v) {
        const Bu = this.bernstein3(u);
        const Bv = this.bernstein3(v);
        let x = 0;
        let y = 0;
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const b = Bu[i] * Bv[j];
                x += b * this.controlGrid[i][j].x;
                y += b * this.controlGrid[i][j].y;
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

    renderControlGrid(ctx) {
        ctx.save();
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
        ctx.fillStyle = '#ffffff';

        // 行
        for (let i = 0; i < 4; i++) {
            ctx.beginPath();
            for (let j = 0; j < 4; j++) {
                const p = this.controlGrid[i][j];
                if (j === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }
            ctx.stroke();
        }

        // 列
        for (let j = 0; j < 4; j++) {
            ctx.beginPath();
            for (let i = 0; i < 4; i++) {
                const p = this.controlGrid[i][j];
                if (i === 0) ctx.moveTo(p.x, p.y);
                else ctx.lineTo(p.x, p.y);
            }
            ctx.stroke();
        }

        // 控制点
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const p = this.controlGrid[i][j];
                ctx.beginPath();
                ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            }
        }

        ctx.restore();
    }

    getBounds() {
        let minX = Infinity;
        let minY = Infinity;
        let maxX = -Infinity;
        let maxY = -Infinity;
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const p = this.controlGrid[i][j];
                minX = Math.min(minX, p.x);
                minY = Math.min(minY, p.y);
                maxX = Math.max(maxX, p.x);
                maxY = Math.max(maxY, p.y);
            }
        }
        if (!isFinite(minX)) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        const padding = 8;
        return {
            x: minX - padding,
            y: minY - padding,
            width: (maxX - minX) + padding * 2,
            height: (maxY - minY) + padding * 2
        };
    }

    setCenter(x, y) {
        const bounds = this.getBounds();
        const cx = bounds.x + bounds.width / 2;
        const cy = bounds.y + bounds.height / 2;
        const dx = x - cx;
        const dy = y - cy;
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                this.controlGrid[i][j].x += dx;
                this.controlGrid[i][j].y += dy;
            }
        }
        this.cacheValid = false;
    }

    rotate(angleRad, cx, cy) {
        const bounds = this.getBounds();
        const centerX = bounds.x + bounds.width / 2;
        const centerY = bounds.y + bounds.height / 2;
        const ox = cx !== undefined ? cx : centerX;
        const oy = cy !== undefined ? cy : centerY;
        const cosA = Math.cos(angleRad);
        const sinA = Math.sin(angleRad);
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const p = this.controlGrid[i][j];
                const dx = p.x - ox;
                const dy = p.y - oy;
                p.x = ox + dx * cosA - dy * sinA;
                p.y = oy + dx * sinA + dy * cosA;
            }
        }
        this.cacheValid = false;
    }

    scale(scaleX, scaleY, cx, cy) {
        const sy = scaleY !== undefined ? scaleY : scaleX;
        const bounds = this.getBounds();
        const centerX = bounds.x + bounds.width / 2;
        const centerY = bounds.y + bounds.height / 2;
        const ox = cx !== undefined ? cx : centerX;
        const oy = cy !== undefined ? cy : centerY;
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                const p = this.controlGrid[i][j];
                p.x = ox + (p.x - ox) * scaleX;
                p.y = oy + (p.y - oy) * sy;
            }
        }
        this.cacheValid = false;
    }

    contains(x, y) {
        // 对于曲面，使用更精确的检测：只检查是否点击了控制点或控制网格线附近
        // 这样可以避免因为边界框太大而误选
        const tolerance = 15; // 控制网格线点击容差
        
        // 先检查是否点击了控制点
        const controlHit = this.hitTestControlPoint(x, y, tolerance);
        if (controlHit) {
            return true;
        }
        
        // 检查是否点击了控制网格线附近
        for (let i = 0; i < 4; i++) {
            // 检查行（水平线）
            for (let j = 0; j < 3; j++) {
                const p1 = this.controlGrid[i][j];
                const p2 = this.controlGrid[i][j + 1];
                if (this.pointNearLine(x, y, p1.x, p1.y, p2.x, p2.y, tolerance)) {
                    return true;
                }
            }
            // 检查列（垂直线）
            if (i < 3) {
                for (let j = 0; j < 4; j++) {
                    const p1 = this.controlGrid[i][j];
                    const p2 = this.controlGrid[i + 1][j];
                    if (this.pointNearLine(x, y, p1.x, p1.y, p2.x, p2.y, tolerance)) {
                        return true;
                    }
                }
            }
        }
        
        // 如果都没有命中，返回 false（不选中）
        return false;
    }
    
    // 检查点是否在直线附近
    pointNearLine(px, py, x1, y1, x2, y2, tolerance) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const lengthSq = dx * dx + dy * dy;
        
        if (lengthSq === 0) {
            // 线段退化为点
            const distSq = (px - x1) * (px - x1) + (py - y1) * (py - y1);
            return distSq <= tolerance * tolerance;
        }
        
        // 计算点到线段的最近距离
        const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / lengthSq));
        const projX = x1 + t * dx;
        const projY = y1 + t * dy;
        const distSq = (px - projX) * (px - projX) + (py - projY) * (py - projY);
        
        return distSq <= tolerance * tolerance;
    }

    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                controlGrid: this.controlGrid.map(row => row.map(p => ({ x: p.x, y: p.y }))),
                stepsU: this.stepsU,
                stepsV: this.stepsV,
                mode: this.mode,
                showControlGrid: this.showControlGrid,
                useRasterization: this.useRasterization
            }
        };
    }

    static fromDict(data) {
        const props = data.properties || {};
        const surface = new BezierSurface(props.controlGrid, {
            ...props,
            id: data.id
        });
        surface.stepsU = props.stepsU || 12;
        surface.stepsV = props.stepsV || 12;
        surface.mode = props.mode || 'grid';
        surface.showControlGrid = props.showControlGrid !== false;
        surface.useRasterization = props.useRasterization !== false;
        surface.timestamp = data.timestamp;
        return surface;
    }
}

export default BezierSurface;



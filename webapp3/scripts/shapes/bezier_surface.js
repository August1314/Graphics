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

        this.algorithm.execute({
            controlGrid: localGrid,
            stepsU: this.stepsU,
            stepsV: this.stepsV,
            mode: this.mode,
            strokeColor: this.properties.strokeColor,
            fillColor: this.properties.fillColor && this.properties.fillColor !== 'transparent'
                ? this.properties.fillColor
                : null
        }, renderer);

        renderer.endPixelMode();
        ctx.drawImage(this.cache, offsetX, offsetY);
        this.cacheValid = true;
    }

    renderWithCanvas(ctx) {
        // 简单版本：只画控制网格
        this.renderControlGrid(ctx);
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
        const bounds = this.getBounds();
        return x >= bounds.x && x <= bounds.x + bounds.width &&
               y >= bounds.y && y <= bounds.y + bounds.height;
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



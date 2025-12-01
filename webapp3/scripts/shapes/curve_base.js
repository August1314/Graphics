/**
 * 曲线图形基类
 */

import { BaseShape } from './base.js';

export class CurveShapeBase extends BaseShape {
    constructor(type, controlPoints = [], properties = {}) {
        super(properties.id, type, properties);
        this.controlPoints = controlPoints.map(p => ({ x: p.x, y: p.y }));
        this.samples = properties.samples || 64;
        this.showControlPolygon = properties.showControlPolygon !== false;
        this.useRasterization = properties.useRasterization !== false;
        this.cache = null;
        this.cacheValid = false;
        this.lastStats = null;
    }

    setControlPoints(points) {
        this.controlPoints = points.map(p => ({ x: p.x, y: p.y }));
        this.invalidateCache();
    }

    updateControlPoint(index, x, y) {
        if (index < 0 || index >= this.controlPoints.length) return;
        this.controlPoints[index] = { x, y };
        this.invalidateCache();
    }

    addControlPoint(point) {
        this.controlPoints.push({ x: point.x, y: point.y });
        this.invalidateCache();
    }

    hitTestControlPoint(x, y, tolerance = 10) {
        for (let i = 0; i < this.controlPoints.length; i++) {
            const pt = this.controlPoints[i];
            const dx = pt.x - x;
            const dy = pt.y - y;
            if (dx * dx + dy * dy <= tolerance * tolerance) {
                return i;
            }
        }
        return -1;
    }

    getBounds() {
        if (this.controlPoints.length === 0) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        const stroke = Math.max(1, this.properties.strokeWidth || 1);
        let minX = this.controlPoints[0].x;
        let maxX = this.controlPoints[0].x;
        let minY = this.controlPoints[0].y;
        let maxY = this.controlPoints[0].y;
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

    setCenter(x, y) {
        const bounds = this.getBounds();
        const currentCenter = {
            x: bounds.x + bounds.width / 2,
            y: bounds.y + bounds.height / 2
        };
        const dx = x - currentCenter.x;
        const dy = y - currentCenter.y;
        this.controlPoints = this.controlPoints.map(pt => ({
            x: pt.x + dx,
            y: pt.y + dy
        }));
        this.invalidateCache();
    }

    contains(x, y) {
        const bounds = this.getBounds();
        return x >= bounds.x && x <= bounds.x + bounds.width &&
               y >= bounds.y && y <= bounds.y + bounds.height;
    }

    invalidateCache() {
        this.cacheValid = false;
    }

    renderControlPolygon(ctx) {
        if (!this.showControlPolygon || this.controlPoints.length === 0) return;
        ctx.save();
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(37, 99, 235, 0.6)';
        ctx.fillStyle = '#ffffff';
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        for (let i = 0; i < this.controlPoints.length; i++) {
            const pt = this.controlPoints[i];
            if (i === 0) {
                ctx.moveTo(pt.x, pt.y);
            } else {
                ctx.lineTo(pt.x, pt.y);
            }
        }
        ctx.stroke();
        ctx.setLineDash([]);

        for (const pt of this.controlPoints) {
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }

        ctx.restore();
    }

    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                controlPoints: this.controlPoints.map(pt => ({ ...pt })),
                samples: this.samples,
                showControlPolygon: this.showControlPolygon,
                useRasterization: this.useRasterization
            }
        };
    }
}

export default CurveShapeBase;


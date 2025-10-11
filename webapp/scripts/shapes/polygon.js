/**
 * 多边形图形类
 */

import { BaseShape } from './base.js';

export class Polygon extends BaseShape {
    constructor(points = [], properties = {}) {
        super(properties.id, 'polygon', properties);
        this.points = points; // [{x, y}, ...]
    }

    render(ctx) {
        if (this.points.length < 2) return;
        
        ctx.save();
        this.applyStyle(ctx);
        
        ctx.beginPath();
        ctx.moveTo(this.points[0].x, this.points[0].y);
        
        for (let i = 1; i < this.points.length; i++) {
            ctx.lineTo(this.points[i].x, this.points[i].y);
        }
        
        ctx.closePath();
        
        // 只在填充不是透明时才填充
        if (this.properties.fillColor && this.properties.fillColor !== 'transparent') {
            ctx.fill();
        }
        ctx.stroke();
        
        ctx.restore();
        this.renderSelection(ctx);
    }

    getBounds() {
        if (this.points.length === 0) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        
        let minX = this.points[0].x;
        let minY = this.points[0].y;
        let maxX = this.points[0].x;
        let maxY = this.points[0].y;
        
        for (const point of this.points) {
            minX = Math.min(minX, point.x);
            minY = Math.min(minY, point.y);
            maxX = Math.max(maxX, point.x);
            maxY = Math.max(maxY, point.y);
        }
        
        return {
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY
        };
    }

    setCenter(x, y) {
        const center = this.getCenter();
        const dx = x - center.x;
        const dy = y - center.y;
        
        this.points = this.points.map(p => ({
            x: p.x + dx,
            y: p.y + dy
        }));
    }

    setPolygon(points) {
        this.points = points;
    }

    addPoint(x, y) {
        this.points.push({ x, y });
    }

    contains(px, py) {
        // 使用射线法判断点是否在多边形内
        let inside = false;
        for (let i = 0, j = this.points.length - 1; i < this.points.length; j = i++) {
            const xi = this.points[i].x;
            const yi = this.points[i].y;
            const xj = this.points[j].x;
            const yj = this.points[j].y;
            
            const intersect = ((yi > py) !== (yj > py)) &&
                (px < (xj - xi) * (py - yi) / (yj - yi) + xi);
            if (intersect) inside = !inside;
        }
        return inside;
    }

    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                points: this.points.map(p => ({ x: p.x, y: p.y }))
            }
        };
    }

    static fromDict(data) {
        const props = data.properties;
        const polygon = new Polygon(
            props.points || [],
            { ...props, id: data.id }
        );
        polygon.timestamp = data.timestamp;
        return polygon;
    }
}

export default Polygon;

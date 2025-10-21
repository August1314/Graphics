/**
 * 多边形图形类
 */

import { BaseShape } from './base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { AlgorithmFactory } from '../algorithms/factory.js';

export class Polygon extends BaseShape {
    constructor(points = [], properties = {}) {
        super(properties.id, 'polygon', properties);
        this.points = points; // [{x, y}, ...]
        this.fillAlgorithm = properties.fillAlgorithm || 'scanline';
        this.useRasterization = properties.useRasterization !== false;
        
        // 调试：记录多边形创建
        console.log('Polygon created with points:', points, 'properties:', properties);
        console.trace('Polygon creation stack trace');
    }

    render(ctx) {
        // 至少需要2个点才能渲染
        if (!this.points || this.points.length < 2) {
            console.log('Polygon render skipped: not enough points', this.points?.length);
            return;
        }
        
        try {
            // 只有完整的多边形（至少3个点）才使用光栅化填充
            if (this.useRasterization && this.fillAlgorithm !== 'canvas' && 
                this.points.length >= 3 &&
                this.properties.fillColor && this.properties.fillColor !== 'transparent') {
                this.renderWithAlgorithm(ctx);
            } else {
                this.renderWithCanvas(ctx);
            }
        } catch (error) {
            console.error('Rasterization failed, falling back to Canvas API:', error);
            this.renderWithCanvas(ctx);
        }
        
        this.renderSelection(ctx);
    }
    
    /**
     * 使用光栅化算法渲染
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    renderWithAlgorithm(ctx) {
        // 检查是否有足够的点
        if (!this.points || this.points.length < 3) {
            return;
        }
        
        const renderer = new PixelRenderer(ctx.canvas);
        renderer.beginPixelMode();
        
        // 考虑设备像素比，将显示坐标转换为像素坐标
        const dpr = window.devicePixelRatio || 1;
        const pixelVertices = this.points.map(p => ({
            x: p.x * dpr,
            y: p.y * dpr
        }));
        
        console.log('Polygon render with algorithm, DPR:', dpr);
        console.log('Original vertices:', this.points);
        console.log('Pixel vertices:', pixelVertices);
        
        // 填充
        const fillAlgorithm = AlgorithmFactory.createFillAlgorithm(this.fillAlgorithm);
        fillAlgorithm.execute({
            vertices: pixelVertices,
            color: this.properties.fillColor
        }, renderer);
        
        renderer.endPixelMode();
        
        // 绘制边框（使用 Canvas API）
        ctx.save();
        ctx.strokeStyle = this.properties.strokeColor;
        ctx.lineWidth = this.properties.strokeWidth;
        ctx.beginPath();
        ctx.moveTo(this.points[0].x, this.points[0].y);
        for (let i = 1; i < this.points.length; i++) {
            if (this.points[i] && typeof this.points[i].x === 'number' && typeof this.points[i].y === 'number') {
                ctx.lineTo(this.points[i].x, this.points[i].y);
            }
        }
        ctx.closePath();
        ctx.stroke();
        ctx.restore();
    }
    
    /**
     * 使用 Canvas API 渲染
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    renderWithCanvas(ctx) {
        // 检查是否有足够的点
        if (!this.points || this.points.length < 2) {
            return;
        }
        
        // 检查第一个点是否有效
        if (!this.points[0] || typeof this.points[0].x !== 'number' || typeof this.points[0].y !== 'number') {
            console.warn('Polygon has invalid first point:', this.points[0]);
            return;
        }
        
        ctx.save();
        this.applyStyle(ctx);
        
        ctx.beginPath();
        ctx.moveTo(this.points[0].x, this.points[0].y);
        
        for (let i = 1; i < this.points.length; i++) {
            if (this.points[i] && typeof this.points[i].x === 'number' && typeof this.points[i].y === 'number') {
                ctx.lineTo(this.points[i].x, this.points[i].y);
            }
        }
        
        // 只有至少3个点时才闭合路径并填充
        if (this.points.length >= 3) {
            ctx.closePath();
            
            // 只在填充不是透明时才填充
            if (this.properties.fillColor && this.properties.fillColor !== 'transparent') {
                ctx.fill();
            }
        }
        
        ctx.stroke();
        
        ctx.restore();
    }
    
    /**
     * 设置填充算法
     * @param {string} algorithm - 算法名称
     */
    setFillAlgorithm(algorithm) {
        this.fillAlgorithm = algorithm;
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
                points: this.points.map(p => ({ x: p.x, y: p.y })),
                fillAlgorithm: this.fillAlgorithm,
                useRasterization: this.useRasterization
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

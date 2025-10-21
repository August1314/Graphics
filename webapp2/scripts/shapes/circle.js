/**
 * 圆形图形类
 */

import { BaseShape } from './base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { AlgorithmFactory } from '../algorithms/factory.js';

export class Circle extends BaseShape {
    constructor(cx, cy, radius, properties = {}) {
        super(properties.id, 'circle', properties);
        this.cx = cx;
        this.cy = cy;
        this.radius = radius;
        this.algorithm = properties.algorithm || 'midpoint';
        this.useRasterization = properties.useRasterization !== false;
        this.cache = null; // 缓存的离屏 Canvas
        this.cacheValid = false; // 缓存是否有效
    }

    render(ctx) {
        try {
            if (this.useRasterization && this.algorithm !== 'canvas') {
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
        // 计算边界和偏移
        const bounds = this.getBounds();
        const padding = Math.ceil((this.properties.strokeWidth || 2) / 2) + 2;
        const offsetX = bounds.x - padding;
        const offsetY = bounds.y - padding;
        
        // 如果缓存有效，直接使用缓存
        if (this.cacheValid && this.cache) {
            ctx.drawImage(this.cache, offsetX, offsetY);
            // 显示缓存统计信息
            if (window.DEBUG_MODE && this.lastStats) {
                if (window.updateDebugPanel) {
                    window.updateDebugPanel(this.lastStats);
                }
            }
            return;
        }
        
        // 创建离屏 Canvas 用于缓存
        const cacheWidth = Math.max(1, Math.ceil(bounds.width)) + padding * 2;
        const cacheHeight = Math.max(1, Math.ceil(bounds.height)) + padding * 2;
        
        if (!this.cache) {
            this.cache = document.createElement('canvas');
        }
        this.cache.width = cacheWidth;
        this.cache.height = cacheHeight;
        
        const renderer = new PixelRenderer(this.cache);
        renderer.beginPixelMode();
        
        // 调整坐标到缓存 Canvas 的本地坐标系
        const localCx = this.cx - offsetX;
        const localCy = this.cy - offsetY;
        
        const algorithm = AlgorithmFactory.createCircleAlgorithm(this.algorithm);
        
        // 填充
        if (this.properties.fillColor && this.properties.fillColor !== 'transparent') {
            algorithm.execute({
                cx: localCx,
                cy: localCy,
                radius: this.radius,
                color: this.properties.fillColor,
                fill: true
            }, renderer);
        }
        
        // 绘制轮廓
        algorithm.execute({
            cx: localCx,
            cy: localCy,
            radius: this.radius,
            color: this.properties.strokeColor,
            fill: false,
            lineWidth: this.properties.strokeWidth || 2
        }, renderer);
        
        renderer.endPixelMode();
        
        // 标记缓存有效
        this.cacheValid = true;
        
        // 绘制缓存到主 Canvas
        ctx.drawImage(this.cache, offsetX, offsetY);
        
        // 可选：显示统计信息
        if (window.DEBUG_MODE) {
            const stats = algorithm.getStats();
            stats.name = algorithm.name;
            this.lastStats = stats; // 保存统计信息
            console.log(`${algorithm.name}:`, stats);
            if (window.updateDebugPanel) {
                window.updateDebugPanel(stats);
            }
        }
    }
    
    /**
     * 使用 Canvas API 渲染
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    renderWithCanvas(ctx) {
        ctx.save();
        this.applyStyle(ctx);
        
        ctx.beginPath();
        ctx.arc(this.cx, this.cy, this.radius, 0, Math.PI * 2);
        
        // 只在填充不是透明时才填充
        if (this.properties.fillColor && this.properties.fillColor !== 'transparent') {
            ctx.fill();
        }
        ctx.stroke();
        
        ctx.restore();
    }
    
    /**
     * 设置算法
     * @param {string} algorithm - 算法名称
     */
    setAlgorithm(algorithm) {
        this.algorithm = algorithm;
        this.cacheValid = false; // 使缓存失效
    }
    
    /**
     * 设置描边颜色（重写以使缓存失效）
     */
    setStrokeColor(color) {
        super.setStrokeColor(color);
        this.cacheValid = false;
    }
    
    /**
     * 设置描边宽度（重写以使缓存失效）
     */
    setStrokeWidth(width) {
        super.setStrokeWidth(width);
        this.cacheValid = false;
    }
    
    /**
     * 设置填充颜色（重写以使缓存失效）
     */
    setFillColor(color) {
        super.setFillColor(color);
        this.cacheValid = false;
    }

    getBounds() {
        return {
            x: this.cx - this.radius,
            y: this.cy - this.radius,
            width: this.radius * 2,
            height: this.radius * 2
        };
    }

    getCenter() {
        return { x: this.cx, y: this.cy };
    }

    setCenter(x, y) {
        this.cx = x;
        this.cy = y;
    }

    setCenterRadius(cx, cy, radius) {
        this.cx = cx;
        this.cy = cy;
        this.radius = radius;
        this.cacheValid = false; // 使缓存失效
    }

    contains(px, py) {
        const distance = BaseShape.distance(this.cx, this.cy, px, py);
        return distance <= this.radius;
    }

    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                cx: this.cx,
                cy: this.cy,
                r: this.radius,
                algorithm: this.algorithm,
                useRasterization: this.useRasterization
            }
        };
    }

    static fromDict(data) {
        const props = data.properties;
        const circle = new Circle(
            props.cx, props.cy, props.r,
            { ...props, id: data.id }
        );
        circle.timestamp = data.timestamp;
        return circle;
    }
}

export default Circle;

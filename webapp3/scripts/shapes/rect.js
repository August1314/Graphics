/**
 * 矩形图形类
 */

import { BaseShape } from './base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { AlgorithmFactory } from '../algorithms/factory.js';

export class Rectangle extends BaseShape {
    constructor(x, y, width, height, properties = {}) {
        super(properties.id, 'rect', properties);
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.fillAlgorithm = properties.fillAlgorithm || 'scanline';
        this.useRasterization = properties.useRasterization !== false;
    }

    render(ctx) {
        try {
            if (this.useRasterization && this.fillAlgorithm !== 'canvas' && 
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
        const renderer = new PixelRenderer(ctx.canvas);
        renderer.beginPixelMode();
        
        // 构建矩形顶点
        const vertices = [
            { x: this.x, y: this.y },
            { x: this.x + this.width, y: this.y },
            { x: this.x + this.width, y: this.y + this.height },
            { x: this.x, y: this.y + this.height }
        ];
        
        // 填充
        const fillAlgorithm = AlgorithmFactory.createFillAlgorithm(this.fillAlgorithm);
        fillAlgorithm.execute({
            vertices: vertices,
            color: this.properties.fillColor
        }, renderer);
        
        renderer.endPixelMode();
        
        // 绘制边框（使用 Canvas API）
        ctx.save();
        ctx.strokeStyle = this.properties.strokeColor;
        ctx.lineWidth = this.properties.strokeWidth;
        ctx.strokeRect(this.x, this.y, this.width, this.height);
        ctx.restore();
    }
    
    /**
     * 使用 Canvas API 渲染
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    renderWithCanvas(ctx) {
        ctx.save();
        this.applyStyle(ctx);
        
        ctx.beginPath();
        ctx.rect(this.x, this.y, this.width, this.height);
        
        // 只在填充不是透明时才填充
        if (this.properties.fillColor && this.properties.fillColor !== 'transparent') {
            ctx.fill();
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
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    setCenter(x, y) {
        this.x = x - this.width / 2;
        this.y = y - this.height / 2;
    }

    setGeometry(x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    contains(px, py) {
        return px >= this.x && px <= this.x + this.width &&
               py >= this.y && py <= this.y + this.height;
    }

    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                x: this.x,
                y: this.y,
                width: this.width,
                height: this.height,
                fillAlgorithm: this.fillAlgorithm,
                useRasterization: this.useRasterization
            }
        };
    }

    static fromDict(data) {
        const props = data.properties;
        const rect = new Rectangle(
            props.x, props.y, props.width, props.height,
            { ...props, id: data.id }
        );
        rect.timestamp = data.timestamp;
        return rect;
    }
}

export default Rectangle;

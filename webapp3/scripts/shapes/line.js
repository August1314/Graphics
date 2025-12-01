/**
 * 线图形类
 */

import { BaseShape } from './base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { AlgorithmFactory } from '../algorithms/factory.js';

export class Line extends BaseShape {
    /**
     * 构造函数
     * @param {number} x1 - 起点 X 坐标
     * @param {number} y1 - 起点 Y 坐标
     * @param {number} x2 - 终点 X 坐标
     * @param {number} y2 - 终点 Y 坐标
     * @param {Object} properties - 其他属性
     */
    constructor(x1, y1, x2, y2, properties = {}) {
        super(properties.id, 'line', properties);
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
        this.algorithm = properties.algorithm || 'bresenham';
        this.useRasterization = properties.useRasterization !== false;
        this.cache = null; // 缓存的离屏 Canvas
        this.cacheValid = false; // 缓存是否有效
    }

    /**
     * 渲染线
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
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
        
        // 绘制选中状态
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
        const algorithm = AlgorithmFactory.createLineAlgorithm(this.algorithm);
        algorithm.execute({
            x1: this.x1 - offsetX,
            y1: this.y1 - offsetY,
            x2: this.x2 - offsetX,
            y2: this.y2 - offsetY,
            color: this.properties.strokeColor,
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
        ctx.moveTo(this.x1, this.y1);
        ctx.lineTo(this.x2, this.y2);
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
     * 获取边界框
     * @returns {Object} {x, y, width, height}
     */
    getBounds() {
        const minX = Math.min(this.x1, this.x2);
        const minY = Math.min(this.y1, this.y2);
        const maxX = Math.max(this.x1, this.x2);
        const maxY = Math.max(this.y1, this.y2);
        
        return {
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY
        };
    }

    /**
     * 设置中心点
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     */
    setCenter(x, y) {
        const center = this.getCenter();
        const dx = x - center.x;
        const dy = y - center.y;
        
        this.x1 += dx;
        this.y1 += dy;
        this.x2 += dx;
        this.y2 += dy;
    }

    /**
     * 设置端点
     * @param {number} x1 - 起点 X 坐标
     * @param {number} y1 - 起点 Y 坐标
     * @param {number} x2 - 终点 X 坐标
     * @param {number} y2 - 终点 Y 坐标
     */
    setPoints(x1, y1, x2, y2) {
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
        this.cacheValid = false; // 使缓存失效
    }

    /**
     * 判断点是否在图形内（线附近）
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     * @returns {boolean}
     */
    contains(x, y) {
        const distance = BaseShape.pointToLineDistance(
            x, y, this.x1, this.y1, this.x2, this.y2
        );
        const threshold = Math.max(5, this.properties.strokeWidth / 2 + 3);
        return distance <= threshold;
    }

    /**
     * 序列化为字典
     * @returns {Object}
     */
    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                x1: this.x1,
                y1: this.y1,
                x2: this.x2,
                y2: this.y2,
                algorithm: this.algorithm,
                useRasterization: this.useRasterization
            }
        };
    }

    /**
     * 从字典反序列化
     * @param {Object} data - 序列化数据
     * @returns {Line}
     */
    static fromDict(data) {
        const props = data.properties;
        const line = new Line(
            props.x1,
            props.y1,
            props.x2,
            props.y2,
            { ...props, id: data.id }
        );
        line.timestamp = data.timestamp;
        return line;
    }
}

export default Line;

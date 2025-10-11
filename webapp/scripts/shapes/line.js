/**
 * 线图形类
 */

import { BaseShape } from './base.js';

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
    }

    /**
     * 渲染线
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    render(ctx) {
        ctx.save();
        this.applyStyle(ctx);
        
        ctx.beginPath();
        ctx.moveTo(this.x1, this.y1);
        ctx.lineTo(this.x2, this.y2);
        ctx.stroke();
        
        ctx.restore();
        
        // 绘制选中状态
        this.renderSelection(ctx);
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
                y2: this.y2
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

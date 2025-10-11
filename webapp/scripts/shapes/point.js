/**
 * 点图形类
 */

import { BaseShape } from './base.js';

export class Point extends BaseShape {
    /**
     * 构造函数
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     * @param {number} radius - 半径
     * @param {Object} properties - 其他属性
     */
    constructor(x, y, radius = 3, properties = {}) {
        super(properties.id, 'point', properties);
        this.x = x;
        this.y = y;
        this.radius = radius;
    }

    /**
     * 渲染点
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    render(ctx) {
        ctx.save();
        this.applyStyle(ctx);
        
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
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
        return {
            x: this.x - this.radius,
            y: this.y - this.radius,
            width: this.radius * 2,
            height: this.radius * 2
        };
    }

    /**
     * 获取中心点
     * @returns {Object} {x, y}
     */
    getCenter() {
        return { x: this.x, y: this.y };
    }

    /**
     * 设置中心点
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     */
    setCenter(x, y) {
        this.x = x;
        this.y = y;
    }

    /**
     * 判断点是否在图形内
     * @param {number} px - X 坐标
     * @param {number} py - Y 坐标
     * @returns {boolean}
     */
    contains(px, py) {
        const distance = BaseShape.distance(this.x, this.y, px, py);
        return distance <= this.radius + this.properties.strokeWidth / 2;
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
                x: this.x,
                y: this.y,
                radius: this.radius
            }
        };
    }

    /**
     * 从字典反序列化
     * @param {Object} data - 序列化数据
     * @returns {Point}
     */
    static fromDict(data) {
        const props = data.properties;
        const point = new Point(
            props.x,
            props.y,
            props.radius,
            { ...props, id: data.id }
        );
        point.timestamp = data.timestamp;
        return point;
    }
}

export default Point;

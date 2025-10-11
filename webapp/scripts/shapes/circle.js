/**
 * 圆形图形类
 */

import { BaseShape } from './base.js';

export class Circle extends BaseShape {
    constructor(cx, cy, radius, properties = {}) {
        super(properties.id, 'circle', properties);
        this.cx = cx;
        this.cy = cy;
        this.radius = radius;
    }

    render(ctx) {
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
        this.renderSelection(ctx);
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
                r: this.radius
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

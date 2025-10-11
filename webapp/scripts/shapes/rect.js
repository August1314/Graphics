/**
 * 矩形图形类
 */

import { BaseShape } from './base.js';

export class Rectangle extends BaseShape {
    constructor(x, y, width, height, properties = {}) {
        super(properties.id, 'rect', properties);
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    render(ctx) {
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
        this.renderSelection(ctx);
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
                height: this.height
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

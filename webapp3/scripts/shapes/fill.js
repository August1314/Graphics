/**
 * 填充图形
 * 保存填充操作的结果
 */

import { BaseShape } from './base.js';

export class FillShape extends BaseShape {
    constructor(imageData, x, y, width, height, properties = {}) {
        super(properties.id, 'fill', properties);
        this.imageData = imageData;  // 保存填充后的像素数据
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    render(ctx) {
        // 直接绘制保存的像素数据
        if (this.imageData) {
            ctx.putImageData(this.imageData, this.x, this.y);
        }
    }

    contains(x, y) {
        // 填充图形不支持选择
        return false;
    }

    getBounds() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    toDict() {
        // 填充图形不支持序列化（像素数据太大）
        return {
            ...super.toDict(),
            type: 'fill',
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }

    static fromDict(dict) {
        // 填充图形不支持反序列化
        return null;
    }
}

export default FillShape;

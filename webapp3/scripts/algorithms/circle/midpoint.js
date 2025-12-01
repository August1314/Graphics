/**
 * 中点画圆算法
 * 使用八对称性和中点判别绘制圆形
 */

import { BaseAlgorithm } from '../base.js';

export class MidpointCircleAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Midpoint Circle', '中点画圆算法（八对称性）');
    }
    
    /**
     * 执行中点画圆算法
     * @param {Object} params - 参数对象
     * @param {number} params.cx - 圆心 X 坐标
     * @param {number} params.cy - 圆心 Y 坐标
     * @param {number} params.radius - 半径
     * @param {string} params.color - 颜色（十六进制格式）
     * @param {boolean} params.fill - 是否填充
     * @param {Object} renderer - 像素渲染器
     */
    execute({ cx, cy, radius, color, fill, lineWidth = 1 }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        // 转换为整数
        const centerX = Math.round(cx);
        const centerY = Math.round(cy);
        const r_int = Math.round(radius);
        
        if (fill) {
            // 填充圆形
            pixelCount = this.fillCircle(centerX, centerY, r_int, r, g, b, a, renderer);
        } else {
            // 绘制圆形轮廓
            pixelCount = this.drawCircleOutline(centerX, centerY, r_int, r, g, b, a, renderer, lineWidth);
        }
        
        // 更新统计信息
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    /**
     * 绘制圆形轮廓
     */
    drawCircleOutline(cx, cy, radius, r, g, b, a, renderer, lineWidth = 1) {
        let pixelCount = 0;
        let x = 0;
        let y = radius;
        let d = 1 - radius;
        
        // 绘制初始八个对称点
        pixelCount += this.plot8Points(cx, cy, x, y, r, g, b, a, renderer, lineWidth);
        
        // 中点画圆主循环
        while (x < y) {
            if (d < 0) {
                d += 2 * x + 3;
            } else {
                d += 2 * (x - y) + 5;
                y--;
            }
            x++;
            pixelCount += this.plot8Points(cx, cy, x, y, r, g, b, a, renderer, lineWidth);
        }
        
        return pixelCount;
    }
    
    /**
     * 填充圆形
     */
    fillCircle(cx, cy, radius, r, g, b, a, renderer) {
        let pixelCount = 0;
        const radiusSq = radius * radius;
        
        // 使用扫描线填充
        for (let y = -radius; y <= radius; y++) {
            const width = Math.floor(Math.sqrt(radiusSq - y * y));
            for (let x = -width; x <= width; x++) {
                renderer.setPixel(cx + x, cy + y, r, g, b, a);
                pixelCount++;
            }
        }
        
        return pixelCount;
    }
    
    /**
     * 绘制八个对称点
     */
    plot8Points(cx, cy, x, y, r, g, b, a, renderer, lineWidth = 1) {
        let count = 0;
        if (lineWidth > 1) {
            const halfWidth = Math.floor(lineWidth / 2);
            for (let w = -halfWidth; w <= halfWidth; w++) {
                renderer.setPixel(cx + x, cy + y + w, r, g, b, a);
                renderer.setPixel(cx - x, cy + y + w, r, g, b, a);
                renderer.setPixel(cx + x, cy - y + w, r, g, b, a);
                renderer.setPixel(cx - x, cy - y + w, r, g, b, a);
                renderer.setPixel(cx + y + w, cy + x, r, g, b, a);
                renderer.setPixel(cx - y + w, cy + x, r, g, b, a);
                renderer.setPixel(cx + y + w, cy - x, r, g, b, a);
                renderer.setPixel(cx - y + w, cy - x, r, g, b, a);
                count += 8;
            }
        } else {
            renderer.setPixel(cx + x, cy + y, r, g, b, a);
            renderer.setPixel(cx - x, cy + y, r, g, b, a);
            renderer.setPixel(cx + x, cy - y, r, g, b, a);
            renderer.setPixel(cx - x, cy - y, r, g, b, a);
            renderer.setPixel(cx + y, cy + x, r, g, b, a);
            renderer.setPixel(cx - y, cy + x, r, g, b, a);
            renderer.setPixel(cx + y, cy - x, r, g, b, a);
            renderer.setPixel(cx - y, cy - x, r, g, b, a);
            count = 8;
        }
        return count;
    }
}

export default MidpointCircleAlgorithm;

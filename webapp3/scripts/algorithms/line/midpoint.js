/**
 * 中点画线算法
 * 使用中点判别绘制直线
 */

import { BaseAlgorithm } from '../base.js';

export class MidpointLineAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Midpoint Line', '中点画线算法（中点判别）');
    }
    
    /**
     * 执行中点画线算法
     * @param {Object} params - 参数对象
     * @param {number} params.x1 - 起点 X 坐标
     * @param {number} params.y1 - 起点 Y 坐标
     * @param {number} params.x2 - 终点 X 坐标
     * @param {number} params.y2 - 终点 Y 坐标
     * @param {string} params.color - 颜色（十六进制格式）
     * @param {Object} renderer - 像素渲染器
     */
    execute({ x1, y1, x2, y2, color, lineWidth = 1 }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        // 转换为整数坐标
        let x0 = Math.round(x1);
        let y0 = Math.round(y1);
        let x1_int = Math.round(x2);
        let y1_int = Math.round(y2);
        
        // 计算差值
        let dx = Math.abs(x1_int - x0);
        let dy = Math.abs(y1_int - y0);
        let sx = x0 < x1_int ? 1 : -1;
        let sy = y0 < y1_int ? 1 : -1;
        
        // 判断斜率
        if (dx > dy) {
            // 斜率 < 1
            pixelCount = this.drawLowSlope(x0, y0, x1_int, y1_int, sx, sy, dx, dy, r, g, b, a, renderer, lineWidth);
        } else {
            // 斜率 >= 1
            pixelCount = this.drawHighSlope(x0, y0, x1_int, y1_int, sx, sy, dx, dy, r, g, b, a, renderer, lineWidth);
        }
        
        // 更新统计信息
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    /**
     * 绘制低斜率直线（斜率 < 1）
     */
    drawLowSlope(x0, y0, x1, y1, sx, sy, dx, dy, r, g, b, a, renderer, lineWidth) {
        let pixelCount = 0;
        let d = 2 * dy - dx;
        let y = y0;
        
        for (let x = x0; sx > 0 ? x <= x1 : x >= x1; x += sx) {
            if (lineWidth > 1) {
                const radius = Math.floor(lineWidth / 2);
                for (let dy = -radius; dy <= radius; dy++) {
                    for (let dx = -radius; dx <= radius; dx++) {
                        if (dx * dx + dy * dy <= radius * radius) {
                            renderer.setPixel(x + dx, y + dy, r, g, b, a);
                            pixelCount++;
                        }
                    }
                }
            } else {
                renderer.setPixel(x, y, r, g, b, a);
                pixelCount++;
            }
            
            if (d > 0) {
                y += sy;
                d -= 2 * dx;
            }
            d += 2 * dy;
        }
        
        return pixelCount;
    }
    
    /**
     * 绘制高斜率直线（斜率 >= 1）
     */
    drawHighSlope(x0, y0, x1, y1, sx, sy, dx, dy, r, g, b, a, renderer, lineWidth) {
        let pixelCount = 0;
        let d = 2 * dx - dy;
        let x = x0;
        
        for (let y = y0; sy > 0 ? y <= y1 : y >= y1; y += sy) {
            if (lineWidth > 1) {
                const radius = Math.floor(lineWidth / 2);
                for (let dy = -radius; dy <= radius; dy++) {
                    for (let dx = -radius; dx <= radius; dx++) {
                        if (dx * dx + dy * dy <= radius * radius) {
                            renderer.setPixel(x + dx, y + dy, r, g, b, a);
                            pixelCount++;
                        }
                    }
                }
            } else {
                renderer.setPixel(x, y, r, g, b, a);
                pixelCount++;
            }
            
            if (d > 0) {
                x += sx;
                d -= 2 * dy;
            }
            d += 2 * dx;
        }
        
        return pixelCount;
    }
}

export default MidpointLineAlgorithm;

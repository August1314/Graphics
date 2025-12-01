/**
 * Bresenham 直线算法
 * 使用整数运算绘制直线，高效且精确
 */

import { BaseAlgorithm } from '../base.js';

export class BresenhamLineAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Bresenham', 'Bresenham 直线算法（整数运算，高效）');
    }
    
    /**
     * 执行 Bresenham 算法绘制直线
     * @param {Object} params - 参数对象
     * @param {number} params.x1 - 起点 X 坐标
     * @param {number} params.y1 - 起点 Y 坐标
     * @param {number} params.x2 - 终点 X 坐标
     * @param {number} params.y2 - 终点 Y 坐标
     * @param {string} params.color - 颜色（十六进制格式）
     * @param {number} params.lineWidth - 线宽
     * @param {Object} renderer - 像素渲染器
     */
    execute({ x1, y1, x2, y2, color, lineWidth = 1 }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        const { r, g, b, a } = this.parseColor(color);
        
        // 计算差值和方向
        let dx = Math.abs(x2 - x1);
        let dy = Math.abs(y2 - y1);
        let sx = x1 < x2 ? 1 : -1;
        let sy = y1 < y2 ? 1 : -1;
        let err = dx - dy;
        
        // 转换为整数坐标
        let x = Math.round(x1);
        let y = Math.round(y1);
        const endX = Math.round(x2);
        const endY = Math.round(y2);
        
        // Bresenham 主循环
        while (true) {
            // 绘制粗线（绘制一个圆形区域）
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
            
            // 到达终点
            if (x === endX && y === endY) break;
            
            // 计算误差并更新坐标
            const e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                x += sx;
            }
            if (e2 < dx) {
                err += dx;
                y += sy;
            }
        }
        
        // 更新统计信息
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
}

export default BresenhamLineAlgorithm;

/**
 * DDA (Digital Differential Analyzer) 直线算法
 * 使用增量计算绘制直线
 */

import { BaseAlgorithm } from '../base.js';

export class DDALineAlgorithm extends BaseAlgorithm {
    constructor() {
        super('DDA', 'DDA 直线算法（增量计算）');
    }
    
    /**
     * 执行 DDA 算法绘制直线
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
        
        // 计算差值
        const dx = x2 - x1;
        const dy = y2 - y1;
        
        // 确定步数（取较大的差值）
        const steps = Math.max(Math.abs(dx), Math.abs(dy));
        
        // 计算增量
        const xIncrement = dx / steps;
        const yIncrement = dy / steps;
        
        // 初始化坐标
        let x = x1;
        let y = y1;
        
        // DDA 主循环
        for (let i = 0; i <= steps; i++) {
            const px = Math.round(x);
            const py = Math.round(y);
            
            // 绘制粗线
            if (lineWidth > 1) {
                const radius = Math.floor(lineWidth / 2);
                for (let dy = -radius; dy <= radius; dy++) {
                    for (let dx = -radius; dx <= radius; dx++) {
                        if (dx * dx + dy * dy <= radius * radius) {
                            renderer.setPixel(px + dx, py + dy, r, g, b, a);
                            pixelCount++;
                        }
                    }
                }
            } else {
                renderer.setPixel(px, py, r, g, b, a);
                pixelCount++;
            }
            
            x += xIncrement;
            y += yIncrement;
        }
        
        // 更新统计信息
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
}

export default DDALineAlgorithm;

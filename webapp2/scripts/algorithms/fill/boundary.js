/**
 * 边界填充算法
 * 从种子点开始向外扩散填充
 */

import { BaseAlgorithm } from '../base.js';

export class BoundaryFillAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Boundary Fill', '边界填充算法（基于栈）');
    }
    
    /**
     * 解析颜色字符串为 RGBA（重写以添加错误处理）
     * @param {string} color - 十六进制颜色字符串
     * @returns {Object} RGBA 颜色对象
     */
    parseColor(color) {
        if (!color || typeof color !== 'string') {
            console.error('BoundaryFill parseColor received invalid color:', color);
            return { r: 255, g: 255, b: 255, a: 255 };
        }
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16) || 0,
            g: parseInt(hex.substr(2, 2), 16) || 0,
            b: parseInt(hex.substr(4, 2), 16) || 0,
            a: 255
        };
    }
    
    /**
     * 执行边界填充算法（种子填充模式）
     * @param {Object} params - 参数对象
     * @param {number} params.seedX - 种子点 X 坐标
     * @param {number} params.seedY - 种子点 Y 坐标
     * @param {string} params.fillColor - 填充颜色（十六进制格式）
     * @param {string} params.boundaryColor - 边界颜色（十六进制格式，可选）
     * @param {string} params.targetColor - 目标颜色（要替换的颜色，可选）
     * @param {Object} renderer - 像素渲染器
     */
    execute({ seedX, seedY, fillColor, boundaryColor, targetColor }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        console.log('BoundaryFill execute params:', { seedX, seedY, fillColor, boundaryColor, targetColor });
        
        const fill = this.parseColor(fillColor);
        console.log('Parsed fill color:', fill);
        
        // 如果提供了targetColor，使用种子填充模式（替换所有相同颜色）
        // 否则使用边界填充模式（遇到边界颜色停止）
        const useTargetMode = !!targetColor;
        console.log('Use target mode:', useTargetMode);
        
        const target = useTargetMode ? this.parseColor(targetColor) : null;
        console.log('Parsed target color:', target);
        
        const boundary = boundaryColor ? this.parseColor(boundaryColor) : null;
        console.log('Parsed boundary color:', boundary);
        
        const stack = [{ x: Math.round(seedX), y: Math.round(seedY) }];
        const visited = new Set();
        const maxIterations = 1000000; // 防止无限循环
        let iterations = 0;
        
        while (stack.length > 0 && iterations < maxIterations) {
            iterations++;
            const { x, y } = stack.pop();
            const key = `${x},${y}`;
            
            // 检查是否已访问
            if (visited.has(key)) continue;
            visited.add(key);
            
            // 获取当前像素颜色
            const pixel = renderer.getPixel(x, y);
            
            // 种子填充模式：只填充与目标颜色相同的像素
            if (useTargetMode) {
                if (!this.colorsEqual(pixel, target)) {
                    continue;
                }
            } else {
                // 边界填充模式：遇到边界颜色或已填充颜色停止
                if (this.colorsEqual(pixel, boundary) || this.colorsEqual(pixel, fill)) {
                    continue;
                }
            }
            
            // 填充当前像素
            renderer.setPixel(x, y, fill.r, fill.g, fill.b, fill.a);
            pixelCount++;
            
            // 添加四个方向的邻居
            stack.push({ x: x + 1, y });
            stack.push({ x: x - 1, y });
            stack.push({ x, y: y + 1 });
            stack.push({ x, y: y - 1 });
        }
        
        // 更新统计信息
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    /**
     * 比较两个颜色是否相等
     * @param {Object} c1 - 颜色1
     * @param {Object} c2 - 颜色2
     * @returns {boolean} 是否相等
     */
    colorsEqual(c1, c2) {
        return c1.r === c2.r && c1.g === c2.g && c1.b === c2.b && c1.a === c2.a;
    }
}

export default BoundaryFillAlgorithm;

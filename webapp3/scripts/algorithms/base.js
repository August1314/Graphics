/**
 * 算法基类
 * 所有光栅化算法的抽象基类
 */

export class BaseAlgorithm {
    /**
     * 构造函数
     * @param {string} name - 算法名称
     * @param {string} description - 算法描述
     */
    constructor(name, description) {
        this.name = name;
        this.description = description;
        this.stats = {
            pixelCount: 0,
            executionTime: 0
        };
    }
    
    /**
     * 执行算法（抽象方法，子类必须实现）
     * @param {Object} params - 算法参数
     * @param {Object} renderer - 像素渲染器
     */
    execute(params, renderer) {
        throw new Error('execute() must be implemented by subclass');
    }
    
    /**
     * 重置统计信息
     */
    resetStats() {
        this.stats = {
            pixelCount: 0,
            executionTime: 0
        };
    }
    
    /**
     * 获取统计信息
     * @returns {Object} 统计信息副本
     */
    getStats() {
        return { ...this.stats };
    }
    
    /**
     * 解析颜色字符串为 RGBA
     * @param {string} color - 十六进制颜色字符串
     * @returns {Object} RGBA 颜色对象
     */
    parseColor(color) {
        if (!color || typeof color !== 'string') {
            console.error('parseColor received invalid color:', color);
            return { r: 0, g: 0, b: 0, a: 255 };
        }
        const hex = color.replace('#', '');
        return {
            r: parseInt(hex.substr(0, 2), 16),
            g: parseInt(hex.substr(2, 2), 16),
            b: parseInt(hex.substr(4, 2), 16),
            a: 255
        };
    }
}

export default BaseAlgorithm;

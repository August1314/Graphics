/**
 * 参数验证器
 * 验证算法参数的有效性
 */

export class ParameterValidator {
    /**
     * 验证直线参数
     * @param {number} x1 - 起点 X 坐标
     * @param {number} y1 - 起点 Y 坐标
     * @param {number} x2 - 终点 X 坐标
     * @param {number} y2 - 终点 Y 坐标
     * @throws {Error} 如果参数无效
     */
    static validateLineParams(x1, y1, x2, y2) {
        if (!Number.isFinite(x1) || !Number.isFinite(y1) || 
            !Number.isFinite(x2) || !Number.isFinite(y2)) {
            throw new Error('Invalid line coordinates: coordinates must be finite numbers');
        }
    }
    
    /**
     * 验证圆形参数
     * @param {number} cx - 圆心 X 坐标
     * @param {number} cy - 圆心 Y 坐标
     * @param {number} radius - 半径
     * @throws {Error} 如果参数无效
     */
    static validateCircleParams(cx, cy, radius) {
        if (!Number.isFinite(cx) || !Number.isFinite(cy)) {
            throw new Error('Invalid circle center: coordinates must be finite numbers');
        }
        if (!Number.isFinite(radius) || radius < 0) {
            throw new Error('Invalid circle radius: radius must be a non-negative finite number');
        }
    }
    
    /**
     * 验证颜色格式
     * @param {string} color - 颜色字符串
     * @throws {Error} 如果颜色格式无效
     */
    static validateColor(color) {
        const hexRegex = /^#[0-9A-Fa-f]{6}$/;
        if (!hexRegex.test(color)) {
            throw new Error('Invalid color format: color must be in #RRGGBB format');
        }
    }
    
    /**
     * 验证多边形顶点
     * @param {Array} vertices - 顶点数组
     * @throws {Error} 如果顶点无效
     */
    static validatePolygonVertices(vertices) {
        if (!Array.isArray(vertices)) {
            throw new Error('Invalid vertices: vertices must be an array');
        }
        if (vertices.length < 3) {
            throw new Error('Invalid polygon: polygon must have at least 3 vertices');
        }
        for (const vertex of vertices) {
            if (!vertex || !Number.isFinite(vertex.x) || !Number.isFinite(vertex.y)) {
                throw new Error('Invalid vertex: each vertex must have finite x and y coordinates');
            }
        }
    }
    
    /**
     * 验证坐标范围
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     * @param {number} width - 画布宽度
     * @param {number} height - 画布高度
     * @returns {boolean} 坐标是否在范围内
     */
    static isInBounds(x, y, width, height) {
        return x >= 0 && x < width && y >= 0 && y < height;
    }
}

export default ParameterValidator;

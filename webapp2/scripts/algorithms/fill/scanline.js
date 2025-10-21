/**
 * 扫描线填充算法
 * 用于多边形填充
 */

import { BaseAlgorithm } from '../base.js';

export class ScanlineFillAlgorithm extends BaseAlgorithm {
    constructor() {
        super('Scanline Fill', '扫描线填充算法');
    }
    
    /**
     * 执行扫描线填充算法
     * @param {Object} params - 参数对象
     * @param {Array} params.vertices - 顶点数组 [{x, y}, ...]
     * @param {string} params.color - 填充颜色（十六进制格式）
     * @param {Object} renderer - 像素渲染器
     */
    execute({ vertices, color }, renderer) {
        const startTime = performance.now();
        let pixelCount = 0;
        
        if (!vertices || vertices.length < 3) {
            this.stats.executionTime = performance.now() - startTime;
            this.stats.pixelCount = 0;
            return;
        }
        
        const { r, g, b, a } = this.parseColor(color);
        
        // 构建边表
        const edges = this.buildEdgeTable(vertices);
        if (edges.length === 0) {
            this.stats.executionTime = performance.now() - startTime;
            this.stats.pixelCount = 0;
            return;
        }
        
        // 获取 Y 范围
        const minY = Math.min(...vertices.map(v => v.y));
        const maxY = Math.max(...vertices.map(v => v.y));
        
        // 扫描线填充
        for (let y = Math.ceil(minY); y <= Math.floor(maxY); y++) {
            const intersections = this.getIntersections(edges, y);
            intersections.sort((a, b) => a - b);
            
            // 填充交点对之间的像素
            for (let i = 0; i < intersections.length; i += 2) {
                if (i + 1 < intersections.length) {
                    const x1 = Math.ceil(intersections[i]);
                    const x2 = Math.floor(intersections[i + 1]);
                    for (let x = x1; x <= x2; x++) {
                        renderer.setPixel(x, y, r, g, b, a);
                        pixelCount++;
                    }
                }
            }
        }
        
        // 更新统计信息
        this.stats.executionTime = performance.now() - startTime;
        this.stats.pixelCount = pixelCount;
    }
    
    /**
     * 构建边表
     * @param {Array} vertices - 顶点数组
     * @returns {Array} 边表
     */
    buildEdgeTable(vertices) {
        const edges = [];
        const n = vertices.length;
        
        for (let i = 0; i < n; i++) {
            const v1 = vertices[i];
            const v2 = vertices[(i + 1) % n];
            
            // 跳过水平边
            if (v1.y === v2.y) continue;
            
            edges.push({
                yMin: Math.min(v1.y, v2.y),
                yMax: Math.max(v1.y, v2.y),
                x: v1.y < v2.y ? v1.x : v2.x,
                slope: (v2.x - v1.x) / (v2.y - v1.y)
            });
        }
        
        return edges;
    }
    
    /**
     * 获取扫描线与边的交点
     * @param {Array} edges - 边表
     * @param {number} y - 扫描线 Y 坐标
     * @returns {Array} 交点 X 坐标数组
     */
    getIntersections(edges, y) {
        const intersections = [];
        
        for (const edge of edges) {
            if (y >= edge.yMin && y < edge.yMax) {
                const x = edge.x + (y - edge.yMin) * edge.slope;
                intersections.push(x);
            }
        }
        
        return intersections;
    }
}

export default ScanlineFillAlgorithm;

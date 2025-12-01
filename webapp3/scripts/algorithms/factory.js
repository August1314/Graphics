/**
 * 算法工厂
 * 提供统一的算法实例创建接口
 */

import { BresenhamLineAlgorithm } from './line/bresenham.js';
import { DDALineAlgorithm } from './line/dda.js';
import { MidpointLineAlgorithm } from './line/midpoint.js';
import { MidpointCircleAlgorithm } from './circle/midpoint.js';
import { ScanlineFillAlgorithm } from './fill/scanline.js';
import { BoundaryFillAlgorithm } from './fill/boundary.js';
import { BezierCurveAlgorithm } from './curve/bezier.js';
import { BSplineCurveAlgorithm } from './curve/bspline.js';

export class AlgorithmFactory {
    static lineAlgorithms = {
        'bresenham': () => new BresenhamLineAlgorithm(),
        'dda': () => new DDALineAlgorithm(),
        'midpoint': () => new MidpointLineAlgorithm()
    };
    
    static circleAlgorithms = {
        'midpoint': () => new MidpointCircleAlgorithm()
    };
    
    static fillAlgorithms = {
        'scanline': () => new ScanlineFillAlgorithm(),
        'boundary': () => new BoundaryFillAlgorithm()
    };
    
    static curveAlgorithms = {
        'bezier': () => new BezierCurveAlgorithm(),
        'bspline': () => new BSplineCurveAlgorithm()
    };
    
    /**
     * 创建直线算法实例
     * @param {string} type - 算法类型
     * @returns {BaseAlgorithm} 算法实例
     */
    static createLineAlgorithm(type) {
        const factory = this.lineAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown line algorithm: ${type}`);
        }
        return factory();
    }
    
    /**
     * 创建圆形算法实例
     * @param {string} type - 算法类型
     * @returns {BaseAlgorithm} 算法实例
     */
    static createCircleAlgorithm(type) {
        const factory = this.circleAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown circle algorithm: ${type}`);
        }
        return factory();
    }
    
    /**
     * 创建填充算法实例
     * @param {string} type - 算法类型
     * @returns {BaseAlgorithm} 算法实例
     */
    static createFillAlgorithm(type) {
        const factory = this.fillAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown fill algorithm: ${type}`);
        }
        return factory();
    }

    /**
     * 创建曲线算法实例
     * @param {string} type
     * @returns {BaseAlgorithm}
     */
    static createCurveAlgorithm(type) {
        const factory = this.curveAlgorithms[type];
        if (!factory) {
            throw new Error(`Unknown curve algorithm: ${type}`);
        }
        return factory();
    }
}

export default AlgorithmFactory;

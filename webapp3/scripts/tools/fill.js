/**
 * 填充工具（油漆桶工具）
 * 点击封闭区域进行填充
 */

import { BaseTool } from './base.js';
import { PixelRenderer } from '../algorithms/renderer.js';
import { BoundaryFillAlgorithm } from '../algorithms/fill/boundary.js';
import CONFIG from '../config.js';

export class FillTool extends BaseTool {
    constructor() {
        super('fill');
        this.algorithm = 'boundary'; // 默认使用边界填充算法
        this.useRasterization = true; // 默认使用光栅化算法
        this.currentStyle = {
            fillColor: CONFIG.TOOLS.defaultFillColor,
            opacity: CONFIG.TOOLS.defaultOpacity
        };
    }

    setStyle(style) {
        this.currentStyle = { ...this.currentStyle, ...style };
    }

    setAlgorithm(algorithm) {
        this.algorithm = algorithm;
    }

    setUseRasterization(use) {
        this.useRasterization = use;
    }

    onMouseDown(x, y, event) {
        // 点击时立即执行填充
        console.log('Fill tool clicked at:', x, y);
        console.log('Fill color:', this.currentStyle.fillColor);
        console.log('Algorithm:', this.algorithm);
        console.log('Use rasterization:', this.useRasterization);
        this.fill(x, y);
    }

    onMouseMove(x, y, event) {
        // 填充工具不需要处理鼠标移动
    }

    onMouseUp(x, y, event) {
        // 填充工具不需要处理鼠标释放
    }

    /**
     * 执行填充操作
     * @param {number} x - 点击的 X 坐标
     * @param {number} y - 点击的 Y 坐标
     */
    fill(x, y) {
        if (this.useRasterization && this.algorithm === 'boundary') {
            this.fillWithBoundaryAlgorithm(x, y);
        } else {
            this.fillWithCanvasAPI(x, y);
        }
    }

    /**
     * 使用边界填充算法填充
     * @param {number} seedX - 种子点 X 坐标
     * @param {number} seedY - 种子点 Y 坐标
     */
    fillWithBoundaryAlgorithm(seedX, seedY) {
        console.log('fillWithBoundaryAlgorithm called:', seedX, seedY);

        // 触发填充开始事件，获取 canvas 和 document
        this.emit('fillStarted', { x: seedX, y: seedY });

        // 需要从外部获取 canvas 和 document 引用
        // 这里通过事件系统来实现
        const fillData = {
            seedX,
            seedY,
            fillColor: this.currentStyle.fillColor,
            algorithm: this.algorithm,
            callback: (canvas, document) => {
                console.log('Fill callback received canvas:', canvas);
                if (!canvas) {
                    console.error('无法获取 canvas 引用');
                    return;
                }

                try {
                    // 在填充前保存 canvas 快照（用于撤销）
                    const ctx = canvas.getContext('2d');
                    const canvasSnapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);

                    const renderer = new PixelRenderer(canvas);
                    renderer.beginPixelMode();

                    // 检查填充颜色是否有效
                    if (!this.currentStyle.fillColor || this.currentStyle.fillColor === 'transparent') {
                        renderer.endPixelMode();
                        console.log('填充颜色无效或为透明，无法填充');
                        alert('请先选择一个填充颜色，并取消勾选"透明"复选框');
                        return;
                    }

                    // 考虑设备像素比（DPI缩放）
                    const dpr = window.devicePixelRatio || 1;
                    const actualSeedX = Math.floor(seedX * dpr);
                    const actualSeedY = Math.floor(seedY * dpr);

                    console.log(`原始坐标: (${seedX}, ${seedY})`);
                    console.log(`设备像素比: ${dpr}`);
                    console.log(`实际像素坐标: (${actualSeedX}, ${actualSeedY})`);
                    console.log(`Canvas尺寸: ${canvas.width}x${canvas.height}`);

                    // 获取种子点的颜色（要替换的颜色）
                    const seedPixel = renderer.getPixel(actualSeedX, actualSeedY);
                    const targetColor = this.rgbToHex(seedPixel.r, seedPixel.g, seedPixel.b);

                    console.log(`种子点颜色: ${targetColor}`);
                    console.log(`填充颜色: ${this.currentStyle.fillColor}`);

                    // 如果点击的颜色和填充颜色相同，不需要填充
                    if (targetColor === this.currentStyle.fillColor) {
                        renderer.endPixelMode();
                        console.log('点击位置已经是目标颜色，无需填充');
                        return;
                    }

                    // 执行种子填充算法（填充所有与种子点颜色相同的连续区域）
                    const algorithm = new BoundaryFillAlgorithm();
                    algorithm.execute({
                        seedX: actualSeedX,
                        seedY: actualSeedY,
                        fillColor: this.currentStyle.fillColor,
                        targetColor: targetColor  // 要替换的颜色
                    }, renderer);

                    renderer.endPixelMode();

                    // 显示统计信息
                    const stats = algorithm.getStats();
                    console.log(`边界填充完成: ${stats.pixelCount} 像素, ${stats.executionTime.toFixed(2)}ms`);

                    // 查找被点击的图形
                    let targetShape = null;
                    if (document && document.shapes) {
                        // 从后往前查找（顶层图形优先）
                        for (let i = document.shapes.length - 1; i >= 0; i--) {
                            const shape = document.shapes[i];
                            if (shape.type !== 'fill' && shape.contains && shape.contains(seedX, seedY)) {
                                targetShape = shape;
                                console.log('找到目标图形:', shape.type, shape.id);
                                break;
                            }
                        }
                    }

                    // 如果找到了图形，修改其填充颜色
                    if (targetShape && targetShape.properties) {
                        const oldFillColor = targetShape.properties.fillColor;

                        // 使用 setFillColor 方法（如果存在），这样会使缓存失效
                        if (typeof targetShape.setFillColor === 'function') {
                            targetShape.setFillColor(this.currentStyle.fillColor);
                        } else {
                            targetShape.properties.fillColor = this.currentStyle.fillColor;
                        }

                        console.log(`修改图形填充颜色: ${oldFillColor} -> ${this.currentStyle.fillColor}`);

                        // 触发填充完成事件
                        this.emit('fillCompleted', {
                            stats,
                            targetShape: targetShape,
                            oldFillColor: oldFillColor,
                            newFillColor: this.currentStyle.fillColor
                        });
                    } else {
                        console.log('未找到目标图形，填充整个区域');
                        // 触发填充完成事件，传递快照用于撤销
                        this.emit('fillCompleted', {
                            stats,
                            seedX: actualSeedX,
                            seedY: actualSeedY,
                            fillColor: this.currentStyle.fillColor,
                            canvasSnapshot: canvasSnapshot,  // 填充前的快照
                            canvas: canvas  // canvas 引用
                        });
                    }
                } catch (error) {
                    console.error('填充失败:', error);
                    // 回退到 Canvas API
                    this.fillWithCanvasAPI(seedX, seedY);
                }
            }
        };

        this.emit('fillRequested', fillData);
    }

    /**
     * 使用 Canvas API 填充（回退方案）
     * @param {number} x - 点击的 X 坐标
     * @param {number} y - 点击的 Y 坐标
     */
    fillWithCanvasAPI(x, y) {
        console.log('使用 Canvas API 填充（暂未实现完整功能）');
        // Canvas API 的填充需要配合图形对象
        // 这里可以实现一个简单的像素填充
        this.emit('fillWithCanvas', { x, y, fillColor: this.currentStyle.fillColor });
    }

    /**
     * RGB 转十六进制颜色
     * @param {number} r - 红色分量
     * @param {number} g - 绿色分量
     * @param {number} b - 蓝色分量
     * @returns {string} 十六进制颜色字符串
     */
    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    }

    cancel() {
        // 填充工具没有需要取消的操作
    }
}

export default FillTool;

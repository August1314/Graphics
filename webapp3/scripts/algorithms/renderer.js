/**
 * 像素渲染器
 * 负责像素级操作，提供统一的像素绘制接口
 */

export class PixelRenderer {
    /**
     * 构造函数
     * @param {HTMLCanvasElement} canvas - Canvas 元素
     * @param {boolean} useDevicePixelRatio - 是否使用设备像素比（默认 false，离屏 Canvas 不需要）
     */
    constructor(canvas, useDevicePixelRatio = false) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d', { willReadFrequently: true });
        this.imageData = null;
        this.width = 0;
        this.height = 0;
        // 只有主 Canvas 才需要考虑 DPR，离屏 Canvas 不需要
        this.dpr = useDevicePixelRatio ? (window.devicePixelRatio || 1) : 1;
    }
    
    /**
     * 开始批量像素操作
     */
    beginPixelMode() {
        // 使用物理像素尺寸
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        // 获取逻辑尺寸用于坐标转换
        this.logicalWidth = this.canvas.width / this.dpr;
        this.logicalHeight = this.canvas.height / this.dpr;
        this.imageData = this.ctx.getImageData(0, 0, this.width, this.height);
    }
    
    /**
     * 设置单个像素
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     * @param {number} r - 红色分量 (0-255)
     * @param {number} g - 绿色分量 (0-255)
     * @param {number} b - 蓝色分量 (0-255)
     * @param {number} a - Alpha 分量 (0-255)
     */
    setPixel(x, y, r, g, b, a = 255) {
        // 对于离屏 Canvas (dpr=1)，直接使用坐标
        // 对于主 Canvas，需要转换为物理像素坐标
        const physicalX = Math.floor(x * this.dpr);
        const physicalY = Math.floor(y * this.dpr);
        
        // 边界检查
        if (physicalX < 0 || physicalX >= this.width || physicalY < 0 || physicalY >= this.height) {
            return;
        }
        
        const index = (physicalY * this.width + physicalX) * 4;
        this.imageData.data[index] = r;
        this.imageData.data[index + 1] = g;
        this.imageData.data[index + 2] = b;
        this.imageData.data[index + 3] = a;
    }
    
    /**
     * 获取像素颜色
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     * @returns {Object} RGBA 颜色对象
     */
    getPixel(x, y) {
        // 对于离屏 Canvas (dpr=1)，直接使用坐标
        // 对于主 Canvas，需要转换为物理像素坐标
        const physicalX = Math.floor(x * this.dpr);
        const physicalY = Math.floor(y * this.dpr);
        
        // 边界检查
        if (physicalX < 0 || physicalX >= this.width || physicalY < 0 || physicalY >= this.height) {
            return { r: 0, g: 0, b: 0, a: 0 };
        }
        
        const index = (physicalY * this.width + physicalX) * 4;
        return {
            r: this.imageData.data[index],
            g: this.imageData.data[index + 1],
            b: this.imageData.data[index + 2],
            a: this.imageData.data[index + 3]
        };
    }
    
    /**
     * 结束批量像素操作并更新画布
     */
    endPixelMode() {
        if (this.imageData) {
            this.ctx.putImageData(this.imageData, 0, 0);
            this.imageData = null;
        }
    }
    
    /**
     * 清空画布
     */
    clear() {
        this.ctx.clearRect(0, 0, this.width, this.height);
    }
}

export default PixelRenderer;

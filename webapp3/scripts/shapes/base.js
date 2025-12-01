/**
 * 基础图形类
 * 所有图形的抽象基类
 */

export class BaseShape {
    /**
     * 构造函数
     * @param {string} id - 图形唯一标识
     * @param {string} type - 图形类型
     * @param {Object} properties - 图形属性
     */
    constructor(id, type, properties = {}) {
        this.id = id || this.generateId();
        this.type = type;
        this.properties = {
            strokeColor: '#000000',
            strokeWidth: 2,
            strokeStyle: 'solid',
            fillColor: '#FFFFFF',
            opacity: 1.0,
            ...properties
        };
        this.timestamp = Date.now();
        this.selected = false;
    }

    /**
     * 生成唯一 ID
     * @returns {string} UUID
     */
    generateId() {
        return 'shape_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * 渲染图形（抽象方法，子类必须实现）
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    render(ctx) {
        throw new Error('render() 方法必须在子类中实现');
    }

    /**
     * 获取边界框
     * @returns {Object} {x, y, width, height}
     */
    getBounds() {
        throw new Error('getBounds() 方法必须在子类中实现');
    }

    /**
     * 获取中心点
     * @returns {Object} {x, y}
     */
    getCenter() {
        const bounds = this.getBounds();
        return {
            x: bounds.x + bounds.width / 2,
            y: bounds.y + bounds.height / 2
        };
    }

    /**
     * 设置中心点
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     */
    setCenter(x, y) {
        throw new Error('setCenter() 方法必须在子类中实现');
    }

    /**
     * 判断点是否在图形内
     * @param {number} x - X 坐标
     * @param {number} y - Y 坐标
     * @returns {boolean}
     */
    contains(x, y) {
        const bounds = this.getBounds();
        return x >= bounds.x && 
               x <= bounds.x + bounds.width &&
               y >= bounds.y && 
               y <= bounds.y + bounds.height;
    }

    /**
     * 设置描边颜色
     * @param {string} color - 颜色值
     */
    setStrokeColor(color) {
        this.properties.strokeColor = color;
    }

    /**
     * 设置描边宽度
     * @param {number} width - 宽度值
     */
    setStrokeWidth(width) {
        this.properties.strokeWidth = Math.max(0.5, width);
    }

    /**
     * 设置描边样式
     * @param {string} style - 样式 ('solid', 'dashed', 'dotted')
     */
    setStrokeStyle(style) {
        this.properties.strokeStyle = style;
    }

    /**
     * 设置填充颜色
     * @param {string} color - 颜色值
     */
    setFillColor(color) {
        this.properties.fillColor = color;
    }

    /**
     * 设置透明度
     * @param {number} opacity - 透明度 (0-1)
     */
    setOpacity(opacity) {
        this.properties.opacity = Math.max(0, Math.min(1, opacity));
    }

    /**
     * 应用样式到 Canvas 上下文
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    applyStyle(ctx) {
        // 设置描边样式
        ctx.strokeStyle = this.properties.strokeColor;
        ctx.lineWidth = this.properties.strokeWidth;
        
        // 设置线条样式
        switch (this.properties.strokeStyle) {
            case 'dashed':
                ctx.setLineDash([10, 5]);
                break;
            case 'dotted':
                ctx.setLineDash([2, 3]);
                break;
            default:
                ctx.setLineDash([]);
        }
        
        // 设置填充样式
        ctx.fillStyle = this.properties.fillColor;
        
        // 设置透明度
        ctx.globalAlpha = this.properties.opacity;
        
        // 设置线条端点和连接样式
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
    }

    /**
     * 绘制选中状态
     * @param {CanvasRenderingContext2D} ctx - Canvas 上下文
     */
    renderSelection(ctx) {
        if (!this.selected) return;
        
        const bounds = this.getBounds();
        const padding = 5;
        
        ctx.save();
        ctx.strokeStyle = '#2563eb';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(
            bounds.x - padding,
            bounds.y - padding,
            bounds.width + padding * 2,
            bounds.height + padding * 2
        );
        ctx.restore();
    }

    /**
     * 设置选中状态
     * @param {boolean} selected - 是否选中
     */
    setSelected(selected) {
        this.selected = selected;
    }

    /**
     * 克隆图形
     * @returns {BaseShape} 克隆的图形
     */
    clone() {
        const data = this.toDict();
        data.id = this.generateId();
        return this.constructor.fromDict(data);
    }

    /**
     * 序列化为字典
     * @returns {Object} 序列化数据
     */
    toDict() {
        return {
            id: this.id,
            type: this.type,
            properties: { ...this.properties },
            timestamp: this.timestamp
        };
    }

    /**
     * 从字典反序列化（静态方法，子类需要实现）
     * @param {Object} data - 序列化数据
     * @returns {BaseShape} 图形实例
     */
    static fromDict(data) {
        throw new Error('fromDict() 静态方法必须在子类中实现');
    }

    /**
     * 移动图形
     * @param {number} dx - X 方向偏移
     * @param {number} dy - Y 方向偏移
     */
    move(dx, dy) {
        const center = this.getCenter();
        this.setCenter(center.x + dx, center.y + dy);
    }

    /**
     * 围绕给定中心旋转图形（默认实现为空，由子类按需重写）
     * @param {number} angleRad - 旋转角度（弧度）
     * @param {number} [cx] - 旋转中心 X
     * @param {number} [cy] - 旋转中心 Y
     */
    rotate(angleRad, cx, cy) {
        // 默认不做任何事，由具体图形类覆盖
    }

    /**
     * 围绕给定中心缩放图形（默认实现为空，由子类按需重写）
     * @param {number} scaleX - X 方向缩放系数
     * @param {number} [scaleY] - Y 方向缩放系数，默认等比缩放
     * @param {number} [cx] - 缩放中心 X
     * @param {number} [cy] - 缩放中心 Y
     */
    scale(scaleX, scaleY, cx, cy) {
        // 默认不做任何事，由具体图形类覆盖
    }

    /**
     * 获取图形信息（用于调试）
     * @returns {string}
     */
    toString() {
        return `${this.type} [${this.id}]`;
    }

    /**
     * 验证图形数据
     * @returns {boolean}
     */
    validate() {
        if (!this.id || !this.type) {
            return false;
        }
        
        if (!this.properties) {
            return false;
        }
        
        // 验证颜色格式
        const colorRegex = /^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$/;
        if (!colorRegex.test(this.properties.strokeColor) || 
            !colorRegex.test(this.properties.fillColor)) {
            return false;
        }
        
        // 验证数值范围
        if (this.properties.strokeWidth < 0 || 
            this.properties.opacity < 0 || 
            this.properties.opacity > 1) {
            return false;
        }
        
        return true;
    }

    /**
     * 计算两点之间的距离
     * @param {number} x1 - 点1 X坐标
     * @param {number} y1 - 点1 Y坐标
     * @param {number} x2 - 点2 X坐标
     * @param {number} y2 - 点2 Y坐标
     * @returns {number} 距离
     */
    static distance(x1, y1, x2, y2) {
        return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    }

    /**
     * 计算点到线段的距离
     * @param {number} px - 点 X坐标
     * @param {number} py - 点 Y坐标
     * @param {number} x1 - 线段起点 X坐标
     * @param {number} y1 - 线段起点 Y坐标
     * @param {number} x2 - 线段终点 X坐标
     * @param {number} y2 - 线段终点 Y坐标
     * @returns {number} 距离
     */
    static pointToLineDistance(px, py, x1, y1, x2, y2) {
        const A = px - x1;
        const B = py - y1;
        const C = x2 - x1;
        const D = y2 - y1;

        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        let param = -1;

        if (lenSq !== 0) {
            param = dot / lenSq;
        }

        let xx, yy;

        if (param < 0) {
            xx = x1;
            yy = y1;
        } else if (param > 1) {
            xx = x2;
            yy = y2;
        } else {
            xx = x1 + param * C;
            yy = y1 + param * D;
        }

        const dx = px - xx;
        const dy = py - yy;
        return Math.sqrt(dx * dx + dy * dy);
    }
}

export default BaseShape;

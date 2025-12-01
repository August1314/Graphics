/**
 * 画笔路径图形类
 */

import { BaseShape } from './base.js';

export class BrushPath extends BaseShape {
    constructor(points = [], brushType = 'pen', properties = {}) {
        super(properties.id, 'brush_path', properties);
        this.points = points; // [{x, y}, ...]
        this.brushType = brushType; // pen, marker, calligraphy, spray
        this.smoothing = properties.smoothing !== undefined ? properties.smoothing : true;
    }

    render(ctx) {
        if (this.points.length < 2) return;
        
        ctx.save();
        this.applyStyle(ctx);
        
        // 根据画笔类型调整样式
        this.applyBrushStyle(ctx);
        
        ctx.beginPath();
        
        if (this.smoothing && this.points.length >= 3) {
            // 使用平滑曲线
            this.renderSmooth(ctx);
        } else {
            // 直接连线
            this.renderDirect(ctx);
        }
        
        ctx.stroke();
        ctx.restore();
        
        this.renderSelection(ctx);
    }

    applyBrushStyle(ctx) {
        switch (this.brushType) {
            case 'marker':
                ctx.lineCap = 'square';
                ctx.lineJoin = 'miter';
                break;
            case 'calligraphy':
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
                // 书法笔可以有变化的宽度，这里简化处理
                break;
            case 'spray':
                // 喷枪效果需要特殊处理，这里简化
                ctx.globalAlpha = this.properties.opacity * 0.5;
                break;
            default: // pen
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';
        }
    }

    renderDirect(ctx) {
        ctx.moveTo(this.points[0].x, this.points[0].y);
        for (let i = 1; i < this.points.length; i++) {
            ctx.lineTo(this.points[i].x, this.points[i].y);
        }
    }

    renderSmooth(ctx) {
        ctx.moveTo(this.points[0].x, this.points[0].y);
        
        for (let i = 1; i < this.points.length - 1; i++) {
            const current = this.points[i];
            const next = this.points[i + 1];
            const controlX = (current.x + next.x) / 2;
            const controlY = (current.y + next.y) / 2;
            ctx.quadraticCurveTo(current.x, current.y, controlX, controlY);
        }
        
        // 最后一点
        const last = this.points[this.points.length - 1];
        ctx.lineTo(last.x, last.y);
    }

    getBounds() {
        if (this.points.length === 0) {
            return { x: 0, y: 0, width: 0, height: 0 };
        }
        
        let minX = this.points[0].x;
        let minY = this.points[0].y;
        let maxX = this.points[0].x;
        let maxY = this.points[0].y;
        
        for (const point of this.points) {
            minX = Math.min(minX, point.x);
            minY = Math.min(minY, point.y);
            maxX = Math.max(maxX, point.x);
            maxY = Math.max(maxY, point.y);
        }
        
        const padding = this.properties.strokeWidth / 2;
        return {
            x: minX - padding,
            y: minY - padding,
            width: maxX - minX + padding * 2,
            height: maxY - minY + padding * 2
        };
    }

    setCenter(x, y) {
        const center = this.getCenter();
        const dx = x - center.x;
        const dy = y - center.y;
        
        this.points = this.points.map(p => ({
            x: p.x + dx,
            y: p.y + dy
        }));
    }

    addPoint(x, y) {
        this.points.push({ x, y });
    }

    /**
     * 平滑路径（贝塞尔曲线）
     */
    smooth() {
        if (this.points.length < 3) return;
        this.smoothing = true;
    }

    /**
     * 简化路径（道格拉斯-普克算法）
     * @param {number} tolerance - 容差
     */
    simplify(tolerance = 1.0) {
        if (this.points.length < 3) return;
        
        this.points = this.douglasPeucker(this.points, tolerance);
    }

    douglasPeucker(points, tolerance) {
        if (points.length <= 2) return points;
        
        // 找到距离起点和终点连线最远的点
        let maxDistance = 0;
        let maxIndex = 0;
        const start = points[0];
        const end = points[points.length - 1];
        
        for (let i = 1; i < points.length - 1; i++) {
            const distance = BaseShape.pointToLineDistance(
                points[i].x, points[i].y,
                start.x, start.y,
                end.x, end.y
            );
            
            if (distance > maxDistance) {
                maxDistance = distance;
                maxIndex = i;
            }
        }
        
        // 如果最大距离大于容差，递归处理
        if (maxDistance > tolerance) {
            const left = this.douglasPeucker(points.slice(0, maxIndex + 1), tolerance);
            const right = this.douglasPeucker(points.slice(maxIndex), tolerance);
            return left.slice(0, -1).concat(right);
        } else {
            return [start, end];
        }
    }

    contains(px, py) {
        // 检查点是否在路径附近
        const threshold = Math.max(5, this.properties.strokeWidth / 2 + 3);
        
        for (let i = 0; i < this.points.length - 1; i++) {
            const distance = BaseShape.pointToLineDistance(
                px, py,
                this.points[i].x, this.points[i].y,
                this.points[i + 1].x, this.points[i + 1].y
            );
            
            if (distance <= threshold) {
                return true;
            }
        }
        
        return false;
    }

    toDict() {
        return {
            ...super.toDict(),
            properties: {
                ...this.properties,
                points: this.points.map(p => ({ x: p.x, y: p.y })),
                brushType: this.brushType,
                smoothing: this.smoothing
            }
        };
    }

    static fromDict(data) {
        const props = data.properties;
        const path = new BrushPath(
            props.points || [],
            props.brushType || 'pen',
            { ...props, id: data.id }
        );
        path.timestamp = data.timestamp;
        return path;
    }
}

export default BrushPath;

/**
 * 选择工具
 */

import { BaseTool } from './base.js';

export class SelectTool extends BaseTool {
    constructor() {
        super('select');
        this.document = null;
        this.selectedShape = null;
        this.dragging = false;
        this.dragStart = null;
        this.shapeStartPos = null;
        this.selectedShapesStartPos = new Map(); // 保存所有选中图形的初始位置
        this.boxSelecting = false; // 框选模式
        this.selectionBox = null; // 选择框
    }

    setDocument(document) {
        this.document = document;
    }

    onMouseDown(x, y, event) {
        if (!this.document) return;

        // 先检查是否点击了控制点（优先于图形本身）
        // 如果点击了控制点，发出事件让外部切换到对应工具
        const controlPointHit = this.checkControlPointHit(x, y);
        if (controlPointHit) {
            this.emit('controlPointHit', {
                shape: controlPointHit.shape,
                index: controlPointHit.index,
                shapeType: controlPointHit.shape.type,
                x: x,
                y: y
            });
            // 选中该图形
            this.document.deselectAll();
            this.document.selectShape(controlPointHit.shape);
            this.selectedShape = controlPointHit.shape;
            this.emit('shapeSelected', { 
                shape: controlPointHit.shape,
                properties: controlPointHit.shape.properties
            });
            return;
        }

        const shape = this.document.findShapeAt(x, y);
        
        if (shape) {
            // 如果点击的图形已经被选中，不取消其他选择
            const isAlreadySelected = shape.selected;
            
            // 如果没按 Shift 且点击的不是已选中的图形，先取消所有选择
            if (!event.shiftKey && !isAlreadySelected) {
                this.document.deselectAll();
            }
            
            this.document.selectShape(shape);
            this.selectedShape = shape;
            this.dragging = true;
            this.dragStart = { x, y };
            
            // 保存所有选中图形的初始位置
            this.selectedShapesStartPos.clear();
            const selectedShapes = this.document.getSelectedShapes();
            for (const s of selectedShapes) {
                this.selectedShapesStartPos.set(s.id, s.getCenter());
            }
            
            // 发出选中事件，包含图形的属性
            this.emit('shapeSelected', { 
                shape: shape,
                properties: shape.properties
            });
        } else {
            // 点击空白处，开始框选
            if (!event.shiftKey) {
                this.document.deselectAll();
            }
            this.selectedShape = null;
            this.boxSelecting = true;
            this.dragStart = { x, y };
            this.selectionBox = { x1: x, y1: y, x2: x, y2: y };
            this.emit('boxSelectionStarted', { box: this.selectionBox });
        }
    }

    // 检查是否点击了控制点
    checkControlPointHit(x, y) {
        if (!this.document) return null;
        const tolerance = 10; // 控制点点击容差
        
        // 只检查已选中的图形，避免误判
        const selectedShapes = this.document.getSelectedShapes();
        // 从后往前检查（后绘制的图形在上层）
        for (let i = selectedShapes.length - 1; i >= 0; i--) {
            const shape = selectedShapes[i];
            // 只检查支持控制点的图形类型
            if (!this.isEditableShape(shape)) continue;
            
            // 检查是否有 hitTestControlPoint 方法
            if (typeof shape.hitTestControlPoint === 'function') {
                const result = shape.hitTestControlPoint(x, y, tolerance);
                // 对于曲面，返回 {i, j} 对象；对于曲线，返回索引
                if (result !== null && result !== -1 && result !== undefined) {
                    return { shape, index: result };
                }
            }
        }
        return null;
    }

    // 判断图形是否支持控制点编辑
    isEditableShape(shape) {
        const editableTypes = ['bezier_curve', 'bspline_curve', 'bezier_surface'];
        return editableTypes.includes(shape.type);
    }

    onMouseMove(x, y, event) {
        if (this.boxSelecting) {
            // 更新选择框
            this.selectionBox.x2 = x;
            this.selectionBox.y2 = y;
            this.emit('boxSelectionUpdated', { box: this.selectionBox });
            return;
        }
        
        if (!this.dragging || !this.dragStart) return;

        const dx = x - this.dragStart.x;
        const dy = y - this.dragStart.y;
        
        // 移动所有选中的图形
        const selectedShapes = this.document.getSelectedShapes();
        for (const shape of selectedShapes) {
            const startPos = this.selectedShapesStartPos.get(shape.id);
            if (startPos) {
                shape.setCenter(
                    startPos.x + dx,
                    startPos.y + dy
                );
            }
        }
        
        this.emit('shapeMoving', { shapes: selectedShapes, dx, dy });
    }

    onDoubleClick(x, y, event) {
        if (!this.document) return;
        
        // 双击图形时，如果图形支持编辑，切换到对应工具
        const shape = this.document.findShapeAt(x, y);
        if (shape && this.isEditableShape(shape)) {
            this.document.deselectAll();
            this.document.selectShape(shape);
            this.selectedShape = shape;
            this.emit('shapeSelected', { 
                shape: shape,
                properties: shape.properties
            });
            // 发出双击事件，让外部切换到对应工具
            this.emit('shapeDoubleClicked', {
                shape: shape,
                shapeType: shape.type
            });
        }
    }

    onMouseUp(x, y, event) {
        if (this.boxSelecting) {
            // 完成框选
            this.selectShapesInBox();
            this.emit('boxSelectionEnded');
            this.boxSelecting = false;
            this.selectionBox = null;
            this.dragStart = null;
            return;
        }
        
        if (this.dragging) {
            const dx = x - this.dragStart.x;
            const dy = y - this.dragStart.y;
            
            if (Math.abs(dx) > 1 || Math.abs(dy) > 1) {
                const selectedShapes = this.document.getSelectedShapes();
                this.emit('shapeMoved', { 
                    shapes: selectedShapes,
                    dx, dy
                });
            }
        }
        
        this.dragging = false;
        this.dragStart = null;
        this.selectedShapesStartPos.clear();
    }

    selectShape(shape) {
        if (this.document) {
            this.document.selectShape(shape);
            this.selectedShape = shape;
        }
    }

    deselectAll() {
        if (this.document) {
            this.document.deselectAll();
            this.selectedShape = null;
        }
    }

    selectShapesInBox() {
        if (!this.document || !this.selectionBox) return;
        
        const box = this.selectionBox;
        const minX = Math.min(box.x1, box.x2);
        const maxX = Math.max(box.x1, box.x2);
        const minY = Math.min(box.y1, box.y2);
        const maxY = Math.max(box.y1, box.y2);
        
        const shapes = this.document.getShapes();
        let selectedCount = 0;
        
        for (const shape of shapes) {
            const bounds = shape.getBounds();
            const center = shape.getCenter();
            
            // 检查图形中心是否在选择框内
            if (center.x >= minX && center.x <= maxX &&
                center.y >= minY && center.y <= maxY) {
                this.document.selectShape(shape);
                selectedCount++;
            }
        }
        
        if (selectedCount > 0) {
            this.emit('multipleShapesSelected', { count: selectedCount });
        }
    }

    cancel() {
        this.dragging = false;
        this.boxSelecting = false;
        this.dragStart = null;
        this.selectedShapesStartPos.clear();
        this.selectionBox = null;
    }
}

export default SelectTool;

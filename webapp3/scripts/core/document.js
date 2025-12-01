/**
 * 文档管理器
 * 负责文档的生命周期管理、图形管理和导出功能
 */

import CONFIG from '../config.js';
import { Serializer } from './serializer.js';
import { HistoryManager } from './history.js';

export class Document {
    constructor(canvas, config = {}) {
        this.canvas = canvas;
        this.config = { ...CONFIG, ...config };
        
        this.shapes = [];
        this.serializer = new Serializer();
        this.history = new HistoryManager();
        
        this.filePath = null;
        this.modified = false;
        this.metadata = {};
        
        this.listeners = new Map();
        
        // 监听历史记录变化
        this.history.on('undo', () => this.onHistoryChange());
        this.history.on('redo', () => this.onHistoryChange());
        
        // 保存初始空状态，这样第一个图形可以被撤销
        this.saveState();
    }

    new() {
        this.shapes = [];
        this.history.clear();
        this.filePath = null;
        this.modified = false;
        this.metadata = {};
        
        this.emit('documentNew');
        this.emit('shapesChanged', { shapes: this.shapes });
    }

    save() {
        const data = this.serializer.serialize(this.shapes, this.metadata);
        const jsonString = this.serializer.toJSON(data, true);
        
        this.modified = false;
        this.emit('documentSaved', { data, jsonString });
        
        return jsonString;
    }

    load(jsonString) {
        try {
            const data = this.serializer.fromJSON(jsonString);
            const validation = this.serializer.validate(data);
            
            if (!validation.valid) {
                throw new Error(validation.error);
            }
            
            const result = this.serializer.deserialize(data);
            
            this.shapes = result.shapes;
            this.metadata = result.metadata;
            this.modified = false;
            this.history.clear();
            
            // 保存初始状态到历史记录
            this.saveState();
            
            this.emit('documentLoaded', { shapes: this.shapes, metadata: this.metadata });
            this.emit('shapesChanged', { shapes: this.shapes });
            
            return true;
        } catch (error) {
            console.error('加载文档失败:', error);
            this.emit('documentLoadError', { error });
            throw error;
        }
    }

    addShape(shape) {
        this.shapes.push(shape);
        this.markModified();
        this.saveState();
        this.emit('shapeAdded', { shape });
        this.emit('shapesChanged', { shapes: this.shapes });
    }

    removeShape(shape, saveState = true) {
        const index = this.shapes.indexOf(shape);
        if (index > -1) {
            this.shapes.splice(index, 1);
            this.markModified();
            if (saveState) {
                this.saveState();
            }
            this.emit('shapeRemoved', { shape });
            this.emit('shapesChanged', { shapes: this.shapes });
        }
    }

    getShapes() {
        return this.shapes;
    }

    clearShapes() {
        this.shapes = [];
        this.markModified();
        this.saveState();
        this.emit('shapesCleared');
        this.emit('shapesChanged', { shapes: this.shapes });
    }

    exportPNG() {
        if (!this.canvas) {
            throw new Error('Canvas 未初始化');
        }
        
        const dataURL = this.canvas.exportToPNG();
        this.emit('documentExported', { format: 'png', dataURL });
        return dataURL;
    }

    exportBlob(callback, type = 'image/png', quality = 1.0) {
        if (!this.canvas) {
            throw new Error('Canvas 未初始化');
        }
        
        this.canvas.exportToBlob(callback, type, quality);
    }

    isModified() {
        return this.modified;
    }

    markModified(modified = true) {
        if (this.modified !== modified) {
            this.modified = modified;
            this.emit('modifiedChanged', { modified });
        }
    }

    getMetadata(key, defaultValue = null) {
        return this.metadata[key] !== undefined ? this.metadata[key] : defaultValue;
    }

    setMetadata(key, value) {
        this.metadata[key] = value;
        this.markModified();
    }

    getFilePath() {
        return this.filePath;
    }

    setFilePath(path) {
        this.filePath = path;
        this.emit('filePathChanged', { path });
    }

    saveState() {
        const state = {
            shapes: this.shapes.map(shape => shape.toDict()),
            metadata: { ...this.metadata }
        };
        this.history.push(state);
        console.log('保存状态，图形数量:', this.shapes.length, '历史索引:', this.history.getCurrentIndex());
    }

    undo() {
        console.log('撤销前 - 当前图形数:', this.shapes.length, '历史索引:', this.history.getCurrentIndex(), '可撤销:', this.history.canUndo());
        const state = this.history.undo();
        if (state) {
            this.restoreState(state);
            console.log('撤销后 - 当前图形数:', this.shapes.length, '历史索引:', this.history.getCurrentIndex());
            return true;
        }
        console.log('无法撤销');
        return false;
    }

    redo() {
        const state = this.history.redo();
        if (state) {
            this.restoreState(state);
            return true;
        }
        return false;
    }

    canUndo() {
        return this.history.canUndo();
    }

    canRedo() {
        return this.history.canRedo();
    }

    restoreState(state) {
        try {
            // 反序列化图形
            const shapes = [];
            for (const shapeData of state.shapes) {
                const shape = this.serializer.deserializeShape(shapeData);
                if (shape) {
                    shapes.push(shape);
                }
            }
            
            this.shapes = shapes;
            this.metadata = { ...state.metadata };
            this.markModified();
            
            this.emit('stateRestored', { shapes: this.shapes });
            this.emit('shapesChanged', { shapes: this.shapes });
        } catch (error) {
            console.error('恢复状态失败:', error);
        }
    }

    onHistoryChange() {
        this.emit('historyChanged', {
            canUndo: this.canUndo(),
            canRedo: this.canRedo()
        });
    }

    getShapeCount() {
        return this.shapes.length;
    }

    findShapeAt(x, y) {
        // 从后往前查找（后添加的图形在上层）
        for (let i = this.shapes.length - 1; i >= 0; i--) {
            if (this.shapes[i].contains(x, y)) {
                return this.shapes[i];
            }
        }
        return null;
    }

    selectShape(shape) {
        shape.setSelected(true);
        this.emit('shapeSelected', { shape });
        this.emit('shapesChanged', { shapes: this.shapes });
    }

    deselectAll() {
        for (const shape of this.shapes) {
            shape.setSelected(false);
        }
        this.emit('shapesDeselected');
        this.emit('shapesChanged', { shapes: this.shapes });
    }

    getSelectedShapes() {
        return this.shapes.filter(shape => shape.selected);
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    off(event, callback) {
        if (!this.listeners.has(event)) return;
        
        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    }

    emit(event, data) {
        if (!this.listeners.has(event)) return;
        
        const callbacks = this.listeners.get(event);
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`事件处理器错误 (${event}):`, error);
            }
        });
    }

    destroy() {
        this.shapes = [];
        this.history.destroy();
        this.listeners.clear();
    }
}

export default Document;

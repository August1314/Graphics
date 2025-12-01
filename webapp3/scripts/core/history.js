/**
 * 历史记录管理器
 * 负责撤销/重做功能
 */

import CONFIG from '../config.js';

export class HistoryManager {
    constructor(maxSize = CONFIG.HISTORY.maxSize) {
        this.maxSize = maxSize;
        this.history = [];
        this.currentIndex = -1;
        this.listeners = new Map();
    }

    push(state) {
        // 如果当前不在历史记录末尾，删除后面的记录
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }

        // 添加新状态
        this.history.push(this.cloneState(state));
        this.currentIndex++;

        // 限制历史记录数量
        if (this.history.length > this.maxSize) {
            this.history.shift();
            this.currentIndex--;
        }

        this.emit('historyChanged', {
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            size: this.getSize()
        });
    }

    undo() {
        if (!this.canUndo()) {
            return null;
        }

        this.currentIndex--;
        const state = this.history[this.currentIndex];

        this.emit('undo', { state });
        this.emit('historyChanged', {
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            size: this.getSize()
        });

        return this.cloneState(state);
    }

    redo() {
        if (!this.canRedo()) {
            return null;
        }

        this.currentIndex++;
        const state = this.history[this.currentIndex];

        this.emit('redo', { state });
        this.emit('historyChanged', {
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            size: this.getSize()
        });

        return this.cloneState(state);
    }

    clear() {
        this.history = [];
        this.currentIndex = -1;

        this.emit('historyCleared');
        this.emit('historyChanged', {
            canUndo: false,
            canRedo: false,
            size: 0
        });
    }

    canUndo() {
        return this.currentIndex > 0;
    }

    canRedo() {
        return this.currentIndex < this.history.length - 1;
    }

    getSize() {
        return this.history.length;
    }

    getCurrentIndex() {
        return this.currentIndex;
    }

    getCurrentState() {
        if (this.currentIndex >= 0 && this.currentIndex < this.history.length) {
            return this.cloneState(this.history[this.currentIndex]);
        }
        return null;
    }

    cloneState(state) {
        // 深拷贝状态
        try {
            return JSON.parse(JSON.stringify(state));
        } catch (error) {
            console.error('克隆状态失败:', error);
            return state;
        }
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
        this.clear();
        this.listeners.clear();
    }
}

export default HistoryManager;

/**
 * 基础工具类
 * 所有工具的抽象基类
 */

export class BaseTool {
    constructor(name) {
        this.name = name;
        this.active = false;
        this.config = {};
        this.listeners = new Map();
    }

    activate() {
        this.active = true;
        this.emit('activated');
    }

    deactivate() {
        this.active = false;
        this.emit('deactivated');
    }

    isActive() {
        return this.active;
    }

    onMouseDown(x, y, event) {
        // 子类实现
    }

    onMouseMove(x, y, event) {
        // 子类实现
    }

    onMouseUp(x, y, event) {
        // 子类实现
    }

    onDoubleClick(x, y, event) {
        // 子类实现
    }

    cancel() {
        // 子类实现
    }

    setConfig(config) {
        this.config = { ...this.config, ...config };
    }

    getConfig() {
        return this.config;
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    off(event, callback) {
        if (!this.listeners.has(event)) return;
        
        if (callback) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        } else {
            // 如果没有提供 callback，清除该事件的所有监听器
            this.listeners.delete(event);
        }
    }

    emit(event, data) {
        if (!this.listeners.has(event)) return;
        const callbacks = this.listeners.get(event);
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`工具事件处理器错误 (${event}):`, error);
            }
        });
    }
}

export default BaseTool;

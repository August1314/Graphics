/**
 * 错误处理工具
 */

export class DrawingAppError extends Error {
    constructor(message, code, details) {
        super(message);
        this.name = 'DrawingAppError';
        this.code = code;
        this.details = details;
    }
}

export class FileOperationError extends DrawingAppError {}
export class SerializationError extends DrawingAppError {}
export class ValidationError extends DrawingAppError {}
export class CanvasError extends DrawingAppError {}

export function showError(message, title = '错误') {
    console.error(title + ':', message);
    alert(title + ': ' + message);
}

export function logError(message, error) {
    console.error(message, error);
}

export function handleError(error, context = '') {
    const message = error.message || '未知错误';
    logError(`${context} 错误:`, error);
    showError(message, context || '操作失败');
}

export default { DrawingAppError, FileOperationError, SerializationError, ValidationError, CanvasError, showError, logError, handleError };

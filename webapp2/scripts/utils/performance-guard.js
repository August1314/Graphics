/**
 * 性能保护机制
 * 防止算法执行导致的性能问题
 */

export class PerformanceGuard {
    static MAX_PIXELS = 1000000;  // 最大像素数
    static MAX_ITERATIONS = 100000;  // 最大迭代次数
    static MAX_EXECUTION_TIME = 5000;  // 最大执行时间（毫秒）
    
    /**
     * 检查像素数量
     * @param {number} count - 像素数量
     * @throws {Error} 如果超过限制
     */
    static checkPixelCount(count) {
        if (count > this.MAX_PIXELS) {
            throw new Error(`Pixel count (${count}) exceeds limit (${this.MAX_PIXELS})`);
        }
    }
    
    /**
     * 检查迭代次数
     * @param {number} iterations - 迭代次数
     * @throws {Error} 如果超过限制
     */
    static checkIterations(iterations) {
        if (iterations > this.MAX_ITERATIONS) {
            throw new Error(`Iteration count (${iterations}) exceeds limit (${this.MAX_ITERATIONS})`);
        }
    }
    
    /**
     * 检查执行时间
     * @param {number} startTime - 开始时间（performance.now()）
     * @throws {Error} 如果超过限制
     */
    static checkExecutionTime(startTime) {
        const elapsed = performance.now() - startTime;
        if (elapsed > this.MAX_EXECUTION_TIME) {
            throw new Error(`Execution time (${elapsed.toFixed(2)}ms) exceeds limit (${this.MAX_EXECUTION_TIME}ms)`);
        }
    }
    
    /**
     * 创建超时保护的执行器
     * @param {Function} fn - 要执行的函数
     * @param {number} timeout - 超时时间（毫秒）
     * @returns {Promise} 执行结果
     */
    static withTimeout(fn, timeout = this.MAX_EXECUTION_TIME) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error(`Operation timed out after ${timeout}ms`));
            }, timeout);
            
            try {
                const result = fn();
                clearTimeout(timer);
                resolve(result);
            } catch (error) {
                clearTimeout(timer);
                reject(error);
            }
        });
    }
}

export default PerformanceGuard;

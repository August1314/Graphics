/**
 * 主题管理器
 * 负责主题切换、持久化和事件通知
 */

import CONFIG from '../config.js';

export class ThemeManager {
    constructor() {
        this.currentTheme = CONFIG.UI.theme.default;
        this.storageKey = CONFIG.UI.theme.storageKey;
        this.listeners = new Map();
        
        // 初始化主题
        this.init();
    }

    /**
     * 初始化主题管理器
     */
    init() {
        // 从 localStorage 加载保存的主题偏好
        this.loadPreference();
        
        // 应用主题
        this.applyTheme(this.currentTheme);
        
        // 监听系统主题变化（可选）
        this.watchSystemTheme();
    }

    /**
     * 设置主题
     * @param {string} theme - 主题名称 ('light' 或 'dark')
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            console.warn(`无效的主题: ${theme}，使用默认主题`);
            theme = CONFIG.UI.theme.default;
        }

        if (this.currentTheme === theme) {
            return; // 主题未变化，无需操作
        }

        const oldTheme = this.currentTheme;
        this.currentTheme = theme;

        // 应用主题
        this.applyTheme(theme);

        // 保存偏好
        this.savePreference();

        // 触发主题变化事件
        this.emit('themeChanged', { oldTheme, newTheme: theme });
    }

    /**
     * 获取当前主题
     * @returns {string} 当前主题名称
     */
    getTheme() {
        return this.currentTheme;
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    /**
     * 应用主题到 DOM
     * @param {string} theme - 主题名称
     */
    applyTheme(theme) {
        // 设置 data-theme 属性
        document.documentElement.setAttribute('data-theme', theme);

        // 更新主题切换按钮图标
        this.updateThemeToggleButton(theme);

        // 更新 meta theme-color（移动端浏览器地址栏颜色）
        this.updateMetaThemeColor(theme);
    }

    /**
     * 更新主题切换按钮图标
     * @param {string} theme - 主题名称
     */
    updateThemeToggleButton(theme) {
        const toggleButton = document.getElementById('theme-toggle');
        if (toggleButton) {
            // 浅色主题显示月亮图标，深色主题显示太阳图标
            toggleButton.textContent = theme === 'light' ? '🌙' : '☀️';
            toggleButton.setAttribute('aria-label', 
                theme === 'light' ? '切换到深色主题' : '切换到浅色主题'
            );
        }
    }

    /**
     * 更新 meta theme-color
     * @param {string} theme - 主题名称
     */
    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }

        // 根据主题设置颜色
        const color = theme === 'light' ? '#FFFFFF' : '#0F172A';
        metaThemeColor.content = color;
    }

    /**
     * 保存主题偏好到 localStorage
     */
    savePreference() {
        try {
            localStorage.setItem(this.storageKey, this.currentTheme);
        } catch (error) {
            console.error('保存主题偏好失败:', error);
        }
    }

    /**
     * 从 localStorage 加载主题偏好
     */
    loadPreference() {
        try {
            const savedTheme = localStorage.getItem(this.storageKey);
            if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
                this.currentTheme = savedTheme;
            }
        } catch (error) {
            console.error('加载主题偏好失败:', error);
        }
    }

    /**
     * 监听系统主题变化
     */
    watchSystemTheme() {
        // 检查浏览器是否支持 matchMedia
        if (!window.matchMedia) {
            return;
        }

        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // 监听系统主题变化
        const handleChange = (e) => {
            // 只有在用户没有手动设置主题时才跟随系统
            const hasUserPreference = localStorage.getItem(this.storageKey);
            if (!hasUserPreference) {
                const systemTheme = e.matches ? 'dark' : 'light';
                this.setTheme(systemTheme);
            }
        };

        // 添加监听器
        if (darkModeQuery.addEventListener) {
            darkModeQuery.addEventListener('change', handleChange);
        } else if (darkModeQuery.addListener) {
            // 兼容旧版浏览器
            darkModeQuery.addListener(handleChange);
        }
    }

    /**
     * 注册事件监听器
     * @param {string} event - 事件名称
     * @param {Function} callback - 回调函数
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    /**
     * 移除事件监听器
     * @param {string} event - 事件名称
     * @param {Function} callback - 回调函数
     */
    off(event, callback) {
        if (!this.listeners.has(event)) {
            return;
        }

        const callbacks = this.listeners.get(event);
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    }

    /**
     * 触发事件
     * @param {string} event - 事件名称
     * @param {*} data - 事件数据
     */
    emit(event, data) {
        if (!this.listeners.has(event)) {
            return;
        }

        const callbacks = this.listeners.get(event);
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`事件处理器错误 (${event}):`, error);
            }
        });
    }

    /**
     * 获取主题相关的 CSS 变量值
     * @param {string} variableName - CSS 变量名（不含 --）
     * @returns {string} CSS 变量值
     */
    getCSSVariable(variableName) {
        return getComputedStyle(document.documentElement)
            .getPropertyValue(`--${variableName}`)
            .trim();
    }

    /**
     * 设置主题相关的 CSS 变量
     * @param {string} variableName - CSS 变量名（不含 --）
     * @param {string} value - CSS 变量值
     */
    setCSSVariable(variableName, value) {
        document.documentElement.style.setProperty(`--${variableName}`, value);
    }

    /**
     * 检查当前是否为深色主题
     * @returns {boolean}
     */
    isDarkTheme() {
        return this.currentTheme === 'dark';
    }

    /**
     * 检查当前是否为浅色主题
     * @returns {boolean}
     */
    isLightTheme() {
        return this.currentTheme === 'light';
    }

    /**
     * 销毁主题管理器
     */
    destroy() {
        this.listeners.clear();
    }
}

export default ThemeManager;

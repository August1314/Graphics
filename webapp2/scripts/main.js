/**
 * 主入口文件
 * 初始化应用并连接所有模块
 */

import CONFIG from './config.js';
import { ThemeManager } from './ui/theme.js';
import { NavigationManager } from './ui/navigation.js';
import { CanvasManager } from './core/canvas.js';
import { Document } from './core/document.js';
import { SelectTool } from './tools/select.js';
import { PointTool } from './tools/point.js';
import { LineTool } from './tools/line.js';
import { RectTool } from './tools/rect.js';
import { CircleTool } from './tools/circle.js';
import { PolygonTool } from './tools/polygon.js';
import { BrushTool } from './tools/brush.js';
import { EraserTool } from './tools/eraser.js';
import { FillTool } from './tools/fill.js';

class DrawingApp {
    constructor() {
        this.themeManager = null;
        this.navigationManager = null;
        this.canvasManager = null;
        this.document = null;
        this.tools = new Map();
        this.currentTool = null;
        this.currentStyle = {
            strokeColor: CONFIG.TOOLS.defaultStrokeColor,
            fillColor: CONFIG.TOOLS.defaultFillColor,
            strokeWidth: CONFIG.TOOLS.defaultStrokeWidth,
            opacity: CONFIG.TOOLS.defaultOpacity
        };
    }

    async init() {
        console.log('初始化绘图应用...');
        
        // 初始化主题管理器
        this.themeManager = new ThemeManager();
        
        // 初始化导航管理器
        this.navigationManager = new NavigationManager();
        
        // 初始化功能展示
        this.initFeatures();
        
        // 初始化工具栏
        this.initToolbar();
        
        // 初始化 Canvas
        const canvas = document.getElementById('demo-canvas');
        if (canvas) {
            this.canvasManager = new CanvasManager(canvas);
            this.document = new Document(this.canvasManager);
            
            // 监听文档变化
            this.document.on('shapesChanged', (data) => {
                this.canvasManager.setShapes(data.shapes);
            });
            
            // 注册所有工具
            this.registerTools();
            
            // 设置默认工具为选择工具
            this.setTool('select');
            
            // 绑定事件
            this.bindEvents();
            
            console.log('应用初始化完成');
        } else {
            console.error('未找到 Canvas 元素');
        }
    }

    registerTools() {
        const selectTool = new SelectTool();
        selectTool.setDocument(this.document);
        selectTool.on('shapeMoving', () => {
            // 拖动时实时渲染
            this.canvasManager.requestRender();
        });
        selectTool.on('shapeMoved', () => {
            this.document.saveState();
        });
        selectTool.on('shapeSelected', (data) => {
            // 更新样式控件显示选中图形的属性
            this.updateStyleControls(data.properties);
        });
        this.tools.set('select', selectTool);

        const pointTool = new PointTool();
        pointTool.setStyle(this.currentStyle);
        pointTool.on('shapeCreated', (data) => {
            this.document.addShape(data.shape);
        });
        this.tools.set('point', pointTool);

        const lineTool = new LineTool();
        lineTool.setStyle(this.currentStyle);
        lineTool.on('shapeCreated', (data) => {
            this.document.addShape(data.shape);
        });
        this.tools.set('line', lineTool);

        const rectTool = new RectTool();
        rectTool.setStyle(this.currentStyle);
        rectTool.on('shapeCreated', (data) => {
            this.document.addShape(data.shape);
        });
        this.tools.set('rect', rectTool);

        const circleTool = new CircleTool();
        circleTool.setStyle(this.currentStyle);
        circleTool.on('shapeCreated', (data) => {
            this.document.addShape(data.shape);
        });
        this.tools.set('circle', circleTool);

        const polygonTool = new PolygonTool();
        polygonTool.setStyle(this.currentStyle);
        polygonTool.on('shapeCreated', (data) => {
            this.document.addShape(data.shape);
        });
        this.tools.set('polygon', polygonTool);

        const brushTool = new BrushTool();
        brushTool.setStyle(this.currentStyle);
        brushTool.on('shapeCreated', (data) => {
            this.document.addShape(data.shape);
        });
        this.tools.set('brush', brushTool);

        const eraserTool = new EraserTool();
        eraserTool.setDocument(this.document);
        this.tools.set('eraser', eraserTool);

        const fillTool = new FillTool();
        fillTool.setStyle(this.currentStyle);
        fillTool.on('fillRequested', (data) => {
            // 提供 canvas 引用给填充工具
            if (data.callback) {
                data.callback(this.canvasManager.canvas);
            }
        });
        fillTool.on('fillCompleted', () => {
            // 填充完成后保存状态
            this.document.saveState();
        });
        this.tools.set('fill', fillTool);

        console.log(`注册了 ${this.tools.size} 个工具`);
    }

    setTool(toolName) {
        const tool = this.tools.get(toolName);
        if (!tool) {
            console.warn(`工具不存在: ${toolName}`);
            return;
        }

        // 如果切换到非选择工具，取消所有选择
        if (toolName !== 'select' && this.document) {
            this.document.deselectAll();
            this.canvasManager.requestRender();
        }

        this.currentTool = tool;
        this.canvasManager.setTool(tool);
        
        // 更新工具样式
        if (tool.setStyle) {
            tool.setStyle(this.currentStyle);
        }

        console.log(`切换到工具: ${toolName}`);
    }

    initFeatures() {
        const features = [
            { icon: '📐', title: '基础图形绘制', description: '支持点、线、矩形、圆形、多边形等基础图形' },
            { icon: '🖌️', title: '自由画笔', description: '普通画笔、马克笔、书法笔等多种笔触' },
            { icon: '✏️', title: '图形编辑', description: '选择、移动、缩放、旋转图形' },
            { icon: '🎨', title: '颜色管理', description: '自定义颜色、线宽、填充样式' },
            { icon: '↩️', title: '撤销重做', description: '完整的撤销/重做历史记录' },
            { icon: '💾', title: '导出功能', description: '导出为 PNG、JSON 格式' }
        ];

        const featuresGrid = document.querySelector('.features-grid');
        if (featuresGrid) {
            featuresGrid.innerHTML = features.map(feature => `
                <div class="feature-card">
                    <span class="feature-card-icon">${feature.icon}</span>
                    <h3 class="feature-card-title">${feature.title}</h3>
                    <p class="feature-card-description">${feature.description}</p>
                </div>
            `).join('');
        }
    }

    initToolbar() {
        const toolbar = document.querySelector('.demo-toolbar');
        if (!toolbar) return;

        const tools = [
            { id: 'select', icon: '👆', label: '选择', title: '选择和移动图形' },
            { id: 'point', icon: '⚫', label: '点', title: '绘制点' },
            { id: 'line', icon: '📏', label: '线', title: '绘制直线' },
            { id: 'rect', icon: '▭', label: '矩形', title: '绘制矩形' },
            { id: 'circle', icon: '⭕', label: '圆形', title: '绘制圆形' },
            { id: 'polygon', icon: '⬡', label: '多边形', title: '绘制多边形' },
            { id: 'brush', icon: '🖌️', label: '画笔', title: '自由绘制' },
            { id: 'eraser', icon: '🧹', label: '橡皮擦', title: '擦除图形' }
        ];

        toolbar.innerHTML = `
            <div class="toolbar-section">
                <h3>工具</h3>
                <div class="tool-buttons">
                    ${tools.map(tool => `
                        <button class="tool-btn ${tool.id === 'select' ? 'active' : ''}" 
                                data-tool="${tool.id}" 
                                title="${tool.title}">
                            <span class="tool-icon">${tool.icon}</span>
                            <span class="tool-label">${tool.label}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
            <div class="toolbar-section">
                <h3>样式</h3>
                <div class="style-controls">
                    <div class="control-group">
                        <label for="stroke-color">描边颜色</label>
                        <input type="color" id="stroke-color" value="${this.currentStyle.strokeColor}">
                    </div>
                    <div class="control-group">
                        <label for="fill-color">填充颜色</label>
                        <input type="color" id="fill-color" value="${this.currentStyle.fillColor}">
                    </div>
                    <div class="control-group">
                        <label for="stroke-width">线宽: <span id="stroke-width-value">${this.currentStyle.strokeWidth}</span></label>
                        <input type="range" id="stroke-width" min="1" max="20" value="${this.currentStyle.strokeWidth}">
                    </div>
                </div>
            </div>
        `;

        // 绑定工具按钮事件
        toolbar.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const toolId = btn.dataset.tool;
                this.setTool(toolId);
                
                // 更新按钮状态
                toolbar.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // 绑定样式控件事件
        const strokeColorInput = document.getElementById('stroke-color');
        if (strokeColorInput) {
            strokeColorInput.addEventListener('change', (e) => {
                this.currentStyle.strokeColor = e.target.value;
                if (this.currentTool && this.currentTool.setStyle) {
                    this.currentTool.setStyle(this.currentStyle);
                }
                // 如果是选择工具，更新所有选中图形
                if (this.currentTool && this.currentTool.name === 'select') {
                    const selectedShapes = this.document.getSelectedShapes();
                    if (selectedShapes.length > 0) {
                        selectedShapes.forEach(shape => shape.setStrokeColor(e.target.value));
                        this.canvasManager.requestRender();
                        this.document.saveState();
                    }
                }
            });
        }

        const fillColorInput = document.getElementById('fill-color');
        if (fillColorInput) {
            fillColorInput.addEventListener('change', (e) => {
                this.currentStyle.fillColor = e.target.value;
                if (this.currentTool && this.currentTool.setStyle) {
                    this.currentTool.setStyle(this.currentStyle);
                }
                // 如果是选择工具，更新所有选中图形
                if (this.currentTool && this.currentTool.name === 'select') {
                    const selectedShapes = this.document.getSelectedShapes();
                    if (selectedShapes.length > 0) {
                        selectedShapes.forEach(shape => shape.setFillColor(e.target.value));
                        this.canvasManager.requestRender();
                        this.document.saveState();
                    }
                }
            });
        }

        const strokeWidthInput = document.getElementById('stroke-width');
        const strokeWidthValue = document.getElementById('stroke-width-value');
        if (strokeWidthInput && strokeWidthValue) {
            let strokeWidthChanging = false;
            
            strokeWidthInput.addEventListener('input', (e) => {
                this.currentStyle.strokeWidth = parseInt(e.target.value);
                strokeWidthValue.textContent = e.target.value;
                if (this.currentTool && this.currentTool.setStyle) {
                    this.currentTool.setStyle(this.currentStyle);
                }
                // 如果是选择工具，实时更新所有选中图形
                if (this.currentTool && this.currentTool.name === 'select') {
                    const selectedShapes = this.document.getSelectedShapes();
                    if (selectedShapes.length > 0) {
                        if (!strokeWidthChanging) {
                            strokeWidthChanging = true;
                        }
                        selectedShapes.forEach(shape => shape.setStrokeWidth(parseInt(e.target.value)));
                        this.canvasManager.requestRender();
                    }
                }
            });
            
            // 松开鼠标时保存历史记录
            strokeWidthInput.addEventListener('change', (e) => {
                if (strokeWidthChanging && this.currentTool && this.currentTool.name === 'select') {
                    const selectedShapes = this.document.getSelectedShapes();
                    if (selectedShapes.length > 0) {
                        this.document.saveState();
                    }
                    strokeWidthChanging = false;
                }
            });
        }
    }

    bindEvents() {
        // 主题切换按钮
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.themeManager.toggleTheme();
            });
        }

        // 撤销按钮
        const undoBtn = document.getElementById('btn-undo');
        if (undoBtn) {
            undoBtn.addEventListener('click', () => {
                this.document.undo();
            });
        }

        // 重做按钮
        const redoBtn = document.getElementById('btn-redo');
        if (redoBtn) {
            redoBtn.addEventListener('click', () => {
                this.document.redo();
            });
        }

        // 清空按钮
        const clearBtn = document.getElementById('btn-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (confirm('确定要清空所有图形吗？')) {
                    this.document.clearShapes();
                }
            });
        }

        // 导出 PNG 按钮
        const exportPngBtn = document.getElementById('btn-export-png');
        if (exportPngBtn) {
            exportPngBtn.addEventListener('click', () => {
                this.exportPNG();
            });
        }

        // 保存 JSON 按钮
        const saveJsonBtn = document.getElementById('btn-save-json');
        if (saveJsonBtn) {
            saveJsonBtn.addEventListener('click', () => {
                this.saveJSON();
            });
        }

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // 检测 Mac 的 Cmd 键或 Windows/Linux 的 Ctrl 键
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const modifierKey = isMac ? e.metaKey : e.ctrlKey;
            
            // Ctrl/Cmd + Z: 撤销
            if (modifierKey && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.document.undo();
                return;
            }
            
            // Ctrl/Cmd + Shift + Z 或 Ctrl/Cmd + Y: 重做
            if ((modifierKey && e.key === 'z' && e.shiftKey) || (modifierKey && e.key === 'y')) {
                e.preventDefault();
                this.document.redo();
                return;
            }
            
            // Ctrl/Cmd + S: 保存 JSON
            if (modifierKey && e.key === 's') {
                e.preventDefault();
                this.saveJSON();
                return;
            }
            
            // Ctrl/Cmd + E: 导出 PNG
            if (modifierKey && e.key === 'e') {
                e.preventDefault();
                this.exportPNG();
                return;
            }
            
            // Delete 或 Backspace: 删除选中的图形
            if (e.key === 'Delete' || e.key === 'Backspace') {
                const selectedShapes = this.document.getSelectedShapes();
                if (selectedShapes.length > 0) {
                    e.preventDefault();
                    selectedShapes.forEach(shape => this.document.removeShape(shape));
                    this.document.saveState();
                }
                return;
            }
            
            // Esc: 取消当前操作
            if (e.key === 'Escape') {
                if (this.currentTool && typeof this.currentTool.cancel === 'function') {
                    this.currentTool.cancel();
                }
                this.document.deselectAll();
                this.canvasManager.requestRender();
                return;
            }
            
            // 数字键 1-8: 快速切换工具
            const toolKeys = {
                '1': 'select',
                '2': 'point',
                '3': 'line',
                '4': 'rect',
                '5': 'circle',
                '6': 'polygon',
                '7': 'brush',
                '8': 'eraser'
            };
            
            if (toolKeys[e.key] && !modifierKey) {
                e.preventDefault();
                this.setTool(toolKeys[e.key]);
                // 更新工具栏按钮状态
                const toolbar = document.querySelector('.demo-toolbar');
                if (toolbar) {
                    toolbar.querySelectorAll('.tool-btn').forEach(btn => {
                        if (btn.dataset.tool === toolKeys[e.key]) {
                            btn.classList.add('active');
                        } else {
                            btn.classList.remove('active');
                        }
                    });
                }
                return;
            }
            
            // Ctrl/Cmd + 0: 重置缩放
            if (modifierKey && e.key === '0') {
                e.preventDefault();
                this.canvasManager.resetView();
                return;
            }
            
            // Ctrl/Cmd + =: 放大
            if (modifierKey && (e.key === '=' || e.key === '+')) {
                e.preventDefault();
                this.canvasManager.zoomIn();
                return;
            }
            
            // Ctrl/Cmd + -: 缩小
            if (modifierKey && e.key === '-') {
                e.preventDefault();
                this.canvasManager.zoomOut();
                return;
            }
        });

        console.log('事件绑定完成');
    }

    updateStyleControls(properties) {
        // 更新样式控件以显示选中图形的属性
        const strokeColorInput = document.getElementById('stroke-color');
        const fillColorInput = document.getElementById('fill-color');
        const strokeWidthInput = document.getElementById('stroke-width');
        const strokeWidthValue = document.getElementById('stroke-width-value');
        
        if (strokeColorInput && properties.strokeColor) {
            strokeColorInput.value = properties.strokeColor;
        }
        
        if (fillColorInput && properties.fillColor) {
            if (properties.fillColor === 'transparent') {
                fillColorInput.value = '#ffffff';
            } else {
                fillColorInput.value = properties.fillColor;
            }
        }
        
        if (strokeWidthInput && properties.strokeWidth !== undefined) {
            strokeWidthInput.value = properties.strokeWidth;
            if (strokeWidthValue) {
                strokeWidthValue.textContent = properties.strokeWidth;
            }
        }
    }

    exportPNG() {
        try {
            const dataURL = this.document.exportPNG();
            const link = document.createElement('a');
            link.download = `drawing_${Date.now()}.png`;
            link.href = dataURL;
            link.click();
            console.log('PNG 导出成功');
        } catch (error) {
            console.error('PNG 导出失败:', error);
            alert('导出失败: ' + error.message);
        }
    }

    saveJSON() {
        try {
            const jsonString = this.document.save();
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.download = `drawing_${Date.now()}.json`;
            link.href = url;
            link.click();
            URL.revokeObjectURL(url);
            console.log('JSON 保存成功');
        } catch (error) {
            console.error('JSON 保存失败:', error);
            alert('保存失败: ' + error.message);
        }
    }
}

// 应用启动
const app = new DrawingApp();

// DOM 加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}

// 导出到全局（用于调试）
window.drawingApp = app;

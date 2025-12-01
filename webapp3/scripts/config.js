/**
 * 应用配置文件
 * 定义所有默认配置和常量
 */

export const CONFIG = {
    // 应用信息
    APP: {
        name: '绘图系统',
        version: '2.0.0',
        description: '专业的二维图形绘图工具'
    },

    // Canvas 配置
    CANVAS: {
        defaultWidth: 800,
        defaultHeight: 600,
        backgroundColor: '#FFFFFF',
        minWidth: 300,
        minHeight: 200,
        maxWidth: 4096,
        maxHeight: 4096
    },

    // 工具默认配置
    TOOLS: {
        defaultTool: 'select',
        
        // 默认样式
        defaultStrokeColor: '#000000',
        defaultStrokeWidth: 2,
        defaultFillColor: 'transparent', // 透明填充，不覆盖其他图形
        defaultOpacity: 1.0,
        
        // 点工具
        point: {
            defaultRadius: 3,
            minRadius: 1,
            maxRadius: 20
        },
        
        // 线工具
        line: {
            defaultStyle: 'solid', // solid, dashed, dotted
            minWidth: 0.5,
            maxWidth: 50
        },
        
        // 画笔工具
        brush: {
            defaultType: 'pen', // pen, marker, calligraphy, spray
            defaultWidth: 8,
            minWidth: 1,
            maxWidth: 100,
            smoothing: true,
            minDistance: 2, // 最小点间距
            simplifyTolerance: 1.0 // 简化容差
        },
        
        // 橡皮擦工具
        eraser: {
            defaultMode: 'object', // object, path
            defaultSize: 20,
            minSize: 5,
            maxSize: 100
        },
        
        // 多边形工具
        polygon: {
            minPoints: 3,
            maxPoints: 100
        }
    },

    // 历史记录配置
    HISTORY: {
        maxSize: 50, // 最大历史记录数量
        autoSave: false,
        autoSaveInterval: 60000 // 自动保存间隔（毫秒）
    },

    // 序列化配置
    SERIALIZER: {
        version: '2.0',
        prettyPrint: true,
        indent: 2
    },

    // 导出配置
    EXPORT: {
        png: {
            quality: 1.0,
            backgroundColor: '#FFFFFF'
        },
        json: {
            prettyPrint: true,
            indent: 2
        }
    },

    // 性能配置
    PERFORMANCE: {
        useRequestAnimationFrame: true,
        throttleInterval: 16, // 约 60 FPS
        debounceDelay: 300,
        maxShapesBeforeWarning: 1000
    },

    // UI 配置
    UI: {
        theme: {
            default: 'light', // light, dark
            storageKey: 'drawing-app-theme'
        },
        
        toolbar: {
            position: 'left', // left, right, top, bottom
            collapsible: false
        },
        
        modal: {
            closeOnOverlayClick: true,
            closeOnEscape: true
        },
        
        navigation: {
            smoothScroll: true,
            scrollOffset: 60 // 导航栏高度
        }
    },

    // 响应式断点
    BREAKPOINTS: {
        mobile: 768,
        tablet: 1024,
        desktop: 1440
    },

    // 颜色预设
    COLOR_PRESETS: [
        '#000000', // 黑色
        '#FFFFFF', // 白色
        '#FF0000', // 红色
        '#00FF00', // 绿色
        '#0000FF', // 蓝色
        '#FFFF00', // 黄色
        '#FF00FF', // 品红
        '#00FFFF', // 青色
        '#FFA500', // 橙色
        '#800080', // 紫色
        '#808080', // 灰色
        '#A52A2A'  // 棕色
    ],

    // 线宽预设
    LINE_WIDTH_PRESETS: [1, 2, 4, 8, 16, 32],

    // 错误消息
    ERRORS: {
        fileLoadFailed: '文件加载失败',
        fileSaveFailed: '文件保存失败',
        invalidFormat: '无效的文件格式',
        canvasError: 'Canvas 操作失败',
        serializationError: '序列化失败',
        deserializationError: '反序列化失败'
    },

    // 成功消息
    SUCCESS: {
        fileSaved: '文件保存成功',
        fileLoaded: '文件加载成功',
        exported: '导出成功'
    }
};

// 冻结配置对象，防止意外修改
Object.freeze(CONFIG);

export default CONFIG;

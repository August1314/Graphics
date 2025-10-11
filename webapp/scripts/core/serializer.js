/**
 * 序列化器
 * 负责图形数据的序列化和反序列化，支持版本迁移
 */

import CONFIG from '../config.js';
import { Point } from '../shapes/point.js';
import { Line } from '../shapes/line.js';
import { Rectangle } from '../shapes/rect.js';
import { Circle } from '../shapes/circle.js';
import { Polygon } from '../shapes/polygon.js';
import { BrushPath } from '../shapes/path.js';

export class Serializer {
    constructor() {
        this.version = CONFIG.SERIALIZER.version;
        this.typeRegistry = new Map();
        this.registerTypes();
    }

    registerTypes() {
        this.typeRegistry.set('point', Point);
        this.typeRegistry.set('line', Line);
        this.typeRegistry.set('rect', Rectangle);
        this.typeRegistry.set('circle', Circle);
        this.typeRegistry.set('polygon', Polygon);
        this.typeRegistry.set('brush_path', BrushPath);
    }

    serialize(shapes, metadata = {}) {
        const data = {
            version: this.version,
            canvas: {
                width: CONFIG.CANVAS.defaultWidth,
                height: CONFIG.CANVAS.defaultHeight
            },
            metadata: {
                created: new Date().toISOString(),
                modified: new Date().toISOString(),
                ...metadata
            },
            shapes: []
        };

        for (const shape of shapes) {
            try {
                const shapeData = this.serializeShape(shape);
                if (shapeData) {
                    data.shapes.push(shapeData);
                }
            } catch (error) {
                console.error('序列化图形失败:', error, shape);
            }
        }

        return data;
    }

    serializeShape(shape) {
        if (!shape || typeof shape.toDict !== 'function') {
            console.warn('无效的图形对象:', shape);
            return null;
        }

        try {
            return shape.toDict();
        } catch (error) {
            console.error('调用 toDict() 失败:', error, shape);
            return null;
        }
    }

    deserialize(data) {
        if (!data || typeof data !== 'object') {
            throw new Error('无效的序列化数据');
        }

        // 检查版本并迁移
        const version = data.version || '1.0';
        if (version !== this.version) {
            console.log(`检测到旧版本数据 (${version})，进行迁移`);
            data = this.migrateVersion(data, version);
        }

        const shapes = [];
        const shapesData = data.shapes || [];

        for (const shapeData of shapesData) {
            try {
                const shape = this.deserializeShape(shapeData);
                if (shape) {
                    shapes.push(shape);
                }
            } catch (error) {
                console.error('反序列化图形失败:', error, shapeData);
            }
        }

        return {
            shapes,
            metadata: data.metadata || {},
            canvas: data.canvas || {}
        };
    }

    deserializeShape(data) {
        if (!data || !data.type) {
            console.warn('图形数据缺少 type 字段:', data);
            return null;
        }

        const ShapeClass = this.typeRegistry.get(data.type);
        if (!ShapeClass) {
            console.warn(`未注册的图形类型: ${data.type}`);
            return null;
        }

        if (typeof ShapeClass.fromDict !== 'function') {
            console.warn(`图形类 ${data.type} 没有 fromDict 方法`);
            return null;
        }

        try {
            return ShapeClass.fromDict(data);
        } catch (error) {
            console.error(`从字典创建 ${data.type} 失败:`, error);
            return null;
        }
    }

    migrateVersion(data, fromVersion) {
        if (fromVersion === '1.0') {
            console.log('从 v1.0 迁移到 v2.0');
            data = this.migrateV1ToV2(data);
        }
        return data;
    }

    migrateV1ToV2(data) {
        // 更新版本号
        data.version = '2.0';

        // 确保有 metadata 字段
        if (!data.metadata) {
            data.metadata = {};
        }

        // 为每个图形添加 ID（如果没有）
        if (data.shapes) {
            for (const shape of data.shapes) {
                if (!shape.id) {
                    shape.id = this.generateId();
                }
            }
        }

        return data;
    }

    generateId() {
        return 'shape_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    encodeColor(color) {
        // 颜色已经是字符串格式，直接返回
        return color;
    }

    decodeColor(colorStr) {
        // 验证颜色格式
        const colorRegex = /^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$/;
        if (colorRegex.test(colorStr)) {
            return colorStr;
        }
        // 默认返回黑色
        return '#000000';
    }

    toJSON(data, prettyPrint = true) {
        if (prettyPrint) {
            return JSON.stringify(data, null, CONFIG.SERIALIZER.indent);
        }
        return JSON.stringify(data);
    }

    fromJSON(jsonString) {
        try {
            return JSON.parse(jsonString);
        } catch (error) {
            throw new Error(`JSON 解析失败: ${error.message}`);
        }
    }

    validate(data) {
        if (!data || typeof data !== 'object') {
            return { valid: false, error: '数据必须是对象' };
        }

        if (!data.version) {
            return { valid: false, error: '缺少 version 字段' };
        }

        if (!Array.isArray(data.shapes)) {
            return { valid: false, error: 'shapes 必须是数组' };
        }

        for (let i = 0; i < data.shapes.length; i++) {
            const shape = data.shapes[i];
            if (!shape.type) {
                return { valid: false, error: `图形 ${i} 缺少 type 字段` };
            }
            if (!shape.properties) {
                return { valid: false, error: `图形 ${i} 缺少 properties 字段` };
            }
        }

        return { valid: true };
    }
}

export default Serializer;

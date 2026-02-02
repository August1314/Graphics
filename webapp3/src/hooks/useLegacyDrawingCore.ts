import { useCallback, useEffect, useRef } from 'react';
import type { AlgorithmState, SelectionState, StyleState, ToolId, ViewState } from '../pages/DrawPage';

// 直接复用现有 JS 模块（Vite / bundler 需允许从 src 相对导入 .js）
// 这些文件已在 webapp3/scripts 下实现完整逻辑
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { CanvasManager } from '../../scripts/core/canvas.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { Document } from '../../scripts/core/document.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { SelectTool } from '../../scripts/tools/select.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { PointTool } from '../../scripts/tools/point.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { LineTool } from '../../scripts/tools/line.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { RectTool } from '../../scripts/tools/rect.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { CircleTool } from '../../scripts/tools/circle.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { PolygonTool } from '../../scripts/tools/polygon.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { BrushTool } from '../../scripts/tools/brush.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { EraserTool } from '../../scripts/tools/eraser.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { FillTool } from '../../scripts/tools/fill.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { BezierCurveTool } from '../../scripts/tools/bezier_curve.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { BSplineCurveTool } from '../../scripts/tools/bspline_curve.js';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { BezierSurfaceTool } from '../../scripts/tools/bezier_surface.js';

type LegacyCore = {
  setTool: (toolId: ToolId) => void;
  setStyle: (style: StyleState) => void;
  setAlgorithms: (algorithms: AlgorithmState) => void;
  setViewOptions: (view: ViewState) => void;
  setSurfaceOptions: (options: { mode?: 'grid' | 'fill' }) => void;
  undo: () => void;
  redo: () => void;
  clear: () => void;
  exportPng: () => void;
  transform: (action: 'rotateLeft' | 'rotateRight' | 'scaleDown' | 'scaleUp') => void;
  destroy: () => void;
};

export interface UseLegacyDrawingCoreOptions {
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  onSelectionChange: (selection: SelectionState) => void;
  onToolAutoSwitch?: (toolId: ToolId) => void;
}

export function useLegacyDrawingCore(options: UseLegacyDrawingCoreOptions) {
  const { canvasRef, onSelectionChange, onToolAutoSwitch } = options;
  const coreRef = useRef<LegacyCore | null>(null);

  useEffect(() => {
    const canvasElement = canvasRef.current;
    if (!canvasElement) {
      return;
    }

    // 初始化 CanvasManager 与 Document
    const canvasManager = new CanvasManager(canvasElement);
    const drawingDocument = new Document(canvasManager);

    const tools = new Map<string, any>();
    const currentStyle: StyleState = {
      strokeColor: '#000000',
      fillColor: 'transparent',
      strokeWidth: 2,
      fillTransparent: true,
    };

    // 图形类型到工具ID的映射
    const shapeTypeToToolId: Record<string, ToolId> = {
      'point': 'point',
      'line': 'line',
      'rect': 'rect',
      'circle': 'circle',
      'polygon': 'polygon',
      'brush_path': 'brush',
      'bezier_curve': 'bezierCurve',
      'bspline_curve': 'bsplineCurve',
      'bezier_surface': 'bezierSurface',
    };

    // 选择工具
    const selectTool = new SelectTool();
    selectTool.setDocument(drawingDocument);
    selectTool.on('shapeMoving', () => canvasManager.requestRender());
    selectTool.on('shapeMoved', () => drawingDocument.saveState());
    selectTool.on('shapeSelected', (data: any) => {
      const selectedShapes = drawingDocument.getSelectedShapes();
      const shape = data?.shape;
      const selection: SelectionState = {
        selectedShapeType: shape?.type ?? null,
        selectedCount: selectedShapes.length,
        selectedSurfaceMode: shape?.type === 'bezier_surface' ? shape.mode : undefined,
      };
      onSelectionChange(selection);
      // 不再自动切换工具，保持选择工具的功能
    });
    
    // 点击控制点时，切换到对应工具
    selectTool.on('controlPointHit', (data: any) => {
      const toolId = shapeTypeToToolId[data.shapeType];
      if (toolId && toolId !== 'select') {
        isAutoSwitching = true;
        const tool = tools.get(toolId);
        if (tool) {
          canvasManager.setTool(tool);
          if (tool.setStyle) {
            tool.setStyle(currentStyle);
          }
          // 通知 React 组件更新当前工具
          if (onToolAutoSwitch) {
            onToolAutoSwitch(toolId);
          }
          // 让工具处理控制点拖动
          if (typeof tool.tryStartControlDrag === 'function') {
            tool.tryStartControlDrag(data.x || 0, data.y || 0);
          }
        }
      }
    });
    
    // 双击图形时，切换到对应工具进行编辑
    selectTool.on('shapeDoubleClicked', (data: any) => {
      const toolId = shapeTypeToToolId[data.shapeType];
      if (toolId && toolId !== 'select') {
        isAutoSwitching = true;
        const tool = tools.get(toolId);
        if (tool) {
          canvasManager.setTool(tool);
          if (tool.setStyle) {
            tool.setStyle(currentStyle);
          }
          // 通知 React 组件更新当前工具
          if (onToolAutoSwitch) {
            onToolAutoSwitch(toolId);
          }
        }
      }
    });
    
    tools.set('select', selectTool);

    // 注册一个帮助函数：添加图形并自动选中
    const addAndSelect = (shape: any) => {
      if (!shape) return;
      drawingDocument.addShape(shape);
      drawingDocument.deselectAll();
      drawingDocument.selectShape(shape);
      canvasManager.requestRender();
      const selectedShapes = drawingDocument.getSelectedShapes();
      onSelectionChange({
        selectedShapeType: shape.type ?? null,
        selectedCount: selectedShapes.length,
        selectedSurfaceMode: shape.type === 'bezier_surface' ? shape.mode : undefined,
      });
    };

    // 点
    const pointTool = new PointTool();
    pointTool.setStyle(currentStyle);
    pointTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('point', pointTool);

    // 线
    const lineTool = new LineTool();
    lineTool.setStyle(currentStyle);
    lineTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('line', lineTool);

    // 矩形
    const rectTool = new RectTool();
    rectTool.setStyle(currentStyle);
    rectTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('rect', rectTool);

    // 圆
    const circleTool = new CircleTool();
    circleTool.setStyle(currentStyle);
    circleTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('circle', circleTool);

    // 多边形
    const polygonTool = new PolygonTool();
    polygonTool.setStyle(currentStyle);
    polygonTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('polygon', polygonTool);

    // 画笔
    const brushTool = new BrushTool();
    brushTool.setStyle(currentStyle);
    brushTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('brush', brushTool);

    // 橡皮擦
    const eraserTool = new EraserTool();
    eraserTool.setDocument(drawingDocument);
    tools.set('eraser', eraserTool);

    // 填充
    const fillTool = new FillTool();
    fillTool.setStyle(currentStyle);
    fillTool.on('fillRequested', (data: any) => {
      if (data.callback) {
        data.callback(canvasManager.canvas, drawingDocument);
      }
    });
    fillTool.on('fillCompleted', () => {
      drawingDocument.saveState();
      canvasManager.requestRender();
    });
    tools.set('fill', fillTool);

    // Bézier 曲线
    const bezierTool = new BezierCurveTool();
    bezierTool.setDocument(drawingDocument);
    bezierTool.setStyle(currentStyle);
    bezierTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('bezierCurve', bezierTool);

    // B 样条
    const bsplineTool = new BSplineCurveTool();
    bsplineTool.setDocument(drawingDocument);
    bsplineTool.setStyle(currentStyle);
    bsplineTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('bsplineCurve', bsplineTool);

    // Bézier 曲面
    const surfaceTool = new BezierSurfaceTool();
    surfaceTool.setDocument(drawingDocument);
    surfaceTool.setStyle(currentStyle);
    surfaceTool.on('shapeCreated', (data: any) => addAndSelect(data.shape));
    tools.set('bezierSurface', surfaceTool);

    // 将文档变化同步到 Canvas
    drawingDocument.on('shapesChanged', (data: any) => {
      canvasManager.setShapes(data.shapes);
    });

    // 默认工具
    canvasManager.setTool(selectTool);

    // 标记是否正在自动切换工具（避免取消选择）
    let isAutoSwitching = false;
    
    coreRef.current = {
      setTool: (toolId: ToolId, preserveSelection = false) => {
        const tool = tools.get(toolId);
        if (!tool) return;
        // 切换工具前取消选择（除非是自动切换或明确要求保持选择）
        if (toolId !== 'select' && !preserveSelection && !isAutoSwitching) {
          drawingDocument.deselectAll();
          onSelectionChange({ selectedShapeType: null, selectedCount: 0 });
        }
        canvasManager.setTool(tool);
        if (tool.setStyle) {
          tool.setStyle(currentStyle);
        }
        isAutoSwitching = false;
      },
      setStyle: (style: StyleState) => {
        // 更新当前样式并同步到当前工具
        currentStyle.strokeColor = style.strokeColor;
        currentStyle.fillColor = style.fillTransparent ? 'transparent' : style.fillColor;
        currentStyle.strokeWidth = style.strokeWidth;
        currentStyle.fillTransparent = style.fillTransparent;

        const tool = canvasManager.getCurrentTool?.() ?? null;
        if (tool && typeof tool.setStyle === 'function') {
          tool.setStyle(currentStyle);
        }

        // 如果有选中的图形，无论当前工具是什么，都实时更新这些图形的样式
        // 这样即使刚绘制完图形，工具还是绘制工具，也能修改选中图形的样式
        const selectedShapes = drawingDocument.getSelectedShapes();
        if (selectedShapes.length > 0) {
          selectedShapes.forEach((shape: any) => {
            if (typeof shape.setStrokeColor === 'function') {
              shape.setStrokeColor(style.strokeColor);
            }
            if (typeof shape.setFillColor === 'function') {
              shape.setFillColor(style.fillTransparent ? 'transparent' : style.fillColor);
            }
            if (typeof shape.setStrokeWidth === 'function') {
              shape.setStrokeWidth(style.strokeWidth);
            }
          });
          canvasManager.requestRender();
          // 注意：这里不立即保存历史记录，避免频繁保存
          // 历史记录会在用户完成操作后（如鼠标松开）通过其他机制保存
        }
      },
      setAlgorithms: (algorithms: AlgorithmState) => {
        // 这里只预留接口，具体算法选择逻辑已经在 tools 和 shapes 中实现
        // 如果需要，可以在这里遍历现有图形并更新其 algorithm 字段
        console.debug('update algorithms', algorithms);
      },
      setViewOptions: (view: ViewState) => {
        // 网格
        if (view.gridEnabled !== undefined) {
          const show = view.gridEnabled;
          if (canvasManager.showGrid !== show) {
            canvasManager.toggleGrid();
          }
        }
        // 调试
        if (view.debugEnabled !== undefined) {
          (window as any).DEBUG_MODE = view.debugEnabled;
        }
        // 光栅化开关：更新所有已有图形
        if (view.rasterEnabled !== undefined) {
          const shapes = drawingDocument.getShapes();
          shapes.forEach((shape: any) => {
            if (Object.prototype.hasOwnProperty.call(shape, 'useRasterization')) {
              shape.useRasterization = view.rasterEnabled;
            }
          });
          canvasManager.requestRender();
        }
      },
      setSurfaceOptions: (options: { mode?: 'grid' | 'fill' }) => {
        // 更新曲面工具的默认模式
        const surfaceTool = tools.get('bezierSurface');
        if (surfaceTool && typeof surfaceTool.setMode === 'function' && options.mode) {
          surfaceTool.setMode(options.mode);
        }

        // 同步选中曲面
        if (options.mode) {
          const defaultFill = '#cccccc';
          const selectedShapes = drawingDocument.getSelectedShapes();
          let changed = false;
          selectedShapes.forEach((shape: any) => {
            if (shape.type === 'bezier_surface') {
              shape.mode = options.mode;
              if (shape.properties) {
                shape.properties.mode = options.mode;
              }
              // 填充模式下，若当前填充色透明，则补一个默认填充色
              if (options.mode === 'fill') {
                const fill = shape.properties?.fillColor;
                if (!fill || fill === 'transparent') {
                  const newFill = shape.fillColor && shape.fillColor !== 'transparent' ? shape.fillColor : defaultFill;
                  if (shape.setFillColor) {
                    shape.setFillColor(newFill);
                  }
                  if (shape.properties) {
                    shape.properties.fillColor = newFill;
                    shape.properties.fillTransparent = false;
                  }
                }
              }
              if (shape.cacheValid !== undefined) {
                shape.cacheValid = false;
              }
              changed = true;
            }
          });
          if (changed) {
            drawingDocument.markModified();
            drawingDocument.emit('shapesChanged', { shapes: drawingDocument.getShapes() });
            canvasManager.requestRender();
            // 同步选择状态中的曲面模式，避免 UI 被旧值覆盖
            const selection: SelectionState = {
              selectedShapeType: selectedShapes[0]?.type ?? null,
              selectedCount: selectedShapes.length,
              selectedSurfaceMode: options.mode,
            };
            onSelectionChange(selection);
          }
        }
      },
      undo: () => {
        drawingDocument.undo();
      },
      redo: () => {
        drawingDocument.redo();
      },
      clear: () => {
        drawingDocument.clearShapes();
      },
      exportPng: () => {
        const dataURL = drawingDocument.exportPNG();
        const link = window.document.createElement('a');
        link.download = `drawing_${Date.now()}.png`;
        link.href = dataURL;
        link.click();
      },
      transform: (action: 'rotateLeft' | 'rotateRight' | 'scaleDown' | 'scaleUp') => {
        const selected = drawingDocument.getSelectedShapes();
        if (selected.length === 0) return;
        const isRotate = action === 'rotateLeft' || action === 'rotateRight';
        if (isRotate) {
          const angle = (Math.PI / 18) * (action === 'rotateRight' ? 1 : -1); // 10°
          selected.forEach((shape: any) => {
            if (typeof shape.rotate === 'function') {
              shape.rotate(angle);
            }
          });
        } else {
          const factor = action === 'scaleUp' ? 1.1 : 0.9;
          selected.forEach((shape: any) => {
            if (typeof shape.scale === 'function') {
              shape.scale(factor);
            }
          });
        }
        canvasManager.requestRender();
        drawingDocument.saveState();
      },
      saveState: () => {
        drawingDocument.saveState();
      },
      destroy: () => {
        drawingDocument.destroy();
        canvasManager.destroy();
      },
      onToolAutoSwitch,
    };

    // 键盘快捷键（撤销/重做/导出/删除/视图缩放/旋转缩放）
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifierKey = isMac ? e.metaKey : e.ctrlKey;

      // Ctrl/Cmd + Z: 撤销
      if (modifierKey && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        drawingDocument.undo();
        return;
      }

      // Ctrl/Cmd + Shift + Z 或 Ctrl/Cmd + Y: 重做
      if ((modifierKey && e.key === 'z' && e.shiftKey) || (modifierKey && e.key === 'y')) {
        e.preventDefault();
        drawingDocument.redo();
        return;
      }

      // Ctrl/Cmd + E: 导出 PNG
      if (modifierKey && e.key === 'e') {
        e.preventDefault();
        const dataURL = drawingDocument.exportPNG();
        const link = window.document.createElement('a');
        link.download = `drawing_${Date.now()}.png`;
        link.href = dataURL;
        link.click();
        return;
      }

      // Delete 或 Backspace: 删除选中图形
      if (e.key === 'Delete' || e.key === 'Backspace') {
        const selected = drawingDocument.getSelectedShapes();
        if (selected.length > 0) {
          e.preventDefault();
          selected.forEach((shape: any) => drawingDocument.removeShape(shape));
          drawingDocument.saveState();
        }
        return;
      }

      // Esc: 取消当前操作并取消选择
      if (e.key === 'Escape') {
        const tool = canvasManager.getCurrentTool?.() ?? null;
        if (tool && typeof tool.cancel === 'function') {
          tool.cancel();
        }
        drawingDocument.deselectAll();
        canvasManager.requestRender();
        onSelectionChange({ selectedShapeType: null, selectedCount: 0 });
        return;
      }

      // Ctrl/Cmd + 0: 重置缩放
      if (modifierKey && e.key === '0') {
        e.preventDefault();
        canvasManager.resetView();
        return;
      }

      // Ctrl/Cmd + = / +: 放大
      if (modifierKey && (e.key === '=' || e.key === '+')) {
        e.preventDefault();
        canvasManager.zoomIn();
        return;
      }

      // Ctrl/Cmd + -: 缩小
      if (modifierKey && e.key === '-') {
        e.preventDefault();
        canvasManager.zoomOut();
        return;
      }

      // r / R：旋转选中图形
      if (!modifierKey && (e.key === 'r' || e.key === 'R')) {
        const angle = (Math.PI / 18) * (e.key === 'r' ? 1 : -1); // 10 度
        const selected = drawingDocument.getSelectedShapes();
        if (selected.length > 0) {
          e.preventDefault();
          selected.forEach((shape: any) => {
            if (typeof shape.rotate === 'function') {
              shape.rotate(angle);
            }
          });
          canvasManager.requestRender();
          drawingDocument.saveState();
        }
        return;
      }

      // [ / ]：缩放选中图形
      if (!modifierKey && (e.key === '[' || e.key === ']')) {
        const factor = e.key === '[' ? 0.9 : 1.1;
        const selected = drawingDocument.getSelectedShapes();
        if (selected.length > 0) {
          e.preventDefault();
          selected.forEach((shape: any) => {
            if (typeof shape.scale === 'function') {
              shape.scale(factor);
            }
          });
          canvasManager.requestRender();
          drawingDocument.saveState();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      coreRef.current?.destroy();
      coreRef.current = null;
    };
  }, [canvasRef, onSelectionChange]);

  const setTool = useCallback((toolId: ToolId) => {
    coreRef.current?.setTool(toolId);
  }, []);

  const setStyle = useCallback((style: StyleState) => {
    coreRef.current?.setStyle(style);
  }, []);

  const setAlgorithms = useCallback((algorithms: AlgorithmState) => {
    coreRef.current?.setAlgorithms(algorithms);
  }, []);

  const setViewOptions = useCallback((view: ViewState) => {
    coreRef.current?.setViewOptions(view);
  }, []);

  const setSurfaceOptions = useCallback((options: { mode?: 'grid' | 'fill' }) => {
    coreRef.current?.setSurfaceOptions(options);
  }, []);

  const undo = useCallback(() => {
    coreRef.current?.undo();
  }, []);

  const redo = useCallback(() => {
    coreRef.current?.redo();
  }, []);

  const clear = useCallback(() => {
    coreRef.current?.clear();
  }, []);

  const exportPng = useCallback(() => {
    coreRef.current?.exportPng();
  }, []);

  const transform = useCallback(
    (action: 'rotateLeft' | 'rotateRight' | 'scaleDown' | 'scaleUp') => {
      coreRef.current?.transform(action);
    },
    [],
  );

  const saveState = useCallback(() => {
    coreRef.current?.saveState();
  }, []);

  return {
    setTool,
    setStyle,
    setAlgorithms,
    setViewOptions,
    setSurfaceOptions,
    undo,
    redo,
    clear,
    exportPng,
    transform,
    saveState,
  };
}



import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Toolbar } from '../components/Toolbar/Toolbar';
import { CanvasPane } from '../components/CanvasPane/CanvasPane';
import { TourGuide } from '../components/TourGuide/TourGuide';
import { useLegacyDrawingCore } from '../hooks/useLegacyDrawingCore';

export type ToolId =
  | 'select'
  | 'point'
  | 'line'
  | 'rect'
  | 'circle'
  | 'polygon'
  | 'brush'
  | 'fill'
  | 'eraser'
  | 'bezierCurve'
  | 'bsplineCurve'
  | 'bezierSurface';

export interface StyleState {
  strokeColor: string;
  fillColor: string;
  strokeWidth: number;
  fillTransparent: boolean;
}

export interface AlgorithmState {
  line: string;
  circle: string;
  fill: string;
}

export interface ViewState {
  gridEnabled: boolean;
  debugEnabled: boolean;
  rasterEnabled: boolean;
}

export interface SelectionState {
  selectedShapeType: string | null;
  selectedCount: number;
  selectedSurfaceMode?: 'grid' | 'fill';
}

export const DrawPage: React.FC = () => {
  const [currentTool, setCurrentTool] = useState<ToolId>('select');
  const [styleState, setStyleState] = useState<StyleState>({
    strokeColor: '#000000',
    fillColor: '#ffffff',
    strokeWidth: 2,
    fillTransparent: true,
  });

  const [algorithmState, setAlgorithmState] = useState<AlgorithmState>({
    line: 'bresenham',
    circle: 'midpoint',
    fill: 'boundary',
  });

  const [viewState, setViewState] = useState<ViewState>({
    gridEnabled: false,
    debugEnabled: false,
    rasterEnabled: true,
  });

  const [selectionState, setSelectionState] = useState<SelectionState>({
    selectedShapeType: null,
    selectedCount: 0,
    selectedSurfaceMode: undefined,
  });
  const [surfaceMode, setSurfaceMode] = useState<'grid' | 'fill'>('grid');

  const handleToolChange = useCallback((toolId: ToolId) => {
    setCurrentTool(toolId);
  }, []);

  const handleStyleChange = useCallback((partial: Partial<StyleState>) => {
    setStyleState(prev => {
      // 如果用户选择了新的填充色，自动关闭透明开关，避免出现“有色值但未填充”的困惑
      if (partial.fillColor !== undefined) {
        return { ...prev, ...partial, fillTransparent: false };
      }
      return { ...prev, ...partial };
    });
  }, []);

  const handleAlgorithmChange = useCallback((partial: Partial<AlgorithmState>) => {
    setAlgorithmState(prev => ({ ...prev, ...partial }));
  }, []);

  const handleViewChange = useCallback((partial: Partial<ViewState>) => {
    setViewState(prev => ({ ...prev, ...partial }));
  }, []);

  const handleSelectionChange = useCallback((selection: SelectionState) => {
    setSelectionState(selection);
  }, []);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // 初始化 legacy 绘图核心，并获取操作接口
  const {
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
  } = useLegacyDrawingCore({
      canvasRef,
      onSelectionChange: handleSelectionChange,
      onToolAutoSwitch: (toolId) => {
        // 自动切换到对应的工具
        setCurrentTool(toolId);
      },
    });

  // 同步当前工具到 legacy
  useEffect(() => {
    setTool(currentTool);
  }, [currentTool, setTool]);

  // 同步样式
  useEffect(() => {
    setStyle(styleState);
  }, [styleState, setStyle]);

  // 同步算法
  useEffect(() => {
    setAlgorithms(algorithmState);
  }, [algorithmState, setAlgorithms]);

  // 同步视图选项
  useEffect(() => {
    setViewOptions(viewState);
  }, [viewState, setViewOptions]);

  // 当选中曲面时，同步面板的模式显示
  useEffect(() => {
    if (selectionState.selectedSurfaceMode) {
      setSurfaceMode(selectionState.selectedSurfaceMode);
    }
  }, [selectionState.selectedSurfaceMode]);

  const handleSurfaceModeChange = useCallback(
    (mode: 'grid' | 'fill') => {
      setSurfaceMode(mode);
      // 联动填充状态：填充模式确保有色彩，网格模式切回透明
      setStyleState(prev => {
        if (mode === 'fill') {
          const nextColor = prev.fillTransparent ? '#cccccc' : prev.fillColor;
          return { ...prev, fillTransparent: false, fillColor: nextColor };
        }
        return { ...prev, fillTransparent: true };
      });
      setSurfaceOptions({ mode });
    },
    [setSurfaceOptions],
  );

  const handleAction = useCallback(
    (action: 'undo' | 'redo' | 'clear' | 'export' | 'rotateLeft' | 'rotateRight' | 'scaleDown' | 'scaleUp') => {
      switch (action) {
        case 'undo':
          undo();
          break;
        case 'redo':
          redo();
          break;
        case 'clear':
          clear();
          break;
        case 'export':
          exportPng();
          break;
        case 'rotateLeft':
        case 'rotateRight':
        case 'scaleDown':
        case 'scaleUp':
          transform(action);
          break;
        default:
          break;
      }
    },
    [undo, redo, clear, exportPng, transform],
  );

  // 键盘快捷键：数字键 / 字母键切换工具（只在未按 Ctrl/Cmd 时生效）
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifierKey = isMac ? e.metaKey : e.ctrlKey;
      if (modifierKey) return;

      const key = e.key;
      const toolMap: Record<string, ToolId> = {
        '1': 'select',
        '2': 'point',
        '3': 'line',
        '4': 'rect',
        '5': 'circle',
        '6': 'polygon',
        '7': 'brush',
        '8': 'fill',
        '9': 'eraser',
        b: 'bezierCurve',
        B: 'bezierCurve',
        s: 'bsplineCurve',
        S: 'bsplineCurve',
        m: 'bezierSurface',
        M: 'bezierSurface',
      };

      const mapped = toolMap[key];
      if (mapped) {
        e.preventDefault();
        setCurrentTool(mapped);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="draw-page">
      <Toolbar
        currentTool={currentTool}
        onToolChange={handleToolChange}
        styleState={styleState}
        onStyleChange={handleStyleChange}
        algorithmState={algorithmState}
        onAlgorithmChange={handleAlgorithmChange}
        viewState={viewState}
        onViewChange={handleViewChange}
        selectionState={selectionState}
        surfaceMode={surfaceMode}
        onSurfaceModeChange={handleSurfaceModeChange}
        onAction={handleAction}
        onStyleChangeComplete={saveState}
      />
      <CanvasPane
        canvasRef={canvasRef}
        viewState={viewState}
      />
      <TourGuide />
    </div>
  );
};

export default DrawPage;



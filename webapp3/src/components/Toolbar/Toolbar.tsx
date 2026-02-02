import React from 'react';
import type {
  AlgorithmState,
  SelectionState,
  StyleState,
  ToolId,
  ViewState,
} from '../../pages/DrawPage';

export interface ToolbarProps {
  currentTool: ToolId;
  onToolChange: (tool: ToolId) => void;
  styleState: StyleState;
  onStyleChange: (partial: Partial<StyleState>) => void;
  algorithmState: AlgorithmState;
  onAlgorithmChange: (partial: Partial<AlgorithmState>) => void;
  viewState: ViewState;
  onViewChange: (partial: Partial<ViewState>) => void;
  selectionState: SelectionState;
  surfaceMode: 'grid' | 'fill';
  onSurfaceModeChange: (mode: 'grid' | 'fill') => void;
  onAction: (action: 'undo' | 'redo' | 'clear' | 'export') => void;
  onStyleChangeComplete?: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  currentTool,
  onToolChange,
  styleState,
  onStyleChange,
  algorithmState,
  onAlgorithmChange,
  viewState,
  onViewChange,
  selectionState,
  surfaceMode,
  onSurfaceModeChange,
  onAction,
  onStyleChangeComplete,
}) => {
  const handleToolClick = (tool: ToolId) => {
    onToolChange(tool);
  };

  const curveToolIds: ToolId[] = ['bezierCurve', 'bsplineCurve', 'bezierSurface'];
  const curveShapeTypes = ['bezier_curve', 'bspline_curve', 'bezier_surface'];
  const transformVisible =
    curveToolIds.includes(currentTool) ||
    (selectionState.selectedShapeType !== null &&
      curveShapeTypes.includes(selectionState.selectedShapeType));

  return (
    <div className="toolbar">
      {/* 第一行：常用工具 */}
      <div className="toolbar-row">
        {/* 工具选择 */}
        <div className="toolbar-section">
          {(
            [
              ['select', '👆', '选择'],
              ['point', '⚫', '点'],
              ['line', '📏', '直线'],
              ['rect', '▭', '矩形'],
              ['circle', '⭕', '圆形'],
              ['polygon', '⬡', '多边'],
              ['bezierCurve', '♾️', 'Bézier'],
              ['bsplineCurve', '🌀', 'B 样条'],
              ['bezierSurface', '🧊', '曲面'],
              ['brush', '🖌️', '画笔'],
              ['fill', '🪣', '填充'],
              ['eraser', '🧹', '橡皮擦'],
            ] as [ToolId, string, string][]
          ).map(([id, icon, label]) => (
            <button
              key={id}
              className={`tool-btn ${currentTool === id ? 'active' : ''}`}
              type="button"
              onClick={() => handleToolClick(id)}
            >
              <span className="tool-icon">{icon}</span>
              <span className="tool-label">{label}</span>
            </button>
          ))}
        </div>

        {/* 颜色控制 */}
        <div className="toolbar-section">
          <div className="color-group" title="描边颜色">
            <div className="color-picker">
              <div className="color-preview" style={{ backgroundColor: styleState.strokeColor }}></div>
              <input
                type="color"
                value={styleState.strokeColor}
                onChange={e => onStyleChange({ strokeColor: e.target.value })}
                onMouseUp={() => {
                  // 不检查工具类型，只要有选中图形就保存
                  if (selectionState.selectedCount > 0 && onStyleChangeComplete) {
                    onStyleChangeComplete();
                  }
                }}
              />
            </div>
            <span className="color-label">描边</span>
          </div>
          <div className="color-group" title="填充颜色">
            <div className="color-picker">
              <div className="color-preview" style={{ backgroundColor: styleState.fillColor }}></div>
              <input
                type="color"
                value={styleState.fillColor}
                onChange={e => onStyleChange({ fillColor: e.target.value, fillTransparent: false })}
                onMouseUp={() => {
                  // 不检查工具类型，只要有选中图形就保存
                  if (selectionState.selectedCount > 0 && onStyleChangeComplete) {
                    onStyleChangeComplete();
                  }
                }}
              />
            </div>
            <span className="color-label">填充</span>
          </div>
          <label className="checkbox-control">
            <input
              type="checkbox"
              checked={styleState.fillTransparent}
              onChange={e =>
                onStyleChange({
                  fillTransparent: e.target.checked,
                })
              }
            />
            <span>透明</span>
          </label>
        </div>

        {/* 线宽控制 */}
        <div className="toolbar-section">
          <div className="slider-control">
            <span className="slider-label">{styleState.strokeWidth}px</span>
            <input
              type="range"
              min={1}
              max={20}
              value={styleState.strokeWidth}
              onChange={e => onStyleChange({ strokeWidth: Number(e.target.value) })}
              onMouseUp={() => {
                // 当用户松开鼠标时，如果有选中图形，保存历史记录
                // 不检查工具类型，因为即使刚绘制完图形，工具可能还是绘制工具，但图形已被选中
                if (selectionState.selectedCount > 0 && onStyleChangeComplete) {
                  onStyleChangeComplete();
                }
              }}
              onTouchEnd={() => {
                // 触摸设备支持
                if (selectionState.selectedCount > 0 && onStyleChangeComplete) {
                  onStyleChangeComplete();
                }
              }}
            />
          </div>
        </div>

        {/* 基本操作按钮 */}
        <div className="toolbar-section">
          <button className="tool-btn" type="button" onClick={() => onAction('undo')}>
            <span className="tool-icon">↩️</span>
            <span className="tool-label">撤销</span>
          </button>
          <button className="tool-btn" type="button" onClick={() => onAction('redo')}>
            <span className="tool-icon">↪️</span>
            <span className="tool-label">重做</span>
          </button>
          <button className="tool-btn" type="button" onClick={() => onAction('clear')}>
            <span className="tool-icon">🗑️</span>
            <span className="tool-label">清空</span>
          </button>
          <button className="tool-btn" type="button" onClick={() => onAction('export')}>
            <span className="tool-icon">💾</span>
            <span className="tool-label">导出</span>
          </button>
        </div>
      </div>

      {/* 第二行：高级功能 */}
      <div className="toolbar-row">
        {/* 算法选择 */}
        <div className="toolbar-section">
          {currentTool === 'line' && (
            <div className="algorithm-section">
              <span className="algorithm-label">线算法:</span>
              <select
                className="algorithm-selector"
                value={algorithmState.line}
                onChange={e => onAlgorithmChange({ line: e.target.value })}
              >
                <option value="bresenham">Bresenham</option>
                <option value="dda">DDA</option>
                <option value="midpoint">中点</option>
                <option value="canvas">Canvas</option>
              </select>
            </div>
          )}
          {currentTool === 'circle' && (
            <div className="algorithm-section">
              <span className="algorithm-label">圆算法:</span>
              <select
                className="algorithm-selector"
                value={algorithmState.circle}
                onChange={e => onAlgorithmChange({ circle: e.target.value })}
              >
                <option value="midpoint">中点</option>
                <option value="canvas">Canvas</option>
              </select>
            </div>
          )}
          {currentTool === 'fill' && (
            <div className="algorithm-section">
              <span className="algorithm-label">填充:</span>
              <select
                className="algorithm-selector"
                value={algorithmState.fill}
                onChange={e => onAlgorithmChange({ fill: e.target.value })}
              >
                <option value="boundary">边界填充</option>
                <option value="canvas">Canvas</option>
              </select>
            </div>
          )}
          {currentTool === 'bezierSurface' && (
            <div className="algorithm-section">
              <span className="algorithm-label">曲面模式:</span>
              <select
                className="algorithm-selector"
                value={surfaceMode}
                onChange={e => onSurfaceModeChange(e.target.value as 'grid' | 'fill')}
              >
                <option value="grid">网格</option>
                <option value="fill">填充</option>
              </select>
            </div>
          )}
        </div>

        {/* 变换操作（条件显示） */}
        {transformVisible && (
          <div className="toolbar-section">
            <button className="tool-btn" type="button" onClick={() => onAction('rotateLeft')}>
              <span className="tool-icon">⟲</span>
              <span className="tool-label">逆旋</span>
            </button>
            <button className="tool-btn" type="button" onClick={() => onAction('rotateRight')}>
              <span className="tool-icon">⟳</span>
              <span className="tool-label">顺旋</span>
            </button>
            <button className="tool-btn" type="button" onClick={() => onAction('scaleDown')}>
              <span className="tool-icon">➖</span>
              <span className="tool-label">缩小</span>
            </button>
            <button className="tool-btn" type="button" onClick={() => onAction('scaleUp')}>
              <span className="tool-icon">➕</span>
              <span className="tool-label">放大</span>
            </button>
          </div>
        )}

        {/* 视图控制 */}
        <div className="toolbar-section">
          <label className="checkbox-control">
            <input
              type="checkbox"
              checked={viewState.gridEnabled}
              onChange={e => onViewChange({ gridEnabled: e.target.checked })}
            />
            <span>网格</span>
          </label>
          <label className="checkbox-control">
            <input
              type="checkbox"
              checked={viewState.debugEnabled}
              onChange={e => onViewChange({ debugEnabled: e.target.checked })}
            />
            <span>调试</span>
          </label>
          <label className="checkbox-control">
            <input
              type="checkbox"
              checked={viewState.rasterEnabled}
              onChange={e => onViewChange({ rasterEnabled: e.target.checked })}
            />
            <span>光栅化</span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default Toolbar;



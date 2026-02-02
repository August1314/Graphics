import React from 'react';
import type { ViewState } from '../../pages/DrawPage';

export interface CanvasPaneProps {
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  viewState: ViewState;
}

export const CanvasPane: React.FC<CanvasPaneProps> = ({
  canvasRef,
  viewState,
}) => {
  return (
    <div className="canvas-container">
      <div className="canvas-card">
        <canvas id="draw-canvas" ref={canvasRef} width={1200} height={700} />
        <div
          id="react-debug-panel"
          className="debug-panel"
          style={{ display: viewState.debugEnabled ? 'block' : 'none' }}
        >
          <div className="debug-title">性能统计</div>
          <div id="react-debug-content" className="debug-content" />
        </div>
      </div>
    </div>
  );
};

export default CanvasPane;



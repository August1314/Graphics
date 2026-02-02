import React, { useState, useEffect, useRef } from 'react';
import './TourGuide.css';

export interface TourStep {
  id: string;
  target: string; // CSS selector
  title: string;
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  offset?: { x: number; y: number };
}

const tourSteps: TourStep[] = [
  {
    id: 'tools',
    target: '.toolbar-section:first-child',
    title: '绘图工具',
    content: '这里可以选择不同的绘图工具。点击工具按钮开始绘制，数字键 1-9 和字母键 B/S/M 可以快速切换工具。',
    position: 'bottom',
  },
  {
    id: 'colors',
    target: '.color-group:first-child',
    title: '颜色设置',
    content: '设置图形的描边和填充颜色。点击颜色选择器可以更改颜色，勾选"透明"可以让填充变为透明。',
    position: 'bottom',
  },
  {
    id: 'stroke-width',
    target: '.slider-control',
    title: '线宽控制',
    content: '拖动滑块调整线条的粗细。选中图形后也可以修改其线宽。',
    position: 'bottom',
  },
  {
    id: 'actions',
    target: '.toolbar-section:nth-child(4)',
    title: '基本操作',
    content: '撤销、重做、清空和导出功能。快捷键：Ctrl+Z 撤销，Ctrl+Y 重做，Ctrl+E 导出。',
    position: 'bottom',
  },
  {
    id: 'algorithms',
    target: '.algorithm-section',
    title: '算法选择',
    content: '选择不同的绘制算法。根据当前工具（直线/圆形/填充）会显示相应的算法选项。',
    position: 'bottom',
  },
  {
    id: 'transform',
    target: '.toolbar-row:last-child',
    title: '图形变换',
    content: '旋转和缩放选中的曲线或曲面。使用选择工具选中图形后，这些按钮会自动显示。',
    position: 'bottom',
  },
  {
    id: 'canvas',
    target: '#draw-canvas',
    title: '画布区域',
    content: '在这里绘制和编辑图形。点击并拖动可以绘制，使用选择工具可以移动和编辑已绘制的图形。',
    position: 'top',
  },
];

export const TourGuide: React.FC = () => {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightBox, setHighlightBox] = useState<{
    left: number;
    top: number;
    right: number;
    bottom: number;
    width: number;
    height: number;
  } | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isActive && currentStep < tourSteps.length) {
      updateHighlight();
      window.addEventListener('resize', updateHighlight);
      window.addEventListener('scroll', updateHighlight, true);
      return () => {
        window.removeEventListener('resize', updateHighlight);
        window.removeEventListener('scroll', updateHighlight, true);
      };
    }
  }, [isActive, currentStep]);

  const updateHighlight = () => {
    if (currentStep >= tourSteps.length) return;

    const step = tourSteps[currentStep];
    const isLastStep = currentStep === tourSteps.length - 1;
    
    // 等待 DOM 更新
    const checkElement = (retryCount = 0) => {
      const element = document.querySelector(step.target);

      if (element && element.getBoundingClientRect().width > 0) {
        const rect = element.getBoundingClientRect();
        // 添加一些边距，让高亮更明显
        const padding = 8;
        const adjustedRect = {
          left: rect.left - padding,
          top: rect.top - padding,
          right: rect.right + padding,
          bottom: rect.bottom + padding,
          width: rect.width + padding * 2,
          height: rect.height + padding * 2,
        };
        setHighlightBox(adjustedRect);
        
        // 更新 tooltip 位置
        if (tooltipRef.current) {
          positionTooltip(adjustedRect, step.position || 'bottom');
        }
      } else {
        // 如果是最后一步，重试几次，不要直接关闭
        if (isLastStep) {
          if (retryCount < 3) {
            // 重试最多3次，每次等待更长时间
            setTimeout(() => checkElement(retryCount + 1), 200 * (retryCount + 1));
          } else {
            // 如果还是找不到，显示在屏幕中央（作为后备方案）
            const centerRect = {
              left: window.innerWidth / 2 - 200,
              top: window.innerHeight / 2 - 150,
              right: window.innerWidth / 2 + 200,
              bottom: window.innerHeight / 2 + 150,
              width: 400,
              height: 300,
            };
            setHighlightBox(centerRect);
            if (tooltipRef.current) {
              positionTooltip(centerRect, 'top');
            }
          }
        } else {
          // 如果不是最后一步，尝试下一步
          if (currentStep < tourSteps.length - 1) {
            setCurrentStep(currentStep + 1);
          }
        }
      }
    };

    // 使用 requestAnimationFrame 确保 DOM 已更新
    requestAnimationFrame(() => {
      setTimeout(() => checkElement(0), 150);
    });
  };

  const positionTooltip = (
    rect: { left: number; top: number; right: number; bottom: number; width: number; height: number },
    position: string
  ) => {
    if (!tooltipRef.current) return;

    const tooltip = tooltipRef.current;
    const offset = 20;
    let top = 0;
    let left = 0;

    switch (position) {
      case 'top':
        top = rect.top - tooltip.offsetHeight - offset;
        left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
        break;
      case 'bottom':
        top = rect.bottom + offset;
        left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
        break;
      case 'left':
        top = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
        left = rect.left - tooltip.offsetWidth - offset;
        break;
      case 'right':
        top = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
        left = rect.right + offset;
        break;
    }

    // 确保 tooltip 在视口内
    const maxLeft = window.innerWidth - tooltip.offsetWidth - 20;
    const maxTop = window.innerHeight - tooltip.offsetHeight - 20;
    left = Math.max(20, Math.min(left, maxLeft));
    top = Math.max(20, Math.min(top, maxTop));

    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;
  };

  const startTour = () => {
    setIsActive(true);
    setCurrentStep(0);
    document.body.style.overflow = 'hidden';
  };

  const endTour = () => {
    setIsActive(false);
    setCurrentStep(0);
    setHighlightBox(null);
    document.body.style.overflow = '';
  };

  const nextStep = () => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      endTour();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const currentStepData = tourSteps[currentStep];

  if (!isActive) {
    return (
      <button className="tour-guide-trigger" onClick={startTour} title="开始引导教程">
        <span className="tour-icon">📖</span>
        <span className="tour-label">教程</span>
      </button>
    );
  }

  return (
    <>
      <div
        ref={overlayRef}
        className="tour-overlay"
        onClick={endTour}
        style={{
          clipPath: highlightBox
            ? `polygon(
                0% 0%,
                0% 100%,
                ${highlightBox.left}px 100%,
                ${highlightBox.left}px ${highlightBox.top}px,
                ${highlightBox.right}px ${highlightBox.top}px,
                ${highlightBox.right}px ${highlightBox.bottom}px,
                ${highlightBox.left}px ${highlightBox.bottom}px,
                ${highlightBox.left}px 100%,
                100% 100%,
                100% 0%
              )`
            : undefined,
        }}
      />
      {highlightBox && currentStepData && (
        <div
          ref={tooltipRef}
          className="tour-tooltip"
          data-position={currentStepData.position || 'bottom'}
        >
          <div className="tour-tooltip-header">
            <h3 className="tour-tooltip-title">{currentStepData.title}</h3>
            <button className="tour-tooltip-close" onClick={endTour}>
              ✕
            </button>
          </div>
          <div className="tour-tooltip-content">{currentStepData.content}</div>
          <div className="tour-tooltip-footer">
            <div className="tour-progress">
              {currentStep + 1} / {tourSteps.length}
            </div>
            <div className="tour-tooltip-actions">
              <button
                className="tour-btn tour-btn-secondary"
                onClick={prevStep}
                disabled={currentStep === 0}
              >
                上一步
              </button>
              {currentStep < tourSteps.length - 1 ? (
                <button className="tour-btn tour-btn-primary" onClick={nextStep}>
                  下一步
                </button>
              ) : (
                <button className="tour-btn tour-btn-primary" onClick={endTour}>
                  完成
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TourGuide;


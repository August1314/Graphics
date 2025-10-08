#!/usr/bin/env python3
"""
喷枪工具性能测试

测试目标：
1. 验证节流机制是否生效
2. 测试快速移动时的帧率
3. 确保达到 30 FPS 以上

运行方式：
    python tests/manual/test_spray_performance.py
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QPen

from app.core.tools.brush_tool import BrushTool


class PerformanceTestWindow(QMainWindow):
    """性能测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("喷枪性能测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建场景和视图
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        # 创建喷枪工具
        self.spray_tool = BrushTool(BrushTool.BrushType.SPRAY)
        pen = QPen(QColor("#FF0000"), 20.0)
        self.spray_tool.set_pen(pen)
        
        # 性能统计
        self.frame_times = []
        self.last_frame_time = 0
        self.test_running = False
        
        # 测试参数
        self.test_points = []
        self.current_point_index = 0
        
        # 生成测试路径（快速移动的圆形路径）
        self._generate_test_path()
        
        # 定时器用于自动测试
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self._run_test_step)
        
        print("=" * 60)
        print("喷枪性能测试")
        print("=" * 60)
        print("\n按空格键开始自动测试")
        print("测试将模拟快速移动的喷枪绘制\n")
    
    def _generate_test_path(self):
        """生成测试路径：一个大圆"""
        center_x, center_y = 400, 300
        radius = 200
        num_points = 100  # 100个点，模拟快速移动
        
        import math
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.test_points.append(QPointF(x, y))
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_Space and not self.test_running:
            self._start_test()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def _start_test(self):
        """开始性能测试"""
        print("\n开始测试...")
        print("-" * 60)
        
        self.test_running = True
        self.frame_times = []
        self.current_point_index = 0
        self.last_frame_time = time.perf_counter()
        
        # 模拟鼠标按下
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent
        
        first_point = self.test_points[0]
        mock_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            first_point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.spray_tool.on_press(self.scene, first_point, mock_event)
        
        # 启动定时器，模拟快速移动
        self.test_timer.start(1)  # 1ms 间隔，模拟极快移动
    
    def _run_test_step(self):
        """运行测试步骤"""
        if self.current_point_index >= len(self.test_points):
            self._finish_test()
            return
        
        # 记录帧时间
        current_time = time.perf_counter()
        if self.last_frame_time > 0:
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        
        # 模拟鼠标移动
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent
        
        point = self.test_points[self.current_point_index]
        mock_event = QMouseEvent(
            QEvent.Type.MouseMove,
            point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.spray_tool.on_move(self.scene, point, mock_event)
        
        self.current_point_index += 1
        
        # 显示进度
        if self.current_point_index % 10 == 0:
            progress = (self.current_point_index / len(self.test_points)) * 100
            print(f"进度: {progress:.0f}%", end="\r")
    
    def _finish_test(self):
        """完成测试并显示结果"""
        self.test_timer.stop()
        self.test_running = False
        
        # 模拟鼠标释放
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent
        
        last_point = self.test_points[-1]
        mock_event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            last_point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        self.spray_tool.on_release(self.scene, last_point, mock_event)
        
        # 计算性能指标
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            min_frame_time = min(self.frame_times)
            max_frame_time = max(self.frame_times)
            max_fps = 1.0 / min_frame_time if min_frame_time > 0 else 0
            min_fps = 1.0 / max_frame_time if max_frame_time > 0 else 0
            
            print("\n" + "-" * 60)
            print("测试结果:")
            print("-" * 60)
            print(f"总帧数: {len(self.frame_times)}")
            print(f"平均帧时间: {avg_frame_time*1000:.2f} ms")
            print(f"平均 FPS: {avg_fps:.1f}")
            print(f"最大 FPS: {max_fps:.1f}")
            print(f"最小 FPS: {min_fps:.1f}")
            print("-" * 60)
            
            # 判断是否达标
            if avg_fps >= 30:
                print("✅ 性能测试通过！平均 FPS >= 30")
            else:
                print(f"❌ 性能测试未通过。平均 FPS ({avg_fps:.1f}) < 30")
            
            print("\n按空格键重新测试，按 ESC 退出")
        else:
            print("\n测试数据不足")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = PerformanceTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

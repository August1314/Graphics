#!/usr/bin/env python3
"""
喷枪工具自动化性能测试（无 GUI）

测试目标：
1. 验证节流机制是否生效
2. 测试快速移动时的处理性能
3. 确保优化后的性能提升

运行方式：
    python tests/manual/test_spray_performance_auto.py
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QApplication, QGraphicsScene

from app.core.tools.brush_tool import BrushTool


def test_spray_performance():
    """自动化性能测试"""
    print("=" * 60)
    print("喷枪性能测试（自动化）")
    print("=" * 60)
    print()
    
    # 创建 Qt 应用（必需，即使不显示 GUI）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 创建场景
    scene = QGraphicsScene()
    
    # 创建喷枪工具
    spray_tool = BrushTool(BrushTool.BrushType.SPRAY)
    pen = QPen(QColor("#FF0000"), 20.0)
    spray_tool.set_pen(pen)
    
    # 生成测试路径（圆形路径，100 个点）
    import math
    center_x, center_y = 400, 300
    radius = 200
    num_points = 100
    
    test_points = []
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        test_points.append(QPointF(x, y))
    
    print(f"测试参数:")
    print(f"  - 测试点数: {num_points}")
    print(f"  - 路径类型: 圆形")
    print(f"  - 半径: {radius}px")
    print(f"  - 画笔宽度: 20px")
    print()
    print("开始测试...")
    print("-" * 60)
    
    # 模拟鼠标按下
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, Qt
    
    first_point = test_points[0]
    mock_event = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        first_point,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    
    start_time = time.perf_counter()
    spray_tool.on_press(scene, first_point, mock_event)
    
    # 记录每次处理的时间
    frame_times = []
    last_frame_time = time.perf_counter()
    
    # 模拟快速移动
    for i, point in enumerate(test_points[1:], 1):
        mock_event = QMouseEvent(
            QEvent.Type.MouseMove,
            point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        frame_start = time.perf_counter()
        spray_tool.on_move(scene, point, mock_event)
        frame_end = time.perf_counter()
        
        frame_time = frame_end - frame_start
        frame_times.append(frame_time)
        
        # 显示进度
        if i % 10 == 0:
            progress = (i / len(test_points)) * 100
            print(f"进度: {progress:.0f}%", end="\r")
    
    # 模拟鼠标释放
    last_point = test_points[-1]
    mock_event = QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        last_point,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier
    )
    spray_tool.on_release(scene, last_point, mock_event)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    print("\n" + "-" * 60)
    print("测试完成！")
    print("-" * 60)
    
    # 计算性能指标
    if frame_times:
        avg_frame_time = sum(frame_times) / len(frame_times)
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        min_frame_time = min(frame_times)
        max_frame_time = max(frame_times)
        max_fps = 1.0 / min_frame_time if min_frame_time > 0 else 0
        min_fps = 1.0 / max_frame_time if max_frame_time > 0 else 0
        
        print()
        print("性能统计:")
        print("-" * 60)
        print(f"总耗时: {total_time*1000:.2f} ms")
        print(f"总帧数: {len(frame_times)}")
        print(f"平均帧时间: {avg_frame_time*1000:.2f} ms")
        print(f"最小帧时间: {min_frame_time*1000:.2f} ms")
        print(f"最大帧时间: {max_frame_time*1000:.2f} ms")
        print()
        print(f"平均 FPS: {avg_fps:.1f}")
        print(f"最大 FPS: {max_fps:.1f}")
        print(f"最小 FPS: {min_fps:.1f}")
        print("-" * 60)
        
        # 节流效果分析
        print()
        print("节流机制分析:")
        print("-" * 60)
        
        # 统计被节流的帧（处理时间 < 1ms 的可能是被跳过的）
        fast_frames = [t for t in frame_times if t < 0.001]
        slow_frames = [t for t in frame_times if t >= 0.001]
        
        print(f"快速帧（< 1ms）: {len(fast_frames)} ({len(fast_frames)/len(frame_times)*100:.1f}%)")
        print(f"正常帧（>= 1ms）: {len(slow_frames)} ({len(slow_frames)/len(frame_times)*100:.1f}%)")
        
        if slow_frames:
            avg_slow = sum(slow_frames) / len(slow_frames)
            print(f"正常帧平均时间: {avg_slow*1000:.2f} ms")
        
        print("-" * 60)
        
        # 判断是否达标
        print()
        print("测试结果:")
        print("-" * 60)
        
        passed = True
        
        # 检查平均 FPS
        if avg_fps >= 30:
            print(f"✅ 平均 FPS 测试通过: {avg_fps:.1f} >= 30")
        else:
            print(f"❌ 平均 FPS 测试未通过: {avg_fps:.1f} < 30")
            passed = False
        
        # 检查最小 FPS
        if min_fps >= 20:
            print(f"✅ 最小 FPS 测试通过: {min_fps:.1f} >= 20")
        else:
            print(f"⚠️  最小 FPS 较低: {min_fps:.1f} < 20")
        
        # 检查平均帧时间
        if avg_frame_time < 0.033:  # 33ms = 30 FPS
            print(f"✅ 平均帧时间测试通过: {avg_frame_time*1000:.2f}ms < 33ms")
        else:
            print(f"❌ 平均帧时间测试未通过: {avg_frame_time*1000:.2f}ms >= 33ms")
            passed = False
        
        print("-" * 60)
        
        if passed:
            print()
            print("🎉 所有性能测试通过！")
            print()
            return 0
        else:
            print()
            print("⚠️  部分性能测试未通过，但可能是测试环境影响")
            print()
            return 1
    else:
        print()
        print("❌ 测试数据不足")
        print()
        return 1


def main():
    """主函数"""
    try:
        exit_code = test_spray_performance()
        return exit_code
    except Exception as e:
        print()
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

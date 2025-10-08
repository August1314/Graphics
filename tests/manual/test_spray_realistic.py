#!/usr/bin/env python3
"""
喷枪工具真实场景性能测试

模拟真实的绘制场景，包括：
1. 实际的场景渲染
2. 图元的创建和更新
3. 更真实的时间间隔

运行方式：
    python tests/manual/test_spray_realistic.py
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtCore import QPointF, QTimer, QEventLoop
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QApplication, QGraphicsScene

from app.core.tools.brush_tool import BrushTool


def test_spray_realistic():
    """真实场景性能测试"""
    print("=" * 60)
    print("喷枪性能测试（真实场景）")
    print("=" * 60)
    print()
    
    # 创建 Qt 应用
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 创建场景
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 800, 600)
    
    # 创建喷枪工具
    spray_tool = BrushTool(BrushTool.BrushType.SPRAY)
    pen = QPen(QColor("#FF0000"), 20.0)
    spray_tool.set_pen(pen)
    
    # 生成测试路径
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
    print(f"  - 模拟间隔: 5ms（模拟 200 Hz 鼠标）")
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
    
    # 记录性能数据
    frame_times = []
    actual_render_times = []  # 实际渲染的帧
    skipped_frames = 0
    
    # 模拟真实的鼠标移动（带时间间隔）
    for i, point in enumerate(test_points[1:], 1):
        # 模拟 5ms 间隔（200 Hz 鼠标）
        time.sleep(0.005)
        
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
        
        # 判断是否实际渲染（处理时间 > 0.1ms 认为是实际渲染）
        if frame_time > 0.0001:
            actual_render_times.append(frame_time)
        else:
            skipped_frames += 1
        
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
        
        print()
        print("整体性能统计:")
        print("-" * 60)
        print(f"总耗时: {total_time*1000:.2f} ms")
        print(f"总帧数: {len(frame_times)}")
        print(f"平均帧时间: {avg_frame_time*1000:.4f} ms")
        print()
        
        # 节流效果分析
        print("节流机制效果:")
        print("-" * 60)
        print(f"实际渲染帧数: {len(actual_render_times)}")
        print(f"跳过帧数: {skipped_frames}")
        print(f"节流率: {skipped_frames/len(frame_times)*100:.1f}%")
        print()
        
        if actual_render_times:
            avg_render_time = sum(actual_render_times) / len(actual_render_times)
            avg_render_fps = 1.0 / avg_render_time if avg_render_time > 0 else 0
            min_render_time = min(actual_render_times)
            max_render_time = max(actual_render_times)
            max_render_fps = 1.0 / min_render_time if min_render_time > 0 else 0
            min_render_fps = 1.0 / max_render_time if max_render_time > 0 else 0
            
            print("实际渲染性能:")
            print("-" * 60)
            print(f"平均渲染时间: {avg_render_time*1000:.2f} ms")
            print(f"最小渲染时间: {min_render_time*1000:.2f} ms")
            print(f"最大渲染时间: {max_render_time*1000:.2f} ms")
            print()
            print(f"平均渲染 FPS: {avg_render_fps:.1f}")
            print(f"最大渲染 FPS: {max_render_fps:.1f}")
            print(f"最小渲染 FPS: {min_render_fps:.1f}")
            print("-" * 60)
            
            # 判断是否达标
            print()
            print("测试结果:")
            print("-" * 60)
            
            passed = True
            
            # 检查节流率
            throttle_rate = skipped_frames / len(frame_times) * 100
            if throttle_rate >= 50:
                print(f"✅ 节流机制有效: {throttle_rate:.1f}% 的帧被跳过")
            else:
                print(f"⚠️  节流率较低: {throttle_rate:.1f}%")
            
            # 检查实际渲染 FPS
            if avg_render_fps >= 30:
                print(f"✅ 实际渲染 FPS 达标: {avg_render_fps:.1f} >= 30")
            else:
                print(f"❌ 实际渲染 FPS 未达标: {avg_render_fps:.1f} < 30")
                passed = False
            
            # 检查渲染时间
            if avg_render_time < 0.033:  # 33ms = 30 FPS
                print(f"✅ 平均渲染时间达标: {avg_render_time*1000:.2f}ms < 33ms")
            else:
                print(f"❌ 平均渲染时间未达标: {avg_render_time*1000:.2f}ms >= 33ms")
                passed = False
            
            # 检查场景图元数量
            item_count = len(scene.items())
            print(f"ℹ️  场景图元数量: {item_count}")
            
            print("-" * 60)
            
            if passed:
                print()
                print("🎉 所有性能测试通过！")
                print()
                print("优化效果总结:")
                print(f"  - 节流机制成功减少了 {throttle_rate:.1f}% 的不必要处理")
                print(f"  - 实际渲染保持在 {avg_render_fps:.1f} FPS")
                print(f"  - 平均渲染时间仅 {avg_render_time*1000:.2f} ms")
                print()
                return 0
            else:
                print()
                print("⚠️  部分性能测试未通过")
                print()
                return 1
        else:
            print("⚠️  没有实际渲染帧，可能节流过度")
            return 1
    else:
        print()
        print("❌ 测试数据不足")
        print()
        return 1


def main():
    """主函数"""
    try:
        exit_code = test_spray_realistic()
        return exit_code
    except Exception as e:
        print()
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

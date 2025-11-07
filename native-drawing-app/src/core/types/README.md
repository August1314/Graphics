# 核心数据类型

本目录包含绘图系统使用的所有基础数据类型。

## 类型概览

### Point / PointF
- **Point**: 整数坐标点，用于像素级操作
- **PointF**: 浮点坐标点，用于精确计算

**功能**:
- 基本运算（加减乘除）
- 距离计算（欧几里得距离、曼哈顿距离）
- 向量运算（点积、叉积、归一化）
- JSON 序列化

### Color
RGBA 颜色表示，每个通道 0-255。

**功能**:
- 多种颜色格式转换（HEX、RGB、RGBA、HSV）
- 颜色混合和 alpha 混合
- 亮度计算
- 预定义颜色常量
- JSON 序列化

### BoundingBox
轴对齐包围盒（AABB），用于快速碰撞检测。

**功能**:
- 点和包围盒的包含检测
- 包围盒相交检测
- 交集和并集计算
- 扩展和收缩
- 平移和缩放
- JSON 序列化

### Matrix
2D 仿射变换矩阵（3x3，存储前两行）。

**功能**:
- 平移、缩放、旋转变换
- 矩阵乘法
- 点和向量变换
- 逆矩阵计算
- 提取变换参数（缩放、旋转、平移）
- JSON 序列化

## 枚举类型

### StrokeStyle
线条样式：实线、虚线、点线等。

### FillRule
填充规则：非零规则、奇偶规则。

### LineCap / LineJoin
线条端点和连接样式。

### RasterAlgorithm
光栅化算法类型：Bresenham、DDA、中点、原生 API。

### FillAlgorithm
填充算法类型：扫描线、泛洪填充、原生 API。

## 使用示例

```cpp
#include "types.h"

using namespace drawing;

// 创建点
Point p1(100, 200);
Point p2(300, 400);

// 计算距离
float distance = p1.distanceTo(p2);

// 创建颜色
Color red = Color::Red;
Color custom = Color::fromHex("#FF5733");
Color hsv = Color::fromHSV(120, 0.5f, 0.8f);

// 颜色混合
Color blended = red.blend(custom, 0.5f);

// 创建包围盒
BoundingBox box = BoundingBox::fromPoints(p1, p2);

// 碰撞检测
if (box.contains(Point(150, 250))) {
    // 点在包围盒内
}

// 创建变换矩阵
Matrix transform;
transform.translate(100, 50);
transform.rotate(M_PI / 4);  // 旋转 45 度
transform.scale(2.0f);

// 变换点
Point transformed = transform.transform(p1);

// JSON 序列化
nlohmann::json json = p1.toJson();
Point restored = Point::fromJson(json);
```

## 性能考虑

- **Point vs PointF**: 整数运算比浮点运算快，优先使用 Point
- **BoundingBox**: 用于快速剔除，避免昂贵的精确碰撞检测
- **Matrix**: 变换可以组合，避免重复计算

## 线程安全

所有类型都是值类型（struct），不包含可变状态，因此是线程安全的。

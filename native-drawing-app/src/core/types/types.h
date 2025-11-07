#pragma once

/**
 * @file types.h
 * @brief 核心数据类型定义
 * 
 * 包含绘图系统使用的所有基础数据类型。
 */

#include "point.h"
#include "color.h"
#include "bounding_box.h"
#include "matrix.h"

namespace drawing {

/**
 * @brief 线条样式枚举
 */
enum class StrokeStyle {
    Solid,      // 实线
    Dashed,     // 虚线
    Dotted,     // 点线
    DashDot,    // 点划线
    DashDotDot  // 双点划线
};

/**
 * @brief 填充规则枚举
 */
enum class FillRule {
    NonZero,    // 非零规则
    EvenOdd     // 奇偶规则
};

/**
 * @brief 线条端点样式
 */
enum class LineCap {
    Butt,       // 平头
    Round,      // 圆头
    Square      // 方头
};

/**
 * @brief 线条连接样式
 */
enum class LineJoin {
    Miter,      // 尖角
    Round,      // 圆角
    Bevel       // 斜角
};

/**
 * @brief 光栅化算法类型
 */
enum class RasterAlgorithm {
    Bresenham,  // Bresenham 算法
    DDA,        // DDA 算法
    Midpoint,   // 中点算法
    Native      // 使用原生 API（Skia）
};

/**
 * @brief 填充算法类型
 */
enum class FillAlgorithm {
    Scanline,   // 扫描线填充
    FloodFill,  // 泛洪填充
    Native      // 使用原生 API
};

/**
 * @brief 性能指标结构
 */
struct PerformanceMetrics {
    std::string algorithmName;
    int64_t executionTimeNs;  // 执行时间（纳秒）
    int pixelCount;           // 绘制的像素数量
    double pixelsPerSecond;   // 每秒绘制的像素数

    PerformanceMetrics()
        : algorithmName("Unknown")
        , executionTimeNs(0)
        , pixelCount(0)
        , pixelsPerSecond(0.0) {}

    PerformanceMetrics(const std::string& name, int64_t timeNs, int pixels)
        : algorithmName(name)
        , executionTimeNs(timeNs)
        , pixelCount(pixels)
        , pixelsPerSecond(pixels * 1e9 / timeNs) {}

    nlohmann::json toJson() const {
        return {
            {"algorithm", algorithmName},
            {"executionTimeNs", executionTimeNs},
            {"executionTimeMs", executionTimeNs / 1e6},
            {"pixelCount", pixelCount},
            {"pixelsPerSecond", pixelsPerSecond}
        };
    }
};

} // namespace drawing

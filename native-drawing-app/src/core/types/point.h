#pragma once

#include <cmath>
#include <nlohmann/json.hpp>

namespace drawing {

/**
 * @brief 2D 点结构
 * 
 * 表示二维空间中的一个点，使用整数坐标。
 */
struct Point {
    int x;
    int y;

    // 构造函数
    Point() : x(0), y(0) {}
    Point(int x, int y) : x(x), y(y) {}

    // 运算符重载
    Point operator+(const Point& other) const {
        return Point(x + other.x, y + other.y);
    }

    Point operator-(const Point& other) const {
        return Point(x - other.x, y - other.y);
    }

    Point operator*(float scalar) const {
        return Point(static_cast<int>(x * scalar), static_cast<int>(y * scalar));
    }

    Point operator/(float scalar) const {
        return Point(static_cast<int>(x / scalar), static_cast<int>(y / scalar));
    }

    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }

    bool operator!=(const Point& other) const {
        return !(*this == other);
    }

    // 工具方法
    
    /**
     * @brief 计算到另一个点的距离
     */
    float distanceTo(const Point& other) const {
        int dx = x - other.x;
        int dy = y - other.y;
        return std::sqrt(static_cast<float>(dx * dx + dy * dy));
    }

    /**
     * @brief 计算到另一个点的曼哈顿距离
     */
    int manhattanDistanceTo(const Point& other) const {
        return std::abs(x - other.x) + std::abs(y - other.y);
    }

    /**
     * @brief 计算向量长度
     */
    float length() const {
        return std::sqrt(static_cast<float>(x * x + y * y));
    }

    /**
     * @brief 归一化向量
     */
    Point normalized() const {
        float len = length();
        if (len == 0.0f) return Point(0, 0);
        return Point(
            static_cast<int>(x / len),
            static_cast<int>(y / len)
        );
    }

    /**
     * @brief 点积
     */
    int dot(const Point& other) const {
        return x * other.x + y * other.y;
    }

    /**
     * @brief 叉积（2D 中返回标量）
     */
    int cross(const Point& other) const {
        return x * other.y - y * other.x;
    }

    // JSON 序列化
    nlohmann::json toJson() const {
        return {
            {"x", x},
            {"y", y}
        };
    }

    static Point fromJson(const nlohmann::json& json) {
        return Point(
            json.value("x", 0),
            json.value("y", 0)
        );
    }
};

// 浮点数版本的点（用于精确计算）
struct PointF {
    float x;
    float y;

    PointF() : x(0.0f), y(0.0f) {}
    PointF(float x, float y) : x(x), y(y) {}
    PointF(const Point& p) : x(static_cast<float>(p.x)), y(static_cast<float>(p.y)) {}

    Point toPoint() const {
        return Point(static_cast<int>(x), static_cast<int>(y));
    }

    PointF operator+(const PointF& other) const {
        return PointF(x + other.x, y + other.y);
    }

    PointF operator-(const PointF& other) const {
        return PointF(x - other.x, y - other.y);
    }

    PointF operator*(float scalar) const {
        return PointF(x * scalar, y * scalar);
    }

    PointF operator/(float scalar) const {
        return PointF(x / scalar, y / scalar);
    }

    float length() const {
        return std::sqrt(x * x + y * y);
    }

    PointF normalized() const {
        float len = length();
        if (len == 0.0f) return PointF(0.0f, 0.0f);
        return PointF(x / len, y / len);
    }
};

} // namespace drawing

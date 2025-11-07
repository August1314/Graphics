#pragma once

#include "point.h"
#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>

namespace drawing {

/**
 * @brief 轴对齐包围盒（AABB）
 * 
 * 表示一个矩形区域，用于快速碰撞检测和空间查询。
 */
struct BoundingBox {
    int x;       // 左上角 x 坐标
    int y;       // 左上角 y 坐标
    int width;   // 宽度
    int height;  // 高度

    // 构造函数
    BoundingBox() : x(0), y(0), width(0), height(0) {}
    BoundingBox(int x, int y, int width, int height)
        : x(x), y(y), width(width), height(height) {}

    /**
     * @brief 从两个点创建包围盒
     */
    static BoundingBox fromPoints(const Point& p1, const Point& p2) {
        int minX = std::min(p1.x, p2.x);
        int minY = std::min(p1.y, p2.y);
        int maxX = std::max(p1.x, p2.x);
        int maxY = std::max(p1.y, p2.y);
        return BoundingBox(minX, minY, maxX - minX, maxY - minY);
    }

    /**
     * @brief 从点集创建包围盒
     */
    static BoundingBox fromPointList(const std::vector<Point>& points) {
        if (points.empty()) {
            return BoundingBox();
        }

        int minX = points[0].x;
        int minY = points[0].y;
        int maxX = points[0].x;
        int maxY = points[0].y;

        for (const auto& p : points) {
            minX = std::min(minX, p.x);
            minY = std::min(minY, p.y);
            maxX = std::max(maxX, p.x);
            maxY = std::max(maxY, p.y);
        }

        return BoundingBox(minX, minY, maxX - minX, maxY - minY);
    }

    // 属性访问
    int left() const { return x; }
    int top() const { return y; }
    int right() const { return x + width; }
    int bottom() const { return y + height; }
    
    Point topLeft() const { return Point(x, y); }
    Point topRight() const { return Point(x + width, y); }
    Point bottomLeft() const { return Point(x, y + height); }
    Point bottomRight() const { return Point(x + width, y + height); }
    Point center() const { return Point(x + width / 2, y + height / 2); }

    int area() const { return width * height; }
    bool isEmpty() const { return width <= 0 || height <= 0; }
    bool isValid() const { return width > 0 && height > 0; }

    /**
     * @brief 检查点是否在包围盒内
     */
    bool contains(const Point& point) const {
        return point.x >= x && point.x <= x + width &&
               point.y >= y && point.y <= y + height;
    }

    /**
     * @brief 检查点是否在包围盒内（严格，不包括边界）
     */
    bool containsStrict(const Point& point) const {
        return point.x > x && point.x < x + width &&
               point.y > y && point.y < y + height;
    }

    /**
     * @brief 检查另一个包围盒是否完全在此包围盒内
     */
    bool contains(const BoundingBox& other) const {
        return other.x >= x && other.y >= y &&
               other.right() <= right() && other.bottom() <= bottom();
    }

    /**
     * @brief 检查是否与另一个包围盒相交
     */
    bool intersects(const BoundingBox& other) const {
        return !(other.x > right() || other.right() < x ||
                 other.y > bottom() || other.bottom() < y);
    }

    /**
     * @brief 计算与另一个包围盒的交集
     */
    BoundingBox intersection(const BoundingBox& other) const {
        int x1 = std::max(x, other.x);
        int y1 = std::max(y, other.y);
        int x2 = std::min(right(), other.right());
        int y2 = std::min(bottom(), other.bottom());

        if (x2 < x1 || y2 < y1) {
            return BoundingBox(); // 无交集
        }

        return BoundingBox(x1, y1, x2 - x1, y2 - y1);
    }

    /**
     * @brief 计算与另一个包围盒的并集
     */
    BoundingBox unionWith(const BoundingBox& other) const {
        if (isEmpty()) return other;
        if (other.isEmpty()) return *this;

        int x1 = std::min(x, other.x);
        int y1 = std::min(y, other.y);
        int x2 = std::max(right(), other.right());
        int y2 = std::max(bottom(), other.bottom());

        return BoundingBox(x1, y1, x2 - x1, y2 - y1);
    }

    /**
     * @brief 扩展包围盒以包含指定点
     */
    BoundingBox& expandToInclude(const Point& point) {
        if (isEmpty()) {
            x = point.x;
            y = point.y;
            width = 0;
            height = 0;
            return *this;
        }

        int x1 = std::min(x, point.x);
        int y1 = std::min(y, point.y);
        int x2 = std::max(right(), point.x);
        int y2 = std::max(bottom(), point.y);

        x = x1;
        y = y1;
        width = x2 - x1;
        height = y2 - y1;

        return *this;
    }

    /**
     * @brief 扩展包围盒以包含另一个包围盒
     */
    BoundingBox& expandToInclude(const BoundingBox& other) {
        if (other.isEmpty()) return *this;
        if (isEmpty()) {
            *this = other;
            return *this;
        }

        int x1 = std::min(x, other.x);
        int y1 = std::min(y, other.y);
        int x2 = std::max(right(), other.right());
        int y2 = std::max(bottom(), other.bottom());

        x = x1;
        y = y1;
        width = x2 - x1;
        height = y2 - y1;

        return *this;
    }

    /**
     * @brief 向外扩展包围盒（增加边距）
     */
    BoundingBox expanded(int margin) const {
        return BoundingBox(
            x - margin,
            y - margin,
            width + 2 * margin,
            height + 2 * margin
        );
    }

    /**
     * @brief 向内收缩包围盒
     */
    BoundingBox shrunk(int margin) const {
        return BoundingBox(
            x + margin,
            y + margin,
            std::max(0, width - 2 * margin),
            std::max(0, height - 2 * margin)
        );
    }

    /**
     * @brief 平移包围盒
     */
    BoundingBox translated(int dx, int dy) const {
        return BoundingBox(x + dx, y + dy, width, height);
    }

    /**
     * @brief 缩放包围盒
     */
    BoundingBox scaled(float scale) const {
        Point c = center();
        int newWidth = static_cast<int>(width * scale);
        int newHeight = static_cast<int>(height * scale);
        return BoundingBox(
            c.x - newWidth / 2,
            c.y - newHeight / 2,
            newWidth,
            newHeight
        );
    }

    // 运算符重载
    bool operator==(const BoundingBox& other) const {
        return x == other.x && y == other.y &&
               width == other.width && height == other.height;
    }

    bool operator!=(const BoundingBox& other) const {
        return !(*this == other);
    }

    // JSON 序列化
    nlohmann::json toJson() const {
        return {
            {"x", x},
            {"y", y},
            {"width", width},
            {"height", height}
        };
    }

    static BoundingBox fromJson(const nlohmann::json& json) {
        return BoundingBox(
            json.value("x", 0),
            json.value("y", 0),
            json.value("width", 0),
            json.value("height", 0)
        );
    }
};

} // namespace drawing

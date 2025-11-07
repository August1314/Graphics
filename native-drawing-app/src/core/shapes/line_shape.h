#pragma once

#include "shape.h"

namespace drawing {

/**
 * @brief 直线图形
 * 
 * 表示从点 (x1, y1) 到点 (x2, y2) 的直线段。
 */
class LineShape : public Shape {
public:
    LineShape() {
        id_ = generateId("line");
        filled_ = false;  // 直线不能填充
    }

    LineShape(int x1, int y1, int x2, int y2) : LineShape() {
        x1_ = x1;
        y1_ = y1;
        x2_ = x2;
        y2_ = y2;
    }

    LineShape(const Point& p1, const Point& p2)
        : LineShape(p1.x, p1.y, p2.x, p2.y) {}

    // 属性访问
    int getX1() const { return x1_; }
    void setX1(int x) { x1_ = x; }

    int getY1() const { return y1_; }
    void setY1(int y) { y1_ = y; }

    int getX2() const { return x2_; }
    void setX2(int x) { x2_ = x; }

    int getY2() const { return y2_; }
    void setY2(int y) { y2_ = y; }

    Point getStart() const { return Point(x1_, y1_); }
    void setStart(const Point& point) {
        x1_ = point.x;
        y1_ = point.y;
    }

    Point getEnd() const { return Point(x2_, y2_); }
    void setEnd(const Point& point) {
        x2_ = point.x;
        y2_ = point.y;
    }

    float getLength() const {
        return getStart().distanceTo(getEnd());
    }

    // Shape 接口实现
    std::string getType() const override {
        return "line";
    }

    void render(RenderingEngine& engine) override;

    BoundingBox getBounds() const override {
        int margin = static_cast<int>(strokeWidth_) + 2;
        BoundingBox box = BoundingBox::fromPoints(getStart(), getEnd());
        return box.expanded(margin);
    }

    bool hitTest(const Point& point, int tolerance = 5) const override {
        // 点到线段的距离
        Point p1(x1_, y1_);
        Point p2(x2_, y2_);
        Point p = point;

        // 向量
        Point v = p2 - p1;
        Point w = p - p1;

        // 计算投影参数 t
        float c1 = w.dot(v);
        if (c1 <= 0) {
            // 最近点是 p1
            return p.distanceTo(p1) <= tolerance + strokeWidth_;
        }

        float c2 = v.dot(v);
        if (c1 >= c2) {
            // 最近点是 p2
            return p.distanceTo(p2) <= tolerance + strokeWidth_;
        }

        // 最近点在线段上
        float t = c1 / c2;
        Point closest = p1 + v * t;
        return p.distanceTo(closest) <= tolerance + strokeWidth_;
    }

    std::unique_ptr<Shape> clone() const override {
        auto cloned = std::make_unique<LineShape>(x1_, y1_, x2_, y2_);
        cloned->strokeColor_ = strokeColor_;
        cloned->strokeWidth_ = strokeWidth_;
        cloned->strokeStyle_ = strokeStyle_;
        cloned->opacity_ = opacity_;
        cloned->transform_ = transform_;
        cloned->zIndex_ = zIndex_;
        cloned->visible_ = visible_;
        cloned->locked_ = locked_;
        return cloned;
    }

    nlohmann::json toJson() const override {
        auto json = serializeCommonProperties();
        json["properties"] = {
            {"x1", x1_},
            {"y1", y1_},
            {"x2", x2_},
            {"y2", y2_}
        };
        return json;
    }

    static std::unique_ptr<LineShape> fromJson(const nlohmann::json& json) {
        auto shape = std::make_unique<LineShape>();
        shape->deserializeCommonProperties(json);
        
        if (json.contains("properties")) {
            const auto& props = json["properties"];
            shape->x1_ = props.value("x1", 0);
            shape->y1_ = props.value("y1", 0);
            shape->x2_ = props.value("x2", 0);
            shape->y2_ = props.value("y2", 0);
        }
        
        return shape;
    }

private:
    int x1_ = 0;
    int y1_ = 0;
    int x2_ = 0;
    int y2_ = 0;
};

} // namespace drawing

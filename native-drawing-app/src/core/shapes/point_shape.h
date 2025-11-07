#pragma once

#include "shape.h"

namespace drawing {

/**
 * @brief 点图形
 * 
 * 表示一个单独的点。
 */
class PointShape : public Shape {
public:
    PointShape() {
        id_ = generateId("point");
    }

    PointShape(int x, int y) : PointShape() {
        x_ = x;
        y_ = y;
    }

    PointShape(const Point& point) : PointShape(point.x, point.y) {}

    // 属性访问
    int getX() const { return x_; }
    void setX(int x) { x_ = x; }

    int getY() const { return y_; }
    void setY(int y) { y_ = y; }

    Point getPoint() const { return Point(x_, y_); }
    void setPoint(const Point& point) {
        x_ = point.x;
        y_ = point.y;
    }

    // Shape 接口实现
    std::string getType() const override {
        return "point";
    }

    void render(RenderingEngine& engine) override;

    BoundingBox getBounds() const override {
        // 点的包围盒是一个小矩形
        int size = static_cast<int>(strokeWidth_) + 2;
        return BoundingBox(x_ - size/2, y_ - size/2, size, size);
    }

    bool hitTest(const Point& point, int tolerance = 5) const override {
        Point p(x_, y_);
        return p.distanceTo(point) <= tolerance + strokeWidth_;
    }

    std::unique_ptr<Shape> clone() const override {
        auto cloned = std::make_unique<PointShape>(x_, y_);
        cloned->strokeColor_ = strokeColor_;
        cloned->strokeWidth_ = strokeWidth_;
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
            {"x", x_},
            {"y", y_}
        };
        return json;
    }

    static std::unique_ptr<PointShape> fromJson(const nlohmann::json& json) {
        auto shape = std::make_unique<PointShape>();
        shape->deserializeCommonProperties(json);
        
        if (json.contains("properties")) {
            const auto& props = json["properties"];
            shape->x_ = props.value("x", 0);
            shape->y_ = props.value("y", 0);
        }
        
        return shape;
    }

private:
    int x_ = 0;
    int y_ = 0;
};

} // namespace drawing

#pragma once

#include "shape.h"

namespace drawing {

/**
 * @brief 圆形图形
 * 
 * 表示一个圆形。
 */
class CircleShape : public Shape {
public:
    CircleShape() {
        id_ = generateId("circle");
    }

    CircleShape(int cx, int cy, int radius) : CircleShape() {
        cx_ = cx;
        cy_ = cy;
        radius_ = radius;
    }

    CircleShape(const Point& center, int radius)
        : CircleShape(center.x, center.y, radius) {}

    // 属性访问
    int getCenterX() const { return cx_; }
    void setCenterX(int cx) { cx_ = cx; }

    int getCenterY() const { return cy_; }
    void setCenterY(int cy) { cy_ = cy; }

    Point getCenter() const { return Point(cx_, cy_); }
    void setCenter(const Point& center) {
        cx_ = center.x;
        cy_ = center.y;
    }

    int getRadius() const { return radius_; }
    void setRadius(int radius) { radius_ = std::max(0, radius); }

    int getDiameter() const { return radius_ * 2; }

    // Shape 接口实现
    std::string getType() const override {
        return "circle";
    }

    void render(RenderingEngine& engine) override;

    BoundingBox getBounds() const override {
        int margin = static_cast<int>(strokeWidth_) + 2;
        int size = radius_ * 2 + margin * 2;
        return BoundingBox(
            cx_ - radius_ - margin,
            cy_ - radius_ - margin,
            size,
            size
        );
    }

    bool hitTest(const Point& point, int tolerance = 5) const override {
        Point center(cx_, cy_);
        float distance = center.distanceTo(point);
        
        if (filled_) {
            // 如果填充，点在圆内即可
            return distance <= radius_ + tolerance;
        } else {
            // 如果不填充，点必须在圆周附近
            float innerRadius = radius_ - strokeWidth_ - tolerance;
            float outerRadius = radius_ + strokeWidth_ + tolerance;
            return distance >= innerRadius && distance <= outerRadius;
        }
    }

    std::unique_ptr<Shape> clone() const override {
        auto cloned = std::make_unique<CircleShape>(cx_, cy_, radius_);
        cloned->strokeColor_ = strokeColor_;
        cloned->strokeWidth_ = strokeWidth_;
        cloned->strokeStyle_ = strokeStyle_;
        cloned->fillColor_ = fillColor_;
        cloned->filled_ = filled_;
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
            {"cx", cx_},
            {"cy", cy_},
            {"radius", radius_}
        };
        return json;
    }

    static std::unique_ptr<CircleShape> fromJson(const nlohmann::json& json) {
        auto shape = std::make_unique<CircleShape>();
        shape->deserializeCommonProperties(json);
        
        if (json.contains("properties")) {
            const auto& props = json["properties"];
            shape->cx_ = props.value("cx", 0);
            shape->cy_ = props.value("cy", 0);
            shape->radius_ = props.value("radius", 0);
        }
        
        return shape;
    }

private:
    int cx_ = 0;
    int cy_ = 0;
    int radius_ = 0;
};

} // namespace drawing

#pragma once

#include "shape.h"

namespace drawing {

/**
 * @brief 椭圆图形
 * 
 * 表示一个椭圆。
 */
class EllipseShape : public Shape {
public:
    EllipseShape() {
        id_ = generateId("ellipse");
    }

    EllipseShape(int cx, int cy, int rx, int ry) : EllipseShape() {
        cx_ = cx;
        cy_ = cy;
        rx_ = rx;
        ry_ = ry;
    }

    EllipseShape(const Point& center, int rx, int ry)
        : EllipseShape(center.x, center.y, rx, ry) {}

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

    int getRadiusX() const { return rx_; }
    void setRadiusX(int rx) { rx_ = std::max(0, rx); }

    int getRadiusY() const { return ry_; }
    void setRadiusY(int ry) { ry_ = std::max(0, ry); }

    // Shape 接口实现
    std::string getType() const override {
        return "ellipse";
    }

    void render(RenderingEngine& engine) override;

    BoundingBox getBounds() const override {
        int margin = static_cast<int>(strokeWidth_) + 2;
        return BoundingBox(
            cx_ - rx_ - margin,
            cy_ - ry_ - margin,
            (rx_ + margin) * 2,
            (ry_ + margin) * 2
        );
    }

    bool hitTest(const Point& point, int tolerance = 5) const override {
        // 椭圆方程: (x-cx)²/rx² + (y-cy)²/ry² = 1
        float dx = point.x - cx_;
        float dy = point.y - cy_;
        float value = (dx * dx) / (rx_ * rx_) + (dy * dy) / (ry_ * ry_);
        
        if (filled_) {
            // 如果填充，点在椭圆内即可
            return value <= 1.0f + tolerance / std::max(rx_, ry_);
        } else {
            // 如果不填充，点必须在椭圆边界附近
            float innerValue = (dx * dx) / ((rx_ - strokeWidth_) * (rx_ - strokeWidth_)) +
                             (dy * dy) / ((ry_ - strokeWidth_) * (ry_ - strokeWidth_));
            float outerValue = (dx * dx) / ((rx_ + strokeWidth_) * (rx_ + strokeWidth_)) +
                             (dy * dy) / ((ry_ + strokeWidth_) * (ry_ + strokeWidth_));
            return value >= innerValue && value <= outerValue;
        }
    }

    std::unique_ptr<Shape> clone() const override {
        auto cloned = std::make_unique<EllipseShape>(cx_, cy_, rx_, ry_);
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
            {"rx", rx_},
            {"ry", ry_}
        };
        return json;
    }

    static std::unique_ptr<EllipseShape> fromJson(const nlohmann::json& json) {
        auto shape = std::make_unique<EllipseShape>();
        shape->deserializeCommonProperties(json);
        
        if (json.contains("properties")) {
            const auto& props = json["properties"];
            shape->cx_ = props.value("cx", 0);
            shape->cy_ = props.value("cy", 0);
            shape->rx_ = props.value("rx", 0);
            shape->ry_ = props.value("ry", 0);
        }
        
        return shape;
    }

private:
    int cx_ = 0;
    int cy_ = 0;
    int rx_ = 0;
    int ry_ = 0;
};

} // namespace drawing

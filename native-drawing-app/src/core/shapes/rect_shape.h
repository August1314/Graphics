#pragma once

#include "shape.h"

namespace drawing {

/**
 * @brief 矩形图形
 * 
 * 表示一个矩形，可以有圆角。
 */
class RectShape : public Shape {
public:
    RectShape() {
        id_ = generateId("rect");
    }

    RectShape(int x, int y, int width, int height) : RectShape() {
        x_ = x;
        y_ = y;
        width_ = width;
        height_ = height;
    }

    RectShape(const BoundingBox& bounds)
        : RectShape(bounds.x, bounds.y, bounds.width, bounds.height) {}

    // 属性访问
    int getX() const { return x_; }
    void setX(int x) { x_ = x; }

    int getY() const { return y_; }
    void setY(int y) { y_ = y; }

    int getWidth() const { return width_; }
    void setWidth(int width) { width_ = std::max(0, width); }

    int getHeight() const { return height_; }
    void setHeight(int height) { height_ = std::max(0, height); }

    float getCornerRadius() const { return cornerRadius_; }
    void setCornerRadius(float radius) { cornerRadius_ = std::max(0.0f, radius); }

    Point getTopLeft() const { return Point(x_, y_); }
    Point getTopRight() const { return Point(x_ + width_, y_); }
    Point getBottomLeft() const { return Point(x_, y_ + height_); }
    Point getBottomRight() const { return Point(x_ + width_, y_ + height_); }
    Point getCenter() const { return Point(x_ + width_/2, y_ + height_/2); }

    // Shape 接口实现
    std::string getType() const override {
        return "rect";
    }

    void render(RenderingEngine& engine) override;

    BoundingBox getBounds() const override {
        int margin = static_cast<int>(strokeWidth_) + 2;
        return BoundingBox(x_, y_, width_, height_).expanded(margin);
    }

    bool hitTest(const Point& point, int tolerance = 5) const override {
        BoundingBox bounds(x_, y_, width_, height_);
        BoundingBox expandedBounds = bounds.expanded(tolerance + static_cast<int>(strokeWidth_));
        
        if (!expandedBounds.contains(point)) {
            return false;
        }

        if (filled_) {
            // 如果填充，点在矩形内即可
            return bounds.contains(point);
        } else {
            // 如果不填充，点必须在边框附近
            BoundingBox innerBounds = bounds.shrunk(static_cast<int>(strokeWidth_) + tolerance);
            return !innerBounds.contains(point);
        }
    }

    std::unique_ptr<Shape> clone() const override {
        auto cloned = std::make_unique<RectShape>(x_, y_, width_, height_);
        cloned->cornerRadius_ = cornerRadius_;
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
            {"x", x_},
            {"y", y_},
            {"width", width_},
            {"height", height_},
            {"cornerRadius", cornerRadius_}
        };
        return json;
    }

    static std::unique_ptr<RectShape> fromJson(const nlohmann::json& json) {
        auto shape = std::make_unique<RectShape>();
        shape->deserializeCommonProperties(json);
        
        if (json.contains("properties")) {
            const auto& props = json["properties"];
            shape->x_ = props.value("x", 0);
            shape->y_ = props.value("y", 0);
            shape->width_ = props.value("width", 0);
            shape->height_ = props.value("height", 0);
            shape->cornerRadius_ = props.value("cornerRadius", 0.0f);
        }
        
        return shape;
    }

private:
    int x_ = 0;
    int y_ = 0;
    int width_ = 0;
    int height_ = 0;
    float cornerRadius_ = 0.0f;
};

} // namespace drawing

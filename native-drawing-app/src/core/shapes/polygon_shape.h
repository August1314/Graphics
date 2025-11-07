#pragma once

#include "shape.h"
#include <vector>

namespace drawing {

/**
 * @brief 多边形图形
 * 
 * 表示一个由多个顶点组成的多边形（闭合）。
 */
class PolygonShape : public Shape {
public:
    PolygonShape() {
        id_ = generateId("polygon");
    }

    PolygonShape(const std::vector<Point>& points) : PolygonShape() {
        points_ = points;
    }

    // 属性访问
    const std::vector<Point>& getPoints() const { return points_; }
    void setPoints(const std::vector<Point>& points) { points_ = points; }

    void addPoint(const Point& point) {
        points_.push_back(point);
    }

    void insertPoint(size_t index, const Point& point) {
        if (index <= points_.size()) {
            points_.insert(points_.begin() + index, point);
        }
    }

    void removePoint(size_t index) {
        if (index < points_.size()) {
            points_.erase(points_.begin() + index);
        }
    }

    void updatePoint(size_t index, const Point& point) {
        if (index < points_.size()) {
            points_[index] = point;
        }
    }

    size_t getPointCount() const { return points_.size(); }

    bool isClosed() const { return closed_; }
    void setClosed(bool closed) { closed_ = closed; }

    // Shape 接口实现
    std::string getType() const override {
        return "polygon";
    }

    void render(RenderingEngine& engine) override;

    BoundingBox getBounds() const override {
        if (points_.empty()) {
            return BoundingBox();
        }
        
        int margin = static_cast<int>(strokeWidth_) + 2;
        return BoundingBox::fromPointList(points_).expanded(margin);
    }

    bool hitTest(const Point& point, int tolerance = 5) const override {
        if (points_.size() < 2) {
            return false;
        }

        if (filled_ && closed_) {
            // 使用射线法判断点是否在多边形内
            return isPointInPolygon(point);
        } else {
            // 检查点是否在任何边附近
            for (size_t i = 0; i < points_.size() - 1; i++) {
                if (isPointNearSegment(point, points_[i], points_[i + 1], tolerance)) {
                    return true;
                }
            }
            
            // 如果是闭合多边形，检查最后一条边
            if (closed_ && points_.size() > 2) {
                return isPointNearSegment(point, points_.back(), points_.front(), tolerance);
            }
            
            return false;
        }
    }

    std::unique_ptr<Shape> clone() const override {
        auto cloned = std::make_unique<PolygonShape>(points_);
        cloned->closed_ = closed_;
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
        
        nlohmann::json pointsJson = nlohmann::json::array();
        for (const auto& point : points_) {
            pointsJson.push_back(point.toJson());
        }
        
        json["properties"] = {
            {"points", pointsJson},
            {"closed", closed_}
        };
        return json;
    }

    static std::unique_ptr<PolygonShape> fromJson(const nlohmann::json& json) {
        auto shape = std::make_unique<PolygonShape>();
        shape->deserializeCommonProperties(json);
        
        if (json.contains("properties")) {
            const auto& props = json["properties"];
            
            if (props.contains("points")) {
                for (const auto& pointJson : props["points"]) {
                    shape->points_.push_back(Point::fromJson(pointJson));
                }
            }
            
            shape->closed_ = props.value("closed", true);
        }
        
        return shape;
    }

private:
    std::vector<Point> points_;
    bool closed_ = true;

    /**
     * @brief 使用射线法判断点是否在多边形内
     */
    bool isPointInPolygon(const Point& point) const {
        if (points_.size() < 3) {
            return false;
        }

        int crossings = 0;
        for (size_t i = 0; i < points_.size(); i++) {
            const Point& p1 = points_[i];
            const Point& p2 = points_[(i + 1) % points_.size()];

            if ((p1.y <= point.y && p2.y > point.y) ||
                (p1.y > point.y && p2.y <= point.y)) {
                
                float t = static_cast<float>(point.y - p1.y) / (p2.y - p1.y);
                float x = p1.x + t * (p2.x - p1.x);
                
                if (point.x < x) {
                    crossings++;
                }
            }
        }

        return (crossings % 2) == 1;
    }

    /**
     * @brief 判断点是否在线段附近
     */
    bool isPointNearSegment(const Point& point, const Point& p1, const Point& p2, int tolerance) const {
        Point v = p2 - p1;
        Point w = point - p1;

        float c1 = w.dot(v);
        if (c1 <= 0) {
            return point.distanceTo(p1) <= tolerance + strokeWidth_;
        }

        float c2 = v.dot(v);
        if (c1 >= c2) {
            return point.distanceTo(p2) <= tolerance + strokeWidth_;
        }

        float t = c1 / c2;
        Point closest = p1 + v * t;
        return point.distanceTo(closest) <= tolerance + strokeWidth_;
    }
};

} // namespace drawing

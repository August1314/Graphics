#pragma once

#include "../types/types.h"
#include <string>
#include <memory>
#include <nlohmann/json.hpp>

namespace drawing {

// 前向声明
class RenderingEngine;

/**
 * @brief 图形基类
 * 
 * 所有图形类型的抽象基类，定义了图形的通用接口。
 */
class Shape {
public:
    virtual ~Shape() = default;

    // 纯虚函数 - 必须由派生类实现
    
    /**
     * @brief 获取图形类型名称
     */
    virtual std::string getType() const = 0;

    /**
     * @brief 渲染图形
     * @param engine 渲染引擎
     */
    virtual void render(RenderingEngine& engine) = 0;

    /**
     * @brief 获取包围盒
     */
    virtual BoundingBox getBounds() const = 0;

    /**
     * @brief 点击测试
     * @param point 测试点
     * @param tolerance 容差（像素）
     * @return 如果点在图形上或附近返回 true
     */
    virtual bool hitTest(const Point& point, int tolerance = 5) const = 0;

    /**
     * @brief 克隆图形
     */
    virtual std::unique_ptr<Shape> clone() const = 0;

    /**
     * @brief 序列化为 JSON
     */
    virtual nlohmann::json toJson() const = 0;

    // 通用属性访问器

    const std::string& getId() const { return id_; }
    void setId(const std::string& id) { id_ = id; }

    const Color& getStrokeColor() const { return strokeColor_; }
    void setStrokeColor(const Color& color) { strokeColor_ = color; }

    float getStrokeWidth() const { return strokeWidth_; }
    void setStrokeWidth(float width) { strokeWidth_ = width; }

    StrokeStyle getStrokeStyle() const { return strokeStyle_; }
    void setStrokeStyle(StrokeStyle style) { strokeStyle_ = style; }

    const Color& getFillColor() const { return fillColor_; }
    void setFillColor(const Color& color) { fillColor_ = color; }

    bool isFilled() const { return filled_; }
    void setFilled(bool filled) { filled_ = filled; }

    float getOpacity() const { return opacity_; }
    void setOpacity(float opacity) { opacity_ = std::clamp(opacity, 0.0f, 1.0f); }

    const Matrix& getTransform() const { return transform_; }
    void setTransform(const Matrix& transform) { transform_ = transform; }

    int getZIndex() const { return zIndex_; }
    void setZIndex(int zIndex) { zIndex_ = zIndex; }

    bool isVisible() const { return visible_; }
    void setVisible(bool visible) { visible_ = visible; }

    bool isLocked() const { return locked_; }
    void setLocked(bool locked) { locked_ = locked; }

    bool isSelected() const { return selected_; }
    void setSelected(bool selected) { selected_ = selected; }

    // 变换操作

    /**
     * @brief 平移图形
     */
    virtual void translate(float dx, float dy) {
        transform_.translate(dx, dy);
    }

    /**
     * @brief 缩放图形
     */
    virtual void scale(float sx, float sy) {
        transform_.scale(sx, sy);
    }

    /**
     * @brief 旋转图形
     * @param angle 旋转角度（弧度）
     */
    virtual void rotate(float angle) {
        transform_.rotate(angle);
    }

    /**
     * @brief 旋转图形（绕指定点）
     */
    virtual void rotate(float angle, const PointF& center) {
        BoundingBox bounds = getBounds();
        PointF currentCenter(bounds.center());
        
        transform_.translate(-currentCenter.x, -currentCenter.y);
        transform_.translate(center.x, center.y);
        transform_.rotate(angle);
        transform_.translate(-center.x, -center.y);
        transform_.translate(currentCenter.x, currentCenter.y);
    }

protected:
    // 通用属性
    std::string id_;
    Color strokeColor_ = Color::Black;
    float strokeWidth_ = 2.0f;
    StrokeStyle strokeStyle_ = StrokeStyle::Solid;
    Color fillColor_ = Color::White;
    bool filled_ = false;
    float opacity_ = 1.0f;
    Matrix transform_;
    int zIndex_ = 0;
    bool visible_ = true;
    bool locked_ = false;
    bool selected_ = false;

    /**
     * @brief 序列化通用属性
     */
    nlohmann::json serializeCommonProperties() const {
        nlohmann::json json;
        json["id"] = id_;
        json["type"] = getType();
        json["strokeColor"] = strokeColor_.toJson();
        json["strokeWidth"] = strokeWidth_;
        json["strokeStyle"] = static_cast<int>(strokeStyle_);
        json["fillColor"] = fillColor_.toJson();
        json["filled"] = filled_;
        json["opacity"] = opacity_;
        json["transform"] = transform_.toJson();
        json["zIndex"] = zIndex_;
        json["visible"] = visible_;
        json["locked"] = locked_;
        return json;
    }

    /**
     * @brief 反序列化通用属性
     */
    void deserializeCommonProperties(const nlohmann::json& json) {
        if (json.contains("id")) id_ = json["id"];
        if (json.contains("strokeColor")) strokeColor_ = Color::fromJson(json["strokeColor"]);
        if (json.contains("strokeWidth")) strokeWidth_ = json["strokeWidth"];
        if (json.contains("strokeStyle")) strokeStyle_ = static_cast<StrokeStyle>(json["strokeStyle"].get<int>());
        if (json.contains("fillColor")) fillColor_ = Color::fromJson(json["fillColor"]);
        if (json.contains("filled")) filled_ = json["filled"];
        if (json.contains("opacity")) opacity_ = json["opacity"];
        if (json.contains("transform")) transform_ = Matrix::fromJson(json["transform"]);
        if (json.contains("zIndex")) zIndex_ = json["zIndex"];
        if (json.contains("visible")) visible_ = json["visible"];
        if (json.contains("locked")) locked_ = json["locked"];
    }

    /**
     * @brief 生成唯一 ID
     */
    static std::string generateId(const std::string& prefix) {
        static int counter = 0;
        return prefix + "_" + std::to_string(++counter);
    }
};

} // namespace drawing

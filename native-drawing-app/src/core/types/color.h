#pragma once

#include <cstdint>
#include <string>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <nlohmann/json.hpp>

namespace drawing {

/**
 * @brief RGBA 颜色结构
 * 
 * 表示一个 RGBA 颜色，每个通道使用 8 位（0-255）。
 */
struct Color {
    uint8_t r;  // Red (0-255)
    uint8_t g;  // Green (0-255)
    uint8_t b;  // Blue (0-255)
    uint8_t a;  // Alpha (0-255, 255 = 完全不透明)

    // 构造函数
    Color() : r(0), g(0), b(0), a(255) {}
    Color(uint8_t r, uint8_t g, uint8_t b, uint8_t a = 255)
        : r(r), g(g), b(b), a(a) {}

    // 运算符重载
    bool operator==(const Color& other) const {
        return r == other.r && g == other.g && b == other.b && a == other.a;
    }

    bool operator!=(const Color& other) const {
        return !(*this == other);
    }

    // 颜色转换方法

    /**
     * @brief 从十六进制字符串创建颜色
     * @param hex 十六进制字符串，格式：#RRGGBB 或 #RRGGBBAA
     * @return Color 对象
     */
    static Color fromHex(const std::string& hex) {
        std::string hexStr = hex;
        
        // 移除 # 前缀
        if (!hexStr.empty() && hexStr[0] == '#') {
            hexStr = hexStr.substr(1);
        }

        // 验证长度
        if (hexStr.length() != 6 && hexStr.length() != 8) {
            return Color(); // 返回黑色作为默认值
        }

        // 解析十六进制
        uint32_t value = 0;
        std::stringstream ss;
        ss << std::hex << hexStr;
        ss >> value;

        if (hexStr.length() == 6) {
            // #RRGGBB 格式
            return Color(
                (value >> 16) & 0xFF,
                (value >> 8) & 0xFF,
                value & 0xFF,
                255
            );
        } else {
            // #RRGGBBAA 格式
            return Color(
                (value >> 24) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 8) & 0xFF,
                value & 0xFF
            );
        }
    }

    /**
     * @brief 转换为十六进制字符串
     * @param includeAlpha 是否包含 alpha 通道
     * @return 十六进制字符串
     */
    std::string toHex(bool includeAlpha = false) const {
        std::stringstream ss;
        ss << "#" << std::hex << std::setfill('0');
        ss << std::setw(2) << static_cast<int>(r);
        ss << std::setw(2) << static_cast<int>(g);
        ss << std::setw(2) << static_cast<int>(b);
        if (includeAlpha) {
            ss << std::setw(2) << static_cast<int>(a);
        }
        
        std::string result = ss.str();
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return result;
    }

    /**
     * @brief 从 RGB 值创建颜色（0-255）
     */
    static Color fromRGB(uint8_t r, uint8_t g, uint8_t b) {
        return Color(r, g, b, 255);
    }

    /**
     * @brief 从 RGBA 值创建颜色（0-255）
     */
    static Color fromRGBA(uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
        return Color(r, g, b, a);
    }

    /**
     * @brief 从 HSV 创建颜色
     * @param h 色相 (0-360)
     * @param s 饱和度 (0-1)
     * @param v 明度 (0-1)
     * @param a 透明度 (0-255)
     */
    static Color fromHSV(float h, float s, float v, uint8_t a = 255) {
        float c = v * s;
        float x = c * (1.0f - std::abs(std::fmod(h / 60.0f, 2.0f) - 1.0f));
        float m = v - c;

        float r1, g1, b1;
        if (h < 60) {
            r1 = c; g1 = x; b1 = 0;
        } else if (h < 120) {
            r1 = x; g1 = c; b1 = 0;
        } else if (h < 180) {
            r1 = 0; g1 = c; b1 = x;
        } else if (h < 240) {
            r1 = 0; g1 = x; b1 = c;
        } else if (h < 300) {
            r1 = x; g1 = 0; b1 = c;
        } else {
            r1 = c; g1 = 0; b1 = x;
        }

        return Color(
            static_cast<uint8_t>((r1 + m) * 255),
            static_cast<uint8_t>((g1 + m) * 255),
            static_cast<uint8_t>((b1 + m) * 255),
            a
        );
    }

    /**
     * @brief 获取亮度（0-1）
     */
    float getLuminance() const {
        return (0.299f * r + 0.587f * g + 0.114f * b) / 255.0f;
    }

    /**
     * @brief 混合两个颜色
     * @param other 另一个颜色
     * @param t 混合比例 (0-1)，0 = 完全是当前颜色，1 = 完全是另一个颜色
     */
    Color blend(const Color& other, float t) const {
        t = std::clamp(t, 0.0f, 1.0f);
        return Color(
            static_cast<uint8_t>(r + (other.r - r) * t),
            static_cast<uint8_t>(g + (other.g - g) * t),
            static_cast<uint8_t>(b + (other.b - b) * t),
            static_cast<uint8_t>(a + (other.a - a) * t)
        );
    }

    /**
     * @brief 使用 alpha 混合
     */
    Color alphaBlend(const Color& background) const {
        float alpha = a / 255.0f;
        float invAlpha = 1.0f - alpha;
        
        return Color(
            static_cast<uint8_t>(r * alpha + background.r * invAlpha),
            static_cast<uint8_t>(g * alpha + background.g * invAlpha),
            static_cast<uint8_t>(b * alpha + background.b * invAlpha),
            255
        );
    }

    // JSON 序列化
    nlohmann::json toJson() const {
        return {
            {"r", r},
            {"g", g},
            {"b", b},
            {"a", a},
            {"hex", toHex(true)}
        };
    }

    static Color fromJson(const nlohmann::json& json) {
        if (json.contains("hex")) {
            return fromHex(json["hex"]);
        }
        return Color(
            json.value("r", 0),
            json.value("g", 0),
            json.value("b", 0),
            json.value("a", 255)
        );
    }

    // 预定义颜色
    static const Color Black;
    static const Color White;
    static const Color Red;
    static const Color Green;
    static const Color Blue;
    static const Color Yellow;
    static const Color Cyan;
    static const Color Magenta;
    static const Color Transparent;
};

// 预定义颜色常量
inline const Color Color::Black = Color(0, 0, 0, 255);
inline const Color Color::White = Color(255, 255, 255, 255);
inline const Color Color::Red = Color(255, 0, 0, 255);
inline const Color Color::Green = Color(0, 255, 0, 255);
inline const Color Color::Blue = Color(0, 0, 255, 255);
inline const Color Color::Yellow = Color(255, 255, 0, 255);
inline const Color Color::Cyan = Color(0, 255, 255, 255);
inline const Color Color::Magenta = Color(255, 0, 255, 255);
inline const Color Color::Transparent = Color(0, 0, 0, 0);

} // namespace drawing

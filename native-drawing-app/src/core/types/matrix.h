#pragma once

#include "point.h"
#include <cmath>
#include <nlohmann/json.hpp>

namespace drawing {

/**
 * @brief 2D 仿射变换矩阵
 * 
 * 使用 3x3 矩阵表示 2D 仿射变换，但只存储前两行（6个值）：
 * | m[0]  m[1]  m[2] |   | a  b  tx |
 * | m[3]  m[4]  m[5] | = | c  d  ty |
 * |  0     0     1   |   | 0  0   1 |
 * 
 * 变换公式：
 * x' = a*x + b*y + tx
 * y' = c*x + d*y + ty
 */
struct Matrix {
    float m[6];  // [a, b, tx, c, d, ty]

    // 构造函数
    Matrix() {
        identity();
    }

    Matrix(float a, float b, float c, float d, float tx, float ty) {
        m[0] = a;  m[1] = b;  m[2] = tx;
        m[3] = c;  m[4] = d;  m[5] = ty;
    }

    // 访问器
    float a() const { return m[0]; }
    float b() const { return m[1]; }
    float c() const { return m[3]; }
    float d() const { return m[4]; }
    float tx() const { return m[2]; }
    float ty() const { return m[5]; }

    void setA(float value) { m[0] = value; }
    void setB(float value) { m[1] = value; }
    void setC(float value) { m[3] = value; }
    void setD(float value) { m[4] = value; }
    void setTx(float value) { m[2] = value; }
    void setTy(float value) { m[5] = value; }

    /**
     * @brief 设置为单位矩阵
     */
    void identity() {
        m[0] = 1.0f; m[1] = 0.0f; m[2] = 0.0f;
        m[3] = 0.0f; m[4] = 1.0f; m[5] = 0.0f;
    }

    /**
     * @brief 检查是否为单位矩阵
     */
    bool isIdentity() const {
        return m[0] == 1.0f && m[1] == 0.0f && m[2] == 0.0f &&
               m[3] == 0.0f && m[4] == 1.0f && m[5] == 0.0f;
    }

    /**
     * @brief 创建平移矩阵
     */
    static Matrix makeTranslation(float tx, float ty) {
        return Matrix(1.0f, 0.0f, 0.0f, 1.0f, tx, ty);
    }

    /**
     * @brief 创建缩放矩阵
     */
    static Matrix makeScale(float sx, float sy) {
        return Matrix(sx, 0.0f, 0.0f, sy, 0.0f, 0.0f);
    }

    /**
     * @brief 创建均匀缩放矩阵
     */
    static Matrix makeScale(float scale) {
        return makeScale(scale, scale);
    }

    /**
     * @brief 创建旋转矩阵
     * @param angle 旋转角度（弧度）
     */
    static Matrix makeRotation(float angle) {
        float cosA = std::cos(angle);
        float sinA = std::sin(angle);
        return Matrix(cosA, -sinA, sinA, cosA, 0.0f, 0.0f);
    }

    /**
     * @brief 创建绕指定点旋转的矩阵
     */
    static Matrix makeRotation(float angle, const PointF& center) {
        Matrix result;
        result.translate(-center.x, -center.y);
        result.rotate(angle);
        result.translate(center.x, center.y);
        return result;
    }

    /**
     * @brief 平移变换
     */
    Matrix& translate(float tx, float ty) {
        m[2] += m[0] * tx + m[1] * ty;
        m[5] += m[3] * tx + m[4] * ty;
        return *this;
    }

    /**
     * @brief 缩放变换
     */
    Matrix& scale(float sx, float sy) {
        m[0] *= sx;
        m[1] *= sy;
        m[3] *= sx;
        m[4] *= sy;
        return *this;
    }

    /**
     * @brief 均匀缩放变换
     */
    Matrix& scale(float scale) {
        return this->scale(scale, scale);
    }

    /**
     * @brief 旋转变换
     * @param angle 旋转角度（弧度）
     */
    Matrix& rotate(float angle) {
        float cosA = std::cos(angle);
        float sinA = std::sin(angle);

        float a = m[0];
        float b = m[1];
        float c = m[3];
        float d = m[4];

        m[0] = a * cosA - b * sinA;
        m[1] = a * sinA + b * cosA;
        m[3] = c * cosA - d * sinA;
        m[4] = c * sinA + d * cosA;

        return *this;
    }

    /**
     * @brief 矩阵乘法
     */
    Matrix operator*(const Matrix& other) const {
        return Matrix(
            m[0] * other.m[0] + m[1] * other.m[3],
            m[0] * other.m[1] + m[1] * other.m[4],
            m[3] * other.m[0] + m[4] * other.m[3],
            m[3] * other.m[1] + m[4] * other.m[4],
            m[0] * other.m[2] + m[1] * other.m[5] + m[2],
            m[3] * other.m[2] + m[4] * other.m[5] + m[5]
        );
    }

    /**
     * @brief 矩阵乘法赋值
     */
    Matrix& operator*=(const Matrix& other) {
        *this = *this * other;
        return *this;
    }

    /**
     * @brief 变换点
     */
    PointF transform(const PointF& point) const {
        return PointF(
            m[0] * point.x + m[1] * point.y + m[2],
            m[3] * point.x + m[4] * point.y + m[5]
        );
    }

    /**
     * @brief 变换点（整数版本）
     */
    Point transform(const Point& point) const {
        return transform(PointF(point)).toPoint();
    }

    /**
     * @brief 变换向量（不应用平移）
     */
    PointF transformVector(const PointF& vector) const {
        return PointF(
            m[0] * vector.x + m[1] * vector.y,
            m[3] * vector.x + m[4] * vector.y
        );
    }

    /**
     * @brief 计算行列式
     */
    float determinant() const {
        return m[0] * m[4] - m[1] * m[3];
    }

    /**
     * @brief 检查矩阵是否可逆
     */
    bool isInvertible() const {
        return std::abs(determinant()) > 1e-6f;
    }

    /**
     * @brief 计算逆矩阵
     */
    Matrix inverted() const {
        float det = determinant();
        if (std::abs(det) < 1e-6f) {
            // 矩阵不可逆，返回单位矩阵
            return Matrix();
        }

        float invDet = 1.0f / det;
        return Matrix(
            m[4] * invDet,
            -m[1] * invDet,
            -m[3] * invDet,
            m[0] * invDet,
            (m[1] * m[5] - m[4] * m[2]) * invDet,
            (m[3] * m[2] - m[0] * m[5]) * invDet
        );
    }

    /**
     * @brief 提取缩放因子
     */
    PointF getScale() const {
        float sx = std::sqrt(m[0] * m[0] + m[3] * m[3]);
        float sy = std::sqrt(m[1] * m[1] + m[4] * m[4]);
        return PointF(sx, sy);
    }

    /**
     * @brief 提取旋转角度（弧度）
     */
    float getRotation() const {
        return std::atan2(m[3], m[0]);
    }

    /**
     * @brief 提取平移
     */
    PointF getTranslation() const {
        return PointF(m[2], m[5]);
    }

    // 运算符重载
    bool operator==(const Matrix& other) const {
        for (int i = 0; i < 6; i++) {
            if (std::abs(m[i] - other.m[i]) > 1e-6f) {
                return false;
            }
        }
        return true;
    }

    bool operator!=(const Matrix& other) const {
        return !(*this == other);
    }

    // JSON 序列化
    nlohmann::json toJson() const {
        return {
            {"a", m[0]},
            {"b", m[1]},
            {"c", m[3]},
            {"d", m[4]},
            {"tx", m[2]},
            {"ty", m[5]}
        };
    }

    static Matrix fromJson(const nlohmann::json& json) {
        return Matrix(
            json.value("a", 1.0f),
            json.value("b", 0.0f),
            json.value("c", 0.0f),
            json.value("d", 1.0f),
            json.value("tx", 0.0f),
            json.value("ty", 0.0f)
        );
    }
};

} // namespace drawing

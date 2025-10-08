# 贡献指南

感谢你对本项目的关注！我们欢迎任何形式的贡献。

---

## 🤝 如何贡献

### 报告 Bug

如果你发现了 bug，请创建一个 Issue，包含以下信息：

- **Bug 描述**: 清晰简洁的描述
- **复现步骤**: 详细的复现步骤
- **预期行为**: 你期望发生什么
- **实际行为**: 实际发生了什么
- **环境信息**: 操作系统、Python 版本、PySide6 版本
- **截图**: 如果适用，添加截图

### 提出功能建议

如果你有功能建议，请创建一个 Issue，包含：

- **功能描述**: 清晰的功能说明
- **使用场景**: 为什么需要这个功能
- **实现建议**: 如果有，提供实现思路

### 提交代码

1. **Fork 项目**
2. **创建分支**: `git checkout -b feature/my-feature`
3. **编写代码**: 遵循代码规范
4. **编写测试**: 确保测试覆盖
5. **运行测试**: `pytest`
6. **提交代码**: `git commit -m "Add: 我的功能"`
7. **推送分支**: `git push origin feature/my-feature`
8. **创建 Pull Request**

---

## 📝 代码规范

### Python 风格

- 遵循 **PEP 8**
- 使用 **类型注解**
- 编写 **文档字符串**（Google 风格）
- 使用 **有意义的变量名**

### 提交信息

格式：`类型: 简短描述`

类型：
- `Add`: 新增功能
- `Fix`: 修复 bug
- `Update`: 更新功能
- `Refactor`: 重构代码
- `Docs`: 文档更新
- `Test`: 测试相关
- `Style`: 代码格式
- `Perf`: 性能优化

示例：
```
Add: 添加圆形工具

实现了圆形绘制工具，支持拖动绘制和样式编辑。

相关 Issue: #42
```

---

## 🧪 测试要求

- 所有新功能必须有单元测试
- 测试覆盖率不低于 60%
- 所有测试必须通过
- 性能测试必须达标

运行测试：
```bash
pytest
pytest --cov=app --cov-report=html
```

---

## 📚 文档要求

- 所有公共 API 必须有文档字符串
- 复杂逻辑必须有注释
- 新功能必须更新 README
- 重大变更必须更新 CHANGELOG

---

## ✅ Pull Request 检查清单

提交 PR 前，请确保：

- [ ] 代码符合 PEP 8 规范
- [ ] 有完整的文档字符串
- [ ] 有类型注解
- [ ] 有单元测试
- [ ] 所有测试通过
- [ ] 无 lint 警告
- [ ] 更新了相关文档
- [ ] 提交信息符合规范

---

## 🎯 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/drawing-app.git
cd drawing-app
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. 运行应用
```bash
python -m app.main
```

### 5. 运行测试
```bash
pytest
```

---

## 📞 联系方式

如有问题，请通过以下方式联系：

- **Issue**: 在 GitHub 上创建 Issue
- **Email**: [your-email@example.com]
- **讨论**: GitHub Discussions

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

感谢你的贡献！🎉


# Graphics - 二维图形绘图系统

一个基于 PySide6 的专业级二维图形绘图应用，支持多种绘图工具、撤销/重做、JSON 序列化等功能。

## 🎯 项目状态

**当前版本**: 2.0 (优化中)  
**优化进度**: 46% (Phase 3 进行中)  
**代码质量**: ⭐⭐⭐⭐ (4/5)  
**测试覆盖**: 30%

## ✨ 最近更新 (2025-10-08)

- ✅ 完成 Phase 1: 基础设施搭建（日志系统、异常处理、测试框架）
- ✅ 完成 Phase 2: 核心模块实现（Document、SelectionManager、StyleManager）
- 🔄 进行 Phase 3: 架构重构（PropertyController、ToolManager、ViewStateMachine）

详见 [FINAL_SUMMARY.md](FINAL_SUMMARY.md)

## 🚀 快速开始

### 安装依赖

```bash
# 激活 conda 环境
conda activate pnt

# 安装依赖
pip install -r app/requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 运行应用

```bash
python -m app.main
```

### 运行测试

```bash
# 基础功能测试
python test_basic.py

# Phase 3 测试
python test_phase3_simple.py

# 完整单元测试
pytest tests/unit/ -v
```

## 📚 文档

- **快速开始**: [QUICK_START.md](QUICK_START.md)
- **测试报告**: [TEST_REPORT.md](TEST_REPORT.md)
- **进度总结**: [PROGRESS_SUMMARY.md](PROGRESS_SUMMARY.md)
- **最终总结**: [FINAL_SUMMARY.md](FINAL_SUMMARY.md)
- **应用说明**: [app/README.md](app/README.md)

### 规范文档

- **需求文档**: [.kiro/specs/app-optimization/requirements.md](.kiro/specs/app-optimization/requirements.md)
- **设计文档**: [.kiro/specs/app-optimization/design.md](.kiro/specs/app-optimization/design.md)
- **任务列表**: [.kiro/specs/app-optimization/tasks.md](.kiro/specs/app-optimization/tasks.md)

## 🎨 功能特性

### 绘图工具
- ✅ 基础图形：点、线、矩形、圆、多边形
- ✅ 画笔工具：普通画笔、马克笔、书法笔、喷枪
- ✅ 橡皮擦：对象擦除和路径擦除

### 编辑功能
- ✅ 选择和移动（支持多选）
- ✅ 撤销/重做（基于命令模式）
- ✅ 复制/粘贴
- ✅ 属性编辑（颜色、线宽、透明度等）

### 文件操作
- ✅ JSON 格式保存/加载
- ✅ PNG 图片导出
- ✅ 版本迁移支持

### 系统功能
- ✅ 完整的日志系统
- ✅ 异常处理框架
- ✅ 测试框架（pytest）

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────────┐
│           UI Layer (ui/)                │
│  MainWindow, CanvasView, PropertyPanel  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Application Layer                  │
│  Controllers, Managers, State Machines  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Domain Layer (core/)             │
│  Document, Shapes, Tools, Commands      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Infrastructure Layer (utils/)       │
│    Logging, Serialization, Validation   │
└─────────────────────────────────────────┘
```

### 核心模块

- **Document**: 文档生命周期管理
- **SelectionManager**: 统一选择管理
- **StyleManager**: 样式管理和缓存
- **PropertyController**: 统一属性更新
- **ToolManager**: 工具管理
- **ViewStateMachine**: 状态机管理

## 📊 质量指标

| 维度 | 优化前 | 当前 | 目标 |
|------|--------|------|------|
| 代码质量 | ⭐⭐ (2/5) | ⭐⭐⭐⭐ (4/5) | ⭐⭐⭐⭐⭐ (5/5) |
| 架构设计 | ⭐⭐⭐ (3/5) | ⭐⭐⭐⭐ (4/5) | ⭐⭐⭐⭐⭐ (5/5) |
| 测试覆盖 | 0% | 30% | 60%+ |

## 🛠️ 技术栈

- **语言**: Python 3.10+
- **GUI 框架**: PySide6 (Qt for Python)
- **主题**: qt-material
- **测试**: pytest, pytest-qt, pytest-cov
- **代码质量**: pylint, black, mypy

## 📈 优化进度

```
Phase 1: 基础设施搭建    ████████████████████ 100% ✅
Phase 2: 核心模块实现    ████████████████████ 100% ✅
Phase 3: 架构重构        ███████████████░░░░░  75% 🔄
Phase 4: 性能优化        ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 5: 用户体验改进    ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 6: 验收和发布      ░░░░░░░░░░░░░░░░░░░░   0% ⏳

总进度: ████████░░░░░░░░░░░░ 46%
```

## 🤝 贡献

欢迎贡献！请查看 [任务列表](.kiro/specs/app-optimization/tasks.md) 了解待完成的工作。

## 📄 许可证

[待添加]

## 📞 联系

如有问题或建议，请查看文档或提交 Issue。

---

**最后更新**: 2025-10-08  
**维护者**: Kiro AI Assistant

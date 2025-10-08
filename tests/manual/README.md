# 手动测试脚本

本目录包含手动运行的测试脚本，用于快速验证功能。

## 测试脚本

### test_basic.py
测试 Phase 1 和 Phase 2 的基础功能（不需要 Qt 应用）。

**运行**:
```bash
python tests/manual/test_basic.py
```

**测试内容**:
- 模块导入
- 日志系统
- 异常处理
- Style 数据类
- Serializer 类

### test_phase3_simple.py
测试 Phase 3 的新模块（不需要 Qt 应用）。

**运行**:
```bash
python tests/manual/test_phase3_simple.py
```

**测试内容**:
- PropertyController 导入
- ToolManager 导入和基础功能
- ViewStateMachine 导入和状态枚举

### test_phase1_phase2.py
完整的 Phase 1 和 Phase 2 功能测试（需要 Qt 应用）。

**运行**:
```bash
python tests/manual/test_phase1_phase2.py
```

**注意**: 此脚本需要 GUI 环境，可能在某些环境下出现段错误。

### test_phase3.py
完整的 Phase 3 功能测试（需要 Qt 应用）。

**运行**:
```bash
python tests/manual/test_phase3.py
```

**注意**: 此脚本需要 GUI 环境，可能在某些环境下出现段错误。

## 推荐使用

对于日常测试，推荐使用：
- `test_basic.py` - 快速验证基础功能
- `test_phase3_simple.py` - 快速验证 Phase 3 模块

对于完整测试，使用 pytest：
```bash
pytest tests/unit/ -v
```

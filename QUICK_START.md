# 快速开始指南

## 🚀 立即开始

### 1. 激活环境
```bash
conda activate pnt
```

### 2. 运行测试
```bash
# 快速测试（推荐）
python test_basic.py

# 完整单元测试
pytest tests/unit/ -v

# 查看测试覆盖率
pytest tests/unit/ --cov=app --cov-report=term-missing
```

### 3. 启动应用
```bash
python -m app.main
```

### 4. 查看日志
```bash
# 应用日志
tail -f drawing_app.log

# 测试日志
tail -f test_basic.log
```

---

## 📁 项目结构

```
Graphics/
├── app/                          # 应用代码
│   ├── core/                     # 核心模块
│   │   ├── document.py          # ✨ 文档管理（新）
│   │   ├── selection.py         # ✨ 选择管理（新）
│   │   ├── styles.py            # ✨ 样式管理（新）
│   │   ├── serializer.py        # ✨ 序列化器（重构）
│   │   ├── shapes/              # 图形类
│   │   ├── tools/               # 工具类
│   │   └── commands/            # 撤销/重做命令
│   ├── ui/                      # UI 层
│   │   ├── main_window.py       # 主窗口
│   │   ├── canvas_view.py       # 画布视图
│   │   └── ...
│   ├── utils/                   # ✨ 工具模块（新）
│   │   ├── logging_config.py    # 日志配置
│   │   ├── exceptions.py        # 自定义异常
│   │   └── error_handler.py     # 错误处理
│   └── main.py                  # 应用入口
├── tests/                       # ✨ 测试（新）
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   ├── conftest.py              # pytest 配置
│   └── README.md                # 测试文档
├── .kiro/specs/                 # 规范文档
│   └── app-optimization/        # ✨ 优化项目（新）
│       ├── requirements.md      # 需求文档
│       ├── design.md            # 设计文档
│       └── tasks.md             # 任务列表
├── pytest.ini                   # ✨ pytest 配置（新）
├── requirements-dev.txt         # ✨ 开发依赖（新）
├── test_basic.py               # ✨ 基础测试脚本（新）
├── TEST_REPORT.md              # ✨ 测试报告（新）
└── PROGRESS_SUMMARY.md         # ✨ 进度总结（新）
```

**✨ 标记**: Phase 1 & 2 新增或重构的文件

---

## 🔧 常用命令

### 开发
```bash
# 运行应用
python -m app.main

# 运行特定测试
pytest tests/unit/test_document.py -v

# 运行并显示 print 输出
pytest tests/unit/ -v -s

# 运行标记的测试
pytest -m unit
```

### 代码质量
```bash
# 代码格式化（需要安装 black）
black app/ tests/

# 代码检查（需要安装 pylint）
pylint app/

# 类型检查（需要安装 mypy）
mypy app/
```

### 日志
```bash
# 实时查看应用日志
tail -f drawing_app.log

# 查看最近的日志
tail -20 drawing_app.log

# 搜索错误日志
grep ERROR drawing_app.log
```

---

## 📖 重要文档

### 规范文档
- **需求文档**: `.kiro/specs/app-optimization/requirements.md`
  - 10 个核心需求
  - EARS 格式的验收标准
  
- **设计文档**: `.kiro/specs/app-optimization/design.md`
  - 架构设计
  - 模块设计
  - 性能优化策略
  
- **任务列表**: `.kiro/specs/app-optimization/tasks.md`
  - 24 个主要任务
  - 6 个实施阶段
  - 详细的子任务

### 测试文档
- **测试报告**: `TEST_REPORT.md`
  - 详细的测试结果
  - 代码质量评估
  
- **测试指南**: `tests/README.md`
  - 如何编写测试
  - 如何运行测试

### 进度文档
- **进度总结**: `PROGRESS_SUMMARY.md`
  - 整体进度
  - 已完成工作
  - 下一步计划

---

## 🎯 核心模块使用示例

### 1. Document 模块
```python
from app.core.document import Document
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QUndoStack

# 创建文档
scene = QGraphicsScene()
undo_stack = QUndoStack()
doc = Document(scene, undo_stack)

# 保存
doc.save("my_drawing.json")

# 加载
doc.load("my_drawing.json")

# 导出 PNG
doc.export_png("my_drawing.png")
```

### 2. SelectionManager 模块
```python
from app.core.selection import SelectionManager, SelectionMode

# 创建选择管理器
mgr = SelectionManager(scene)

# 选择图形
mgr.select([item1, item2], SelectionMode.REPLACE)

# 全选
mgr.select_all()

# 清空选择
mgr.clear_selection()

# 获取选中的图形
selected = mgr.get_selected_items()
```

### 3. StyleManager 模块
```python
from app.core.styles import StyleManager, Style
from PySide6.QtGui import QColor

# 创建样式管理器
mgr = StyleManager()

# 创建样式
style = Style(
    pen_color=QColor("#FF0000"),
    pen_width=5.0,
    opacity=0.8
)

# 应用样式
mgr.apply_style(item, style)

# 批量应用
mgr.apply_style_to_selection([item1, item2], style)
```

### 4. 日志使用
```python
from app.utils.logging_config import get_logger

# 获取日志器
logger = get_logger(__name__)

# 记录日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 5. 异常处理
```python
from app.utils.exceptions import SerializationError
from app.utils.error_handler import handle_errors

# 使用装饰器
@handle_errors("保存失败")
def save_file(path):
    if not path:
        raise SerializationError("路径为空")
    # 保存逻辑
    ...

# 手动抛出异常
if error_condition:
    raise SerializationError("序列化失败")
```

---

## 🐛 故障排除

### 问题 1: 模块导入失败
```bash
# 确保在正确的环境
conda activate pnt

# 确保在项目根目录
pwd  # 应该显示 .../Graphics

# 检查 Python 路径
python -c "import sys; print(sys.path)"
```

### 问题 2: 测试失败
```bash
# 查看详细错误
pytest tests/unit/ -v --tb=long

# 运行单个测试
pytest tests/unit/test_document.py::TestDocument::test_save_and_load -v
```

### 问题 3: 应用无法启动
```bash
# 查看日志
cat drawing_app.log

# 检查依赖
pip list | grep PySide6
pip list | grep qt-material
```

### 问题 4: 日志文件过大
```bash
# 清理日志
rm drawing_app.log*
rm test_basic.log

# 日志会自动轮转（10MB，保留5个备份）
```

---

## 📊 当前状态

- ✅ Phase 1: 基础设施搭建 (100%)
- ✅ Phase 2: 核心模块实现 (100%)
- ⏳ Phase 3: 架构重构 (0%)
- ⏳ Phase 4: 性能优化 (0%)
- ⏳ Phase 5: 用户体验改进 (0%)
- ⏳ Phase 6: 验收和发布 (0%)

**总进度**: 33% (2/6 阶段完成)

---

## 🎓 学习资源

### 项目相关
- [PySide6 文档](https://doc.qt.io/qtforpython/)
- [pytest 文档](https://docs.pytest.org/)
- [Python logging 文档](https://docs.python.org/3/library/logging.html)

### 设计模式
- 命令模式 (撤销/重做)
- 策略模式 (工具切换)
- 观察者模式 (信号/槽)
- 单例模式 (日志器)

---

## 💬 获取帮助

### 查看文档
1. 需求不清楚？查看 `requirements.md`
2. 设计疑问？查看 `design.md`
3. 不知道做什么？查看 `tasks.md`
4. 测试问题？查看 `tests/README.md`

### 运行测试
```bash
# 快速验证
python test_basic.py

# 详细测试
pytest tests/unit/ -v
```

### 查看日志
```bash
# 应用日志
tail -f drawing_app.log

# 测试日志
cat test_basic.log
```

---

**提示**: 这是一个持续改进的项目。每完成一个阶段，都会有新的功能和改进！

**下一步**: 开始 Phase 3 - 架构重构 🚀

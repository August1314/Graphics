# 测试文档

本目录包含画图软件的所有测试代码。

## 测试结构

```
tests/
├── unit/           # 单元测试
├── integration/    # 集成测试
├── ui/            # UI 测试
├── conftest.py    # pytest 配置和共享 fixtures
└── README.md      # 本文件
```

## 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定类型的测试
```bash
# 只运行单元测试
pytest tests/unit/

# 只运行集成测试
pytest tests/integration/

# 只运行 UI 测试
pytest tests/ui/
```

### 运行特定测试文件
```bash
pytest tests/unit/test_logging.py
```

### 运行特定测试函数
```bash
pytest tests/unit/test_logging.py::TestLoggingConfig::test_setup_logging_creates_logger
```

### 使用标记运行测试
```bash
# 只运行单元测试标记的测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"
```

## 代码覆盖率

### 生成覆盖率报告
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

覆盖率报告会生成在 `htmlcov/` 目录，用浏览器打开 `htmlcov/index.html` 查看。

### 检查覆盖率阈值
```bash
pytest --cov=app --cov-fail-under=60
```

## 调试测试

### 显示详细输出
```bash
pytest -v
```

### 显示 print 输出
```bash
pytest -s
```

### 在第一个失败时停止
```bash
pytest -x
```

### 进入调试器
```bash
pytest --pdb
```

## 编写测试

### 测试命名规范
- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`

### 使用 fixtures
```python
def test_something(scene, undo_stack):
    # scene 和 undo_stack 是 conftest.py 中定义的 fixtures
    assert scene is not None
    assert undo_stack is not None
```

### 使用标记
```python
import pytest

@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.slow
def test_slow_function():
    pass
```

### 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

## 持续集成

测试应该在每次提交前运行，确保所有测试通过。

```bash
# 运行所有测试并生成覆盖率报告
pytest --cov=app --cov-report=term-missing --cov-fail-under=60
```

## 性能测试

使用 pytest-benchmark 进行性能测试：

```python
def test_performance(benchmark):
    result = benchmark(some_function, arg1, arg2)
    assert result is not None
```

运行性能测试：
```bash
pytest --benchmark-only
```

## 常见问题

### Qt 应用已存在错误
如果遇到 "QApplication instance already exists" 错误，确保使用 `qapp` fixture：

```python
def test_something(qapp):
    # qapp 确保只有一个 QApplication 实例
    pass
```

### 测试隔离
每个测试应该是独立的，不依赖其他测试的状态。使用 fixtures 来设置测试环境。

### 临时文件
使用 pytest 的 `tmp_path` fixture 创建临时文件：

```python
def test_file_operation(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
```

## 参考资料

- [pytest 文档](https://docs.pytest.org/)
- [pytest-qt 文档](https://pytest-qt.readthedocs.io/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)

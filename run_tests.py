#!/usr/bin/env python3
"""
测试运行脚本

运行所有测试并生成报告
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("运行测试套件")
    print("=" * 60)
    print()
    
    # 运行 pytest
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]
    
    print(f"命令: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd)
    
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    print()
    print("覆盖率报告已生成: htmlcov/index.html")
    print()
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())

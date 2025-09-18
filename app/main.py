from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet

from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # 应用 Material 主题（深色），后续可切换 light_*.xml
    try:
        apply_stylesheet(app, theme='light_.xml')
    except Exception:
        pass
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())



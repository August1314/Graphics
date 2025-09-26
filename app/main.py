from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet

from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    # 应用 Material 主题（有效主题名，带兜底）
    try:
        apply_stylesheet(app, theme='light_teal.xml')
    except Exception:
        try:
            apply_stylesheet(app, theme='dark_teal.xml')
        except Exception:
            pass
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())



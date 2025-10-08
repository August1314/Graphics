from __future__ import annotations

import sys
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet

from app.ui.main_window import MainWindow
from app.utils.logging_config import setup_logging


def main() -> int:
    # 初始化日志系统
    logger = setup_logging(level=logging.INFO)
    logger.info("应用启动")
    
    try:
        app = QApplication(sys.argv)
        
        # 应用 Material 主题（有效主题名，带兜底）
        try:
            apply_stylesheet(app, theme='light_teal.xml')
            logger.debug("应用主题: light_teal.xml")
        except Exception as e:
            logger.warning(f"无法应用 light_teal 主题: {e}")
            try:
                apply_stylesheet(app, theme='dark_teal.xml')
                logger.debug("应用主题: dark_teal.xml")
            except Exception as e2:
                logger.warning(f"无法应用 dark_teal 主题: {e2}")
        
        window = MainWindow()
        window.show()
        logger.info("主窗口已显示")
        
        return app.exec()
    except Exception as e:
        logger.critical(f"应用启动失败: {e}", exc_info=True)
        return 1
    finally:
        logger.info("应用退出")


if __name__ == "__main__":
    raise SystemExit(main())



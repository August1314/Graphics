"""主窗口（重构版）

精简的主窗口实现，职责清晰分离。
"""

from __future__ import annotations

import logging
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, 
    QVBoxLayout, QPushButton
)

from app.ui.canvas_view import CanvasView
from app.ui.canvas_scene import CanvasScene
from app.ui.toolbar import ToolBar
from app.ui.property_panel import PropertyPanel
from PySide6.QtGui import QUndoStack

# 核心模块
from app.core.document import Document
from app.core.selection import SelectionManager
from app.core.styles import StyleManager

# 控制器和管理器
from app.controllers.document_controller import DocumentController
from app.controllers.property_controller import PropertyController
from app.managers.tool_manager import ToolManager
from app.state.view_state import ViewStateMachine

# 命令
from app.core.commands.add_shape_cmd import AddShapeCommand
from app.core.commands.delete_shape_cmd import DeleteShapeCommand

logger = logging.getLogger('drawing_app.ui.main_window')


class MainWindow(QMainWindow):
    """主窗口
    
    重构后的主窗口，职责清晰：
    - UI 初始化和布局
    - 协调各个控制器和管理器
    - 处理用户交互事件
    """
    
    def __init__(self) -> None:
        super().__init__()
        
        # 设置窗口
        self.setWindowTitle("二维图形绘图系统")
        self.resize(1000, 700)
        
        # 创建核心组件
        self.scene = CanvasScene(self)
        self.view = CanvasView(self.scene, self)
        self.undo_stack = QUndoStack(self)
        
        # 创建核心模块
        self.document = Document(self.scene, self.undo_stack, self)
        self.selection_mgr = SelectionManager(self.scene, self)
        self.style_mgr = StyleManager(self)
        
        # 创建控制器和管理器
        self.doc_controller = DocumentController(self.document, self, self)
        self.property_controller = PropertyController(
            self.selection_mgr,
            self.style_mgr,
            self.undo_stack,
            self
        )
        self.tool_manager = ToolManager(self.view, self)
        self.state_machine = ViewStateMachine(self)
        
        # 设置中心部件
        self.setCentralWidget(self.view)
        
        # 初始化 UI
        self._init_menu()
        self._init_status_bar()
        self._init_toolbar()
        self._init_docks()
        self._apply_modern_style()
        
        # 连接信号
        self._connect_signals()
        
        logger.info("主窗口初始化完成")
    
    # ==================== UI 初始化 ====================
    
    def _init_menu(self) -> None:
        """初始化菜单栏"""
        try:
            self.menuBar().setNativeMenuBar(False)
        except Exception:
            pass
        
        menu = self.menuBar()
        
        # 文件菜单
        file_menu = menu.addMenu("文件")
        
        action_new = QAction("新建", self)
        action_new.setShortcut("Ctrl+N")
        action_new.triggered.connect(self.doc_controller.new_document)
        
        action_open = QAction("打开...", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self.doc_controller.load_document)
        
        action_save = QAction("保存", self)
        action_save.setShortcut("Ctrl+S")
        action_save.triggered.connect(self.doc_controller.save_document)
        
        action_save_as = QAction("另存为...", self)
        action_save_as.setShortcut("Ctrl+Shift+S")
        action_save_as.triggered.connect(self.doc_controller.save_document_as)
        
        action_export_png = QAction("导出PNG...", self)
        action_export_png.triggered.connect(self.doc_controller.export_png)
        
        action_quit = QAction("退出", self)
        action_quit.setShortcut("Ctrl+Q")
        action_quit.triggered.connect(self.close)
        
        file_menu.addAction(action_new)
        file_menu.addAction(action_open)
        file_menu.addAction(action_save)
        file_menu.addAction(action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(action_export_png)
        file_menu.addSeparator()
        file_menu.addAction(action_quit)
        
        # 编辑菜单
        edit_menu = menu.addMenu("编辑")
        
        action_undo = self.undo_stack.createUndoAction(self, "撤销")
        action_redo = self.undo_stack.createRedoAction(self, "重做")
        action_undo.setShortcut(QKeySequence.Undo)
        action_redo.setShortcut(QKeySequence.Redo)
        
        action_delete = QAction("删除", self)
        action_delete.setShortcut("Delete")
        action_delete.triggered.connect(self._on_delete_selected)
        
        edit_menu.addAction(action_undo)
        edit_menu.addAction(action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(action_delete)
        
        # 视图菜单
        self.view_menu = menu.addMenu("视图")
        
        logger.debug("菜单栏初始化完成")
    
    def _init_status_bar(self) -> None:
        """初始化状态栏"""
        self.statusBar().showMessage("就绪")
    
    def _init_toolbar(self) -> None:
        """初始化工具栏"""
        self.toolbar = ToolBar(self)
        self.addToolBar(self.toolbar)
        
        # 连接工具栏信号
        self.toolbar.toolChanged.connect(self._on_tool_changed)
        
        # 连接快速样式信号
        if hasattr(self.toolbar, 'quickStrokeColorChanged'):
            self.toolbar.quickStrokeColorChanged.connect(
                lambda color: setattr(self.view, '_current_pen_color', color)
            )
        if hasattr(self.toolbar, 'quickStrokeWidthChanged'):
            self.toolbar.quickStrokeWidthChanged.connect(
                lambda w: setattr(self.view, '_current_pen_width', float(w))
            )
        if hasattr(self.toolbar, 'quickStrokeDashChanged'):
            self.toolbar.quickStrokeDashChanged.connect(
                lambda style: setattr(self.view, '_current_pen_style', style)
            )
        
        logger.debug("工具栏初始化完成")
    
    def _init_docks(self) -> None:
        """初始化停靠窗口"""
        # 属性面板
        self.prop_dock = QDockWidget("属性", self)
        self.prop_dock.setObjectName("dock_properties")
        self.prop_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_panel = PropertyPanel(self)
        self.prop_dock.setWidget(self.property_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.prop_dock)
        
        # 添加到视图菜单
        prop_toggle = self.prop_dock.toggleViewAction()
        prop_toggle.setText("属性面板")
        prop_toggle.setShortcut("F7")
        self.view_menu.addAction(prop_toggle)
        
        # 文件操作面板
        io_dock = QDockWidget("文件", self)
        io_dock.setObjectName("dock_io")
        io_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        container = QWidget(self)
        layout = QVBoxLayout(container)
        
        btn_save = QPushButton("保存为 JSON")
        btn_load = QPushButton("加载 JSON")
        btn_save.clicked.connect(self.doc_controller.save_document)
        btn_load.clicked.connect(self.doc_controller.load_document)
        
        layout.addWidget(btn_save)
        layout.addWidget(btn_load)
        layout.addStretch(1)
        
        io_dock.setWidget(container)
        self.addDockWidget(Qt.RightDockWidgetArea, io_dock)
        
        logger.debug("停靠窗口初始化完成")
    
    def _apply_modern_style(self) -> None:
        """应用现代化样式"""
        self.setStyleSheet(
            """
            QMainWindow { background: #f5f7fb; }
            QToolBar { 
                background: rgba(255,255,255,0.9); 
                border: none; 
                padding: 6px; 
                spacing: 8px; 
            }
            QToolBar QToolButton { 
                padding: 6px 10px; 
                border-radius: 6px; 
            }
            QToolBar QToolButton:hover { 
                background: rgba(0,0,0,0.06); 
            }
            QDockWidget::title { 
                padding: 6px 10px; 
                background: rgba(0,0,0,0.04); 
                border-bottom: 1px solid rgba(0,0,0,0.06); 
            }
            QPushButton { 
                border-radius: 6px; 
                padding: 6px 12px; 
            }
            """
        )
    
    # ==================== 信号连接 ====================
    
    def _connect_signals(self) -> None:
        """连接所有信号"""
        # 文档控制器信号
        self.doc_controller.status_message.connect(
            lambda msg: self.statusBar().showMessage(msg)
        )
        
        # 选择管理器信号
        self.selection_mgr.selection_changed.connect(
            self._on_selection_changed
        )
        
        # 视图信号
        self.view.shapeCommitted.connect(self._on_shape_committed)
        self.view.moveCommitted.connect(self._on_move_committed)
        self.view.deleteRequested.connect(self._on_delete_requested)
        
        # 工具管理器信号
        self.tool_manager.tool_changed.connect(
            lambda name, tool: self.statusBar().showMessage(f"当前工具：{name}")
        )
        
        # 属性面板信号（使用 PropertyController）
        self.property_panel.centerChanged.connect(
            lambda cx, cy: self.property_controller.update_center(cx, cy)
        )
        self.property_panel.radiusChanged.connect(
            lambda r: self.property_controller.update_radius(r)
        )
        self.property_panel.strokeColorChanged.connect(
            lambda color: self.property_controller.update_pen_color(color)
        )
        self.property_panel.strokeWidthChanged.connect(
            lambda w: self.property_controller.update_pen_width(float(w))
        )
        self.property_panel.fillColorChanged.connect(
            lambda color: self.property_controller.update_brush_color(color)
        )
        self.property_panel.opacityChanged.connect(
            lambda pct: self.property_controller.update_opacity(pct / 100.0)
        )
        
        logger.debug("信号连接完成")
    
    # ==================== 事件处理 ====================
    
    def _on_tool_changed(self, tool_name: str) -> None:
        """工具变化处理"""
        self.tool_manager.set_tool(tool_name)
        self.view.set_tool(tool_name)
    
    def _on_selection_changed(self, selected_items: list) -> None:
        """选择变化处理"""
        if not selected_items:
            self.property_panel.set_enabled(False)
            return
        
        # 获取第一个选中的项
        item = selected_items[0]
        item_type = type(item).__name__
        
        # 根据类型设置属性面板
        type_map = {
            'CircleItem': 'circle',
            'PointItem': 'point',
            'LineItem': 'line',
            'RectItem': 'rect',
            'PolygonItem': 'polygon',
            'BrushPathItem': 'brush_path'
        }
        
        mode = type_map.get(item_type)
        if mode:
            self.property_panel.build_for(item, mode, self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
        else:
            self.property_panel.set_enabled(False)
    
    def _on_shape_committed(self, item) -> None:
        """图形提交处理"""
        cmd = AddShapeCommand(self.scene, item)
        self.undo_stack.push(cmd)
    
    def _on_move_committed(self, item, old_pos, new_pos) -> None:
        """移动提交处理"""
        from app.core.commands.move_shape_cmd import MoveShapeCommand
        cmd = MoveShapeCommand(item, old_pos, new_pos)
        self.undo_stack.push(cmd)
    
    def _on_delete_requested(self, item) -> None:
        """删除请求处理"""
        cmd = DeleteShapeCommand(self.scene, item)
        self.undo_stack.push(cmd)
    
    def _on_delete_selected(self) -> None:
        """删除选中的图形"""
        for item in list(self.selection_mgr.get_selected_items()):
            cmd = DeleteShapeCommand(self.scene, item)
            self.undo_stack.push(cmd)
    
    # ==================== 窗口事件 ====================
    
    def closeEvent(self, event) -> None:  # type: ignore[override]
        """窗口关闭事件"""
        # 检查是否需要保存
        if self.document.is_modified():
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "保存更改",
                "文档已修改，是否保存？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                if not self.doc_controller.save_document():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        logger.info("主窗口关闭")
        super().closeEvent(event)

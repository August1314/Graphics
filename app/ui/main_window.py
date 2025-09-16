from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QDockWidget, QWidget, QVBoxLayout, QPushButton

from app.ui.canvas_view import CanvasView
from app.ui.canvas_scene import CanvasScene
from app.ui.toolbar import ToolBar
from app.ui.property_panel import PropertyPanel
from PySide6.QtGui import QUndoStack
from app.core.commands.add_shape_cmd import AddShapeCommand
from app.core.commands.delete_shape_cmd import DeleteShapeCommand
from app.core.commands.move_shape_cmd import MoveShapeCommand
from app.core.commands.update_style_cmd import UpdateStyleCommand


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("二维图形绘图系统")
        self.resize(1000, 700)

        self.scene = CanvasScene(self)
        self.view = CanvasView(self.scene, self)
        self.setCentralWidget(self.view)

        self.undo_stack = QUndoStack(self)

        # 设置项：切回选择工具时恢复上次选择
        self._restore_prev_selection_enabled: bool = True
        self._prev_selected_items: list = []

        self._init_menu()
        self._init_status_bar()
        self._init_toolbar()
        self._init_docks()

    def _init_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("文件")
        settings_menu = menu.addMenu("设置")
        edit_menu = menu.addMenu("编辑")

        action_open = QAction("打开...", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self._on_open)

        action_save_png = QAction("导出PNG...", self)
        action_save_png.triggered.connect(self._on_export_png)

        action_quit = QAction("退出", self)
        action_quit.setShortcut("Ctrl+Q")
        action_quit.triggered.connect(self.close)

        file_menu.addAction(action_open)
        file_menu.addAction(action_save_png)
        file_menu.addSeparator()
        file_menu.addAction(action_quit)

        # 设置：切回选择工具时恢复上次选择
        self.action_restore_prev_selection = QAction("切回‘选择’时恢复上次选择", self)
        self.action_restore_prev_selection.setCheckable(True)
        self.action_restore_prev_selection.setChecked(self._restore_prev_selection_enabled)
        self.action_restore_prev_selection.toggled.connect(self._on_toggle_restore_prev_selection)
        settings_menu.addAction(self.action_restore_prev_selection)

        # 撤销/重做
        action_undo = self.undo_stack.createUndoAction(self, "撤销")
        action_redo = self.undo_stack.createRedoAction(self, "重做")
        action_undo.setShortcut("Ctrl+Z")
        action_redo.setShortcut("Ctrl+Y")
        edit_menu.addAction(action_undo)
        edit_menu.addAction(action_redo)

    def _init_status_bar(self) -> None:
        self.statusBar().showMessage("就绪")

    def _init_toolbar(self) -> None:
        self.tools = ToolBar(self)
        self.addToolBar(self.tools)
        self.tools.toolChanged.connect(self._on_tool_changed)

    def _init_docks(self) -> None:
        # 属性面板 Dock
        prop_dock = QDockWidget("属性", self)
        prop_dock.setObjectName("dock_properties")
        prop_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_panel = PropertyPanel(self)
        prop_dock.setWidget(self.property_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, prop_dock)

        # JSON 保存/加载 Dock（面板+按钮）
        io_dock = QDockWidget("文件", self)
        io_dock.setObjectName("dock_io")
        io_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        container = QWidget(self)
        v = QVBoxLayout(container)
        btn_save = QPushButton("保存为 JSON")
        btn_load = QPushButton("加载 JSON")
        btn_save.clicked.connect(self._on_save_json)
        btn_load.clicked.connect(self._on_load_json)
        v.addWidget(btn_save)
        v.addWidget(btn_load)
        v.addStretch(1)
        io_dock.setWidget(container)
        self.addDockWidget(Qt.RightDockWidgetArea, io_dock)

        # 绑定属性面板与场景选择
        self.scene.selectionChanged.connect(self._on_scene_selection_changed)
        pp = self.property_panel
        pp.set_enabled(False)
        pp.centerChanged.connect(self._on_center_changed)
        pp.radiusChanged.connect(self._on_radius_changed)
        pp.strokeColorChanged.connect(self._on_stroke_color_changed)
        pp.strokeWidthChanged.connect(self._on_stroke_width_changed)
        pp.fillColorChanged.connect(self._on_fill_color_changed)
        pp.opacityChanged.connect(self._on_opacity_changed)
        # 线型联动
        pp.combo_dash.currentIndexChanged.connect(self._on_dash_style_changed)

        # 视图事件接入撤销/重做
        self.view.shapeCommitted.connect(self._on_shape_committed)
        self.view.moveCommitted.connect(self._on_move_committed)
        self.view.deleteRequested.connect(self._on_delete_requested)
        self.view.selectionGeometryChanged.connect(self._on_scene_selection_changed)

        # 删除快捷键
        self._delete_action = QAction("删除", self)
        self._delete_action.setShortcut("Delete")
        self._delete_action.triggered.connect(self._on_delete_selected)
        self.addAction(self._delete_action)

    def _on_open(self) -> None:
        QFileDialog.getOpenFileName(self, "打开文件", "", "JSON 文件 (*.json)")

    def _on_export_png(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "导出 PNG", "scene.png", "PNG 文件 (*.png)")
        if not path:
            return
        ok = self.view.export_png(path)
        if ok:
            self.statusBar().showMessage(f"已导出: {path}")
        else:
            QMessageBox.warning(self, "导出失败", "导出 PNG 失败")

    def _on_tool_changed(self, name: str) -> None:
        self.statusBar().showMessage(f"当前工具：{name}")
        self.view.set_tool(name)
        # 切换工具时处理选择记忆/清理
        if name != "select":
            # 记录当前选择并清除
            self._prev_selected_items = [item for item in self.scene.selectedItems()]
            self.scene.clearSelection()
        else:
            # 切回选择工具：根据设置恢复上次选择
            if self._restore_prev_selection_enabled and self._prev_selected_items:
                for item in list(self._prev_selected_items):
                    if item.scene() is self.scene:
                        item.setSelected(True)
                # 可选择保留记忆或清空，这里保留一轮

    def _on_toggle_restore_prev_selection(self, checked: bool) -> None:
        self._restore_prev_selection_enabled = checked

    # ---- 属性联动 ----
    def _get_selected_circle(self):
        items = self.scene.selectedItems()
        if not items:
            return None
        item = items[0]
        # 仅当为圆形（QGraphicsEllipseItem 派生）时联动
        from app.core.shapes.circle_item import CircleItem

        if isinstance(item, CircleItem):
            return item
        return None

    def _on_scene_selection_changed(self) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            self.property_panel.set_enabled(False)
            return
        cx, cy, r = circle.center_radius()
        p = circle.pen()
        stroke = p.color()
        width = p.widthF()
        fill = circle.brush().color()
        opacity_pct = int(round(circle.opacity() * 100))
        self.property_panel.set_from_circle(cx, cy, r, stroke, width, fill, opacity_pct)
        # 同步线型
        from PySide6.QtCore import Qt as _Qt
        self.property_panel.combo_dash.blockSignals(True)
        self.property_panel.combo_dash.setCurrentIndex(0 if p.style() == _Qt.PenStyle.SolidLine else 1)
        self.property_panel.combo_dash.blockSignals(False)
        self.property_panel.set_enabled(True)

    def _on_center_changed(self, cx: float, cy: float) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        ox, oy, r = circle.center_radius()
        def apply():
            circle.set_center_radius(cx, cy, r)
        def revert():
            circle.set_center_radius(ox, oy, r)
        self.undo_stack.push(UpdateStyleCommand.make("修改中心", apply, revert))

    def _on_radius_changed(self, r: float) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        cx, cy, old_r = circle.center_radius()
        nr = max(0.0, r)
        def apply():
            circle.set_center_radius(cx, cy, nr)
        def revert():
            circle.set_center_radius(cx, cy, old_r)
        self.undo_stack.push(UpdateStyleCommand.make("修改半径", apply, revert))

    def _on_stroke_color_changed(self, color) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        pen = circle.pen()
        old = pen.color()
        def apply():
            p = circle.pen()
            p.setColor(color)
            circle.setPen(p)
        def revert():
            p = circle.pen()
            p.setColor(old)
            circle.setPen(p)
        self.undo_stack.push(UpdateStyleCommand.make("修改描边颜色", apply, revert))

    def _on_stroke_width_changed(self, width: int) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        pen = circle.pen()
        old = pen.widthF()
        nw = max(0.1, float(width))
        def apply():
            p = circle.pen()
            p.setWidthF(nw)
            circle.setPen(p)
        def revert():
            p = circle.pen()
            p.setWidthF(old)
            circle.setPen(p)
        self.undo_stack.push(UpdateStyleCommand.make("修改线宽", apply, revert))

    def _on_fill_color_changed(self, color) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        from PySide6.QtGui import QBrush
        old = circle.brush().color()
        def apply():
            circle.setBrush(QBrush(color))
        def revert():
            circle.setBrush(QBrush(old))
        self.undo_stack.push(UpdateStyleCommand.make("修改填充颜色", apply, revert))

    def _on_opacity_changed(self, pct: int) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        old = circle.opacity()
        new = max(0.0, min(1.0, pct / 100.0))
        def apply():
            circle.setOpacity(new)
        def revert():
            circle.setOpacity(old)
        self.undo_stack.push(UpdateStyleCommand.make("修改不透明度", apply, revert))

    def _on_dash_style_changed(self, idx: int) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            return
        pen = circle.pen()
        from PySide6.QtCore import Qt as _Qt
        old = pen.style()
        new = _Qt.PenStyle.SolidLine if idx == 0 else _Qt.PenStyle.DashLine
        def apply():
            p = circle.pen()
            p.setStyle(new)
            circle.setPen(p)
        def revert():
            p = circle.pen()
            p.setStyle(old)
            circle.setPen(p)
        self.undo_stack.push(UpdateStyleCommand.make("修改线型", apply, revert))

    def _on_delete_selected(self) -> None:
        # 改为走撤销命令
        for item in list(self.scene.selectedItems()):
            self.undo_stack.push(DeleteShapeCommand(self.scene, item))

    # ---- 撤销/重做接入 ----
    def _on_shape_committed(self, item) -> None:
        self.undo_stack.push(AddShapeCommand(self.scene, item))

    def _on_move_committed(self, item, old_pos, new_pos) -> None:
        self.undo_stack.push(MoveShapeCommand(item, old_pos, new_pos))

    def _on_delete_requested(self, item) -> None:
        self.undo_stack.push(DeleteShapeCommand(self.scene, item))

    def _on_save_json(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "保存为 JSON", "scene.json", "JSON 文件 (*.json)")
        if not path:
            return
        # 先放置占位逻辑：后续接入 serializer
        try:
            import json
            from datetime import datetime

            data = {
                "name": "scene-1",
                "canvas": {"width": 1200, "height": 800, "zoom": 1, "pan": {"x": 0, "y": 0}},
                "savedAt": datetime.now().isoformat(),
                "shapes": [
                    {"type": "rect", "x": 100, "y": 120, "width": 200, "height": 100, "strokeColor": "#00AA00", "strokeWidth": 3, "fillColor": "#FF0000"},
                    {"type": "circle", "cx": 460, "cy": 260, "r": 60, "strokeColor": "#0066cc", "strokeWidth": 2}
                ],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.statusBar().showMessage(f"已保存: {path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _on_load_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "加载 JSON", "", "JSON 文件 (*.json)")
        if not path:
            return
        # 占位：后续替换为 serializer.load
        try:
            import json

            with open(path, "r", encoding="utf-8") as f:
                _ = json.load(f)
            self.statusBar().showMessage(f"已加载: {path}")
        except Exception as e:
            QMessageBox.critical(self, "加载失败", str(e))



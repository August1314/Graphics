from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QCursor
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
from app.core.shapes.point_item import PointItem
from app.core.shapes.line_item import LineItem
from app.core.shapes.rect_item import RectItem
from app.core.shapes.polygon_item import PolygonItem
from app.core.shapes.brush_path_item import BrushPathItem


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
        debug_menu = menu.addMenu("调试")

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
        action_undo.setShortcut(QKeySequence.Undo)
        action_redo.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(action_undo)
        edit_menu.addAction(action_redo)

        # 复制/粘贴（Cmd/Ctrl 自动适配）
        action_copy = QAction("复制", self)
        action_copy.setShortcut(QKeySequence.Copy)
        action_copy.triggered.connect(self._on_copy)
        edit_menu.addAction(action_copy)

        action_paste = QAction("粘贴", self)
        action_paste.setShortcut(QKeySequence.Paste)
        action_paste.triggered.connect(self._on_paste)
        edit_menu.addAction(action_paste)

        # 调试：查看剪贴板文本
        action_clip = QAction("查看剪贴板文本", self)
        action_clip.triggered.connect(self._on_show_clipboard)
        debug_menu.addAction(action_clip)

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
        pp.lineP1Changed.connect(self._on_line_p1_changed)
        pp.lineP2Changed.connect(self._on_line_p2_changed)
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
        self.view.copyCompleted.connect(self._on_copy_completed)
        self.view.pasteCompleted.connect(self._on_paste_completed)

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

    def _get_selected_point(self):
        items = self.scene.selectedItems()
        if not items:
            return None
        item = items[0]
        if isinstance(item, PointItem):
            return item
        return None

    def _get_selected_line(self):
        items = self.scene.selectedItems()
        if not items:
            return None
        item = items[0]
        if isinstance(item, LineItem):
            return item
        return None

    def _get_selected_rect(self):
        items = self.scene.selectedItems()
        if not items:
            return None
        item = items[0]
        if isinstance(item, RectItem):
            return item
        return None

    def _get_selected_polygon(self):
        items = self.scene.selectedItems()
        if not items:
            return None
        item = items[0]
        if isinstance(item, PolygonItem):
            return item
        return None
    
    def _get_selected_brush_path(self):
        items = self.scene.selectedItems()
        if not items:
            return None
        item = items[0]
        if isinstance(item, BrushPathItem):
            return item
        return None

    def _on_scene_selection_changed(self) -> None:
        circle = self._get_selected_circle()
        if circle is not None:
            self.property_panel.set_mode("circle")
            # 动态装配组件
            self.property_panel.build_for(circle, "circle", self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
            return
        point = self._get_selected_point()
        if point is not None:
            self.property_panel.set_mode("point")
            self.property_panel.build_for(point, "point", self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
            return
        line = self._get_selected_line()
        if line is not None:
            self.property_panel.set_mode("line")
            self.property_panel.build_for(line, "line", self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
            return
        # 矩形
        rect = self._get_selected_rect()
        if rect is not None:
            self.property_panel.build_for(rect, "rect", self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
            return
        poly = self._get_selected_polygon()
        if poly is not None:
            self.property_panel.build_for(poly, "polygon", self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
            return
        brush_path = self._get_selected_brush_path()
        if brush_path is not None:
            self.property_panel.build_for(brush_path, "brush_path", self.scene, self.undo_stack)
            self.property_panel.set_enabled(True)
            return
        self.property_panel.set_enabled(False)

    def _on_center_changed(self, cx: float, cy: float) -> None:
        circle = self._get_selected_circle()
        if circle is None:
            # Point
            point = self._get_selected_point()
            if point is None:
                return
            ox, oy = point.pos().x(), point.pos().y()
            def apply():
                point.setPos(cx, cy)
            def revert():
                point.setPos(ox, oy)
            self.undo_stack.push(UpdateStyleCommand.make("移动点", apply, revert))
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
            # Point 半径
            point = self._get_selected_point()
            if point is None:
                return
            rect = point.rect(); old_r = rect.width() / 2.0
            nr = max(0.1, r)
            def apply():
                point.setRect(-nr, -nr, 2*nr, 2*nr)
            def revert():
                point.setRect(-old_r, -old_r, 2*old_r, 2*old_r)
            self.undo_stack.push(UpdateStyleCommand.make("修改点半径", apply, revert))
            return
        cx, cy, old_r = circle.center_radius()
        nr = max(0.0, r)
        def apply():
            circle.set_center_radius(cx, cy, nr)
        def revert():
            circle.set_center_radius(cx, cy, old_r)
        self.undo_stack.push(UpdateStyleCommand.make("修改半径", apply, revert))

    def _on_stroke_color_changed(self, color) -> None:
        # Circle or Point or Line
        circle = self._get_selected_circle()
        if circle is not None:
            pen = circle.pen(); old = pen.color()
            def apply():
                p = circle.pen(); p.setColor(color); circle.setPen(p)
                self.scene.update_base_style(circle)
            def revert():
                p = circle.pen(); p.setColor(old); circle.setPen(p)
                self.scene.update_base_style(circle)
            self.undo_stack.push(UpdateStyleCommand.make("修改描边颜色", apply, revert))
            return
        point = self._get_selected_point()
        if point is not None:
            pen = point.pen(); old = pen.color()
            def apply():
                p = point.pen(); p.setColor(color); point.setPen(p)
                self.scene.update_base_style(point)
            def revert():
                p = point.pen(); p.setColor(old); point.setPen(p)
                self.scene.update_base_style(point)
            self.undo_stack.push(UpdateStyleCommand.make("修改描边颜色", apply, revert))
            return
        line = self._get_selected_line()
        if line is not None:
            pen = line.pen(); old = pen.color()
            def apply():
                p = line.pen(); p.setColor(color); line.setPen(p)
                self.scene.update_base_style(line)
            def revert():
                p = line.pen(); p.setColor(old); line.setPen(p)
                self.scene.update_base_style(line)
            self.undo_stack.push(UpdateStyleCommand.make("修改描边颜色", apply, revert))

    def _on_stroke_width_changed(self, width: int) -> None:
        nw = max(0.1, float(width))
        circle = self._get_selected_circle()
        if circle is not None:
            old = circle.pen().widthF()
            def apply():
                p = circle.pen(); p.setWidthF(nw); circle.setPen(p)
                self.scene.update_base_style(circle)
            def revert():
                p = circle.pen(); p.setWidthF(old); circle.setPen(p)
                self.scene.update_base_style(circle)
            self.undo_stack.push(UpdateStyleCommand.make("修改线宽", apply, revert))
            return
        point = self._get_selected_point()
        if point is not None:
            old = point.pen().widthF()
            def apply():
                p = point.pen(); p.setWidthF(nw); point.setPen(p)
                self.scene.update_base_style(point)
            def revert():
                p = point.pen(); p.setWidthF(old); point.setPen(p)
                self.scene.update_base_style(point)
            self.undo_stack.push(UpdateStyleCommand.make("修改线宽", apply, revert))
            return
        line = self._get_selected_line()
        if line is not None:
            old = line.pen().widthF()
            def apply():
                p = line.pen(); p.setWidthF(nw); line.setPen(p)
                self.scene.update_base_style(line)
            def revert():
                p = line.pen(); p.setWidthF(old); line.setPen(p)
                self.scene.update_base_style(line)
            self.undo_stack.push(UpdateStyleCommand.make("修改线宽", apply, revert))

    def _on_fill_color_changed(self, color) -> None:
        # 仅 Circle/Point 支持填充
        from PySide6.QtGui import QBrush
        circle = self._get_selected_circle()
        if circle is not None:
            old = circle.brush().color()
            def apply():
                circle.setBrush(QBrush(color))
                self.scene.update_base_style(circle)
            def revert():
                circle.setBrush(QBrush(old))
                self.scene.update_base_style(circle)
            self.undo_stack.push(UpdateStyleCommand.make("修改填充颜色", apply, revert))
            return
        point = self._get_selected_point()
        if point is not None:
            old = point.brush().color()
            def apply():
                point.setBrush(QBrush(color))
                self.scene.update_base_style(point)
            def revert():
                point.setBrush(QBrush(old))
                self.scene.update_base_style(point)
            self.undo_stack.push(UpdateStyleCommand.make("修改填充颜色", apply, revert))

    def _on_opacity_changed(self, pct: int) -> None:
        new = max(0.0, min(1.0, pct / 100.0))
        circle = self._get_selected_circle()
        if circle is not None:
            old = circle.opacity()
            def apply():
                circle.setOpacity(new)
                self.scene.update_base_style(circle)
            def revert():
                circle.setOpacity(old)
                self.scene.update_base_style(circle)
            self.undo_stack.push(UpdateStyleCommand.make("修改不透明度", apply, revert))
            return
        point = self._get_selected_point()
        if point is not None:
            old = point.opacity()
            def apply():
                point.setOpacity(new)
                self.scene.update_base_style(point)
            def revert():
                point.setOpacity(old)
                self.scene.update_base_style(point)
            self.undo_stack.push(UpdateStyleCommand.make("修改不透明度", apply, revert))
            return
        line = self._get_selected_line()
        if line is not None:
            old = line.opacity()
            def apply():
                line.setOpacity(new)
                self.scene.update_base_style(line)
            def revert():
                line.setOpacity(old)
                self.scene.update_base_style(line)
            self.undo_stack.push(UpdateStyleCommand.make("修改不透明度", apply, revert))

    def _on_dash_style_changed(self, idx: int) -> None:
        from PySide6.QtCore import Qt as _Qt
        new = _Qt.PenStyle.SolidLine if idx == 0 else _Qt.PenStyle.DashLine
        circle = self._get_selected_circle()
        if circle is not None:
            old = circle.pen().style()
            def apply():
                p = circle.pen(); p.setStyle(new); circle.setPen(p)
                self.scene.update_base_style(circle)
            def revert():
                p = circle.pen(); p.setStyle(old); circle.setPen(p)
                self.scene.update_base_style(circle)
            self.undo_stack.push(UpdateStyleCommand.make("修改线型", apply, revert))
            return
        line = self._get_selected_line()
        if line is not None:
            old = line.pen().style()
            def apply():
                p = line.pen(); p.setStyle(new); line.setPen(p)
                self.scene.update_base_style(line)
            def revert():
                p = line.pen(); p.setStyle(old); line.setPen(p)
                self.scene.update_base_style(line)
            self.undo_stack.push(UpdateStyleCommand.make("修改线型", apply, revert))

    def _on_delete_selected(self) -> None:
        # 改为走撤销命令
        for item in list(self.scene.selectedItems()):
            self.undo_stack.push(DeleteShapeCommand(self.scene, item))

    # 直线端点
    def _on_line_p1_changed(self, x1: float, y1: float) -> None:
        line = self._get_selected_line()
        if line is None:
            return
        ln = line.line(); old = (ln.x1(), ln.y1(), ln.x2(), ln.y2())
        def apply():
            line.set_points(x1, y1, old[2], old[3])
        def revert():
            line.set_points(old[0], old[1], old[2], old[3])
        self.undo_stack.push(UpdateStyleCommand.make("修改直线起点", apply, revert))

    def _on_line_p2_changed(self, x2: float, y2: float) -> None:
        line = self._get_selected_line()
        if line is None:
            return
        ln = line.line(); old = (ln.x1(), ln.y1(), ln.x2(), ln.y2())
        def apply():
            line.set_points(old[0], old[1], x2, y2)
        def revert():
            line.set_points(old[0], old[1], old[2], old[3])
        self.undo_stack.push(UpdateStyleCommand.make("修改直线终点", apply, revert))

    def _on_copy(self) -> None:
        # 若无选中，尝试根据鼠标位置命中一个图元后再复制
        if not self.scene.selectedItems():
            pos_view = self.view.mapFromGlobal(QCursor.pos())
            hit = self.view.itemAt(pos_view)
            if hit is not None:
                self.scene.clearSelection()
                hit.setSelected(True)
        self.view.copy_selected()

    def _on_paste(self) -> None:
        # 进入“点击画布以粘贴”模式，由用户点击决定位置
        self.statusBar().showMessage("请在画布上点击以粘贴…")
        self.view.begin_paste_from_clipboard()

    def _on_copy_completed(self, ok: bool) -> None:
        if ok:
            self.statusBar().showMessage("复制成功", 3000)
        else:
            self.statusBar().showMessage("复制失败：无支持的圆形", 3000)
            QMessageBox.warning(self, "复制失败", "请确保选中或鼠标在圆/椭圆上再执行复制。")

    def _on_paste_completed(self, ok: bool) -> None:
        self.statusBar().showMessage("粘贴成功" if ok else "粘贴失败：剪贴板无有效数据", 3000)

    def _on_show_clipboard(self) -> None:
        # 展示当前剪贴板的纯文本与可用 MIME 格式
        try:
            from PySide6.QtWidgets import QApplication
            cb = QApplication.clipboard()
            md = cb.mimeData()
            text = cb.text() or "<空>"
            formats = ", ".join(md.formats()) if md is not None else "<无>"
            preview = text if len(text) < 500 else text[:500] + "…"
            QMessageBox.information(self, "剪贴板内容",
                                    f"MIME 格式: {formats}\n\n文本预览:\n{preview}")
        except Exception as e:
            QMessageBox.warning(self, "读取失败", str(e))

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



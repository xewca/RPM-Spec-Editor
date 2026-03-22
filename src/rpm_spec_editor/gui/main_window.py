from enum import Enum

from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QAction
)
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QTimer, QModelIndex, Qt, QItemSelectionModel

from rpm_spec_editor.core.app_controller import AppController
from rpm_spec_editor.gui.text_editor import TextEditor
from rpm_spec_editor.storage.file_manager import FileAccessError
from rpm_spec_editor.gui.structure_view import StructureView
from rpm_spec_editor.gui.spec_tree_model import SpecTreeModel
from rpm_spec_editor.gui.navigation import NavigationService
from rpm_spec_editor.gui.editor_commands import EditorCommands
from rpm_spec_editor.gui.navigation_types import NavigationSource

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RPM Spec Editor")
        self.resize(900, 600)
        self.controller = AppController()

        self.editor = TextEditor(self)
        self.structure_view = StructureView(self)

        self._tree_model = SpecTreeModel()
        self.structure_view.setModel(self._tree_model)

        self.navigation = NavigationService(self._tree_model)

        self.commands = EditorCommands(
            editor=self.editor,
            navigation=self.navigation,
            main_window=self
        )
        self.structure_view.set_commands(self.commands)

        self.structure_view.expandRequested.connect(lambda idx: self.structure_view.expand(idx))
        self.structure_view.collapseRequested.connect(lambda idx: self.structure_view.collapse(idx))
        self.structure_view.activated.connect(self._on_structure_item_activated)

        self.structure_view.jumpRequested.connect(self._on_tree_jump)
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

        self._rebuild_timer = QTimer(self)
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.timeout.connect(self._rebuild_structure)

        splitter = QSplitter(self)
        splitter.addWidget(self.structure_view)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

        self._navigation_lock = False
        self._navigation_source: NavigationSource | None = None

        self._create_menu()

    def sync_tree_to_line(self, line_no: int):
        index = self._tree_model.index_for_line(line_no)
        if not index.isValid():
            return

        self.structure_view.selectionMode().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        self.structure_view.scrollTo(index)

    def _on_text_changed(self):
        doc = self.controller.current_document
        if not doc:
            return

        self.editor.clear_highlight()
        doc.content = self.editor.get_content()
        self._update_window_title()

        self._rebuild_timer.start(400)

    def _rebuild_structure(self):
        doc = self.controller.current_document
        if not doc:
            return

        parsed = doc.parse()
        issues = self.controller.validator.validate(parsed)

        expanded = self._save_expanded_lines()

        self._tree_model.rebuild(parsed)
        self._tree_model.update_issues(issues)

        self._restore_expanded_lines(expanded)

        self._expand_issues_if_needed()

    def _on_tree_jump(self, line_no: int):
        self._navigate_to_line(line_no, NavigationSource.TREE)
        self.editor.setFocus(Qt.OtherFocusReason)

    def _expand_issues_if_needed(self):
        model = self.structure_view.model()
        if not model:
            return

        index = model.get_issues_root_index()
        if not index or not index.isValid():
            return

        self.structure_view.expand(index)

    def _save_expanded_lines(self) -> set[int]:
        view = self.structure_view
        model = view.model()
        if not model:
            return set()

        expanded = set()

        def walk(index):
            if view.isExpanded(index):
                item = index.internalPointer()
                if item and item.line_no is not None:
                    expanded.add(item.line_no)

            for row in range(model.rowCount(index)):
                child = model.index(row, 0, index)
                walk(child)

        root = QModelIndex()
        for row in range(model.rowCount(root)):
            walk(model.index(row, 0, root))

        return expanded

    def _restore_expanded_lines(self, lines: set[int]):
        model = self.structure_view.model()
        if not isinstance(model, SpecTreeModel):
            return

        for line_no in lines:
            index = model.find_section_for_line(line_no)
            if index and index.isValid():
                self.structure_view.expand(index)

    def _on_cursor_position_changed(self):
        if self._navigation_lock:
            return

        cursor = self.editor.textCursor()
        line_no = cursor.blockNumber() + 1

        model = self.structure_view.model()
        if isinstance(model, SpecTreeModel):
            model.set_active_line(line_no)

        range_ = model.get_active_section_range()
        if range_:
            self.editor.highlight_range(*range_)
        else:
            self.editor.clear_range_highlight()

        self._navigate_to_line(line_no, NavigationSource.EDITOR) # source="editor"

    def _create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("Файл")

        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_file)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        nav_menu = menu.addMenu("Навигация")

        go_to_section = QAction("Перейти к секции...", self)
        go_to_section.setShortcut("Ctrl+G")
        go_to_section.triggered.connect(self._show_go_to_section_dialog)

        select_section = QAction("Выделить секцию", self)
        select_section.setShortcut("Ctrl+Alt+S")
        select_section.triggered.connect(self.commands.select_current_section)

        first_section = QAction("Первая секция", self)
        first_section.setShortcut("Ctrl+Home")
        first_section.triggered.connect(self.commands.go_to_first_section)

        last_section = QAction("Последняя секция", self)
        last_section.setShortcut("Ctrl+End")
        last_section.triggered.connect(self.commands.go_to_last_section)

        prev_section = QAction("Предыдущая секция", self)
        prev_section.setShortcut("Alt+Up")
        prev_section.triggered.connect(self.commands.go_to_prev_section)

        next_section = QAction("Следующая секция", self)
        next_section.setShortcut("Alt+Down")
        next_section.triggered.connect(self.commands.go_to_next_section)

        nav_menu.addAction(go_to_section)
        nav_menu.addSeparator()
        nav_menu.addAction(first_section)
        nav_menu.addAction(last_section)
        nav_menu.addSeparator()
        nav_menu.addAction(prev_section)
        nav_menu.addAction(next_section)

        view_menu = menu.addMenu("Вид")

        toggle_section = QAction("Свернуть / развернуть секцию", self)
        toggle_section.setShortcut("Ctrl+Alt+C")
        toggle_section.triggered.connect(self.commands.toggle_current_section)

        view_menu.addAction(toggle_section)

    def _on_editor_cursor_changed(self):
        cursor = self.editor.textCursor()
        line_no = cursor.blockNumber() + 1
        self._navigate_to_line(line_no, NavigationSource.EDITOR)

    def _sync_tree_with_editor(self, line_no: int):
        index = self.spec_tree_model.find_index_by_line(line_no)
        if not index or not index.isValid():
            return

        self._sync_in_progress = True
        try:
            self.structure_view.select_index(index)
        finally:
            self._sync_in_progress = False

    def _show_go_to_section_dialog(self):
        pass

    def jump_to_line(self, line_no: int):
        if line_no is None:
            return

        editor = self.editor

        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.MoveAnchor,
            max(0, line_no)
        )

        editor.setTextCursor(cursor)
        editor.setFocus()
        editor.centerCursor()


    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть spec-файл",
            "",
            "RPM spec files (*.spec)"
        )

        try:
            document = self.controller.open_file(path)

            self.editor.set_content(document.content)

            parsed = document.parse()
            issues = self.controller.validator.validate(parsed)

            self._tree_model.rebuild(parsed)
            self._tree_model.update_issues(issues)

            self._update_window_title()
        except FileAccessError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def save_file(self):
        try:
            self.controller.save_current()
            self._update_window_title()
        except FileAccessError as exc:
            QMessageBox.critical(self, "Ошбика", str(exc))

    def _update_window_title(self):
        doc = self.controller.current_document
        if not doc:
            self.setWindowTitle("RPM Spec Editor")
            return

        modified = " *" if doc.is_modified else ""
        self.setWindowTitle(f"RPM Spec Editor - {doc.path.name}{modified}")

    def _select_tree_item_by_line(self, line_no: int):
        if self._navigation_lock:
            return

        model = self.structure_view.model()
        if not isinstance(model, SpecTreeModel):
            return

        index = model.find_index_by_line(line_no)
        if not index or not index.isValid():
            return

        self._navigation_lock = True
        try:
            parent = index.parent()
            while parent.isValid():
                self.structure_view.expand(parent)
                parent = parent.parent()

            # self.structure_view.setCurrentIndex(index)
            selection = self.structure_view.selectionModel()
            selection.setCurrentIndex(
                index,
                QItemSelectionModel.ClearAndSelect
            )
            self.structure_view.scrollTo(index)
        finally:
            self._navigation_lock = False

    def _navigate_to_line(self, line_no, source):
        """
        if self._navigation_source is not None:
            return

        self._navigation_source = source
        try:
            if source == NavigationSource.EDITOR:
                self._select_tree_item_by_line(line_no)
            elif source == NavigationSource.TREE:
                self._jump_editor_to_line(line_no)
        finally:
            self._navigation_source = None

        if source != "editor":
            self._jump_editor_to_line(line_no)

        if source != "tree":
            self._select_tree_item_by_line(line_no)
        """
        if self._navigation_lock:
            return

        self._navigation_lock = True
        try:
            if source != NavigationSource.EDITOR:
                self.editor.move_to_line(line_no)

            if source != NavigationSource.TREE:
                self._select_tree_item_by_line(line_no)
        finally:
            self._navigation_lock = False

    def _jump_editor_to_line(self, line_no: int):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.MoveAnchor,
            max(0, line_no - 1)
        )
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()

    def _on_structure_item_activated(self, index):
        model = self.structure_view.model()
        if not isinstance(model, SpecTreeModel):
            return

        item = model.item_from_index(index)
        if not item or item.line_no is None:
            return

        self._navigate_to_line(
            item.line_no,
            NavigationSource.STRUCTURE
        )
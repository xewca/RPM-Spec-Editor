from enum import Enum
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QAction,
    QTextEdit,
    QTreeWidget,
    QTreeView,
    QTreeWidgetItem,
    QShortcut,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPlainTextEdit,
    QTabWidget,
    QFileSystemModel,
    QTabBar,
)
from PyQt5.QtGui import (
    QTextCursor,
    QKeySequence,
    QTextDocument,
    QFont
)
from PyQt5.QtCore import (
    QTimer,
    QModelIndex,
    Qt,
    QItemSelectionModel,
    QThread
)

from rpm_spec_editor.core.app_controller import AppController
from rpm_spec_editor.storage.file_manager import FileAccessError
from rpm_spec_editor.gui.structure_view import StructureView
from rpm_spec_editor.gui.spec_tree_model import SpecTreeModel
from rpm_spec_editor.gui.navigation import NavigationService
from rpm_spec_editor.gui.editor_commands import EditorCommands
from rpm_spec_editor.gui.navigation_types import NavigationSource
from rpm_spec_editor.gui.code_editor import CodeEditor
from rpm_spec_editor.gui.search_bar import SearchBar
from rpm_spec_editor.gui.styles import build_style
from rpm_spec_editor.gui.theme import DARK_COLORS, LIGHT_COLORS
from rpm_spec_editor.core.settings_manager import SettingsManager
from rpm_spec_editor.gui.dialogs.settings_dialog import SettingsDialog
from rpm_spec_editor.gui.workers.build_worker import BuildWorker
from rpm_spec_editor.gui.recovery_dialog import RecoveryDialog
from rpm_spec_editor.core.session_manager import SessionManager
from rpm_spec_editor.gui.formatter import align_spec_fields

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RPM Spec Editor")
        self.resize(900, 600)
        self.settings = SettingsManager()
        self.controller = AppController()
        self.session_manager = SessionManager()
        self._is_modified = False
        self.controller.settings = self.settings

        self.current_theme = self.settings.get("theme", "dark")
        self._tree_model = SpecTreeModel()
        self.structure_view = StructureView(self)
        self.structure_view.setModel(self._tree_model)
        self.metadata_tree = QTreeWidget()
        self.metadata_tree.setHeaderLabels(["Поле", "Значение"])
        self.metadata_tree.setColumnWidth(0, 120)

        # self.editor = CodeEditor()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.editor = None

        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave)
        self._apply_settings()
        self.search_bar = SearchBar()
        #self.editor = TextEditor(self)
        self.apply_theme()

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.addWidget(self.search_bar)

        #editor_layout.addWidget(self.editor)
        editor_layout.addWidget(self.tabs)

        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_shortcut.activated.connect(self.search_bar.open)

        self.search_bar.searchRequested.connect(self._search_text)
        self.search_bar.nextRequested.connect(self._find_next)
        self.search_bar.previousRequested.connect(self._find_previous)
        self.search_bar.closed.connect(self._clear_search)

        #self.metadata_panel = self.structure_view
        self.sidebar_tabs = QTabWidget()
        self.sidebar_tabs.addTab(self.metadata_tree, "Метаданные")
        self.sidebar_tabs.addTab(self.structure_view, "Секции")
        self.sidebar_tabs.addTab(self.file_tree, "Файлы")

        self.issues_panel = QTreeWidget()
        self.issues_panel.setHeaderLabels(["Тип", "Строка", "Сообщение"])
        self.issues_panel.setRootIsDecorated(False)
        self.issues_panel.setUniformRowHeights(True)
        self.issues_panel.setAlternatingRowColors(True)

        self.build_output = QTextEdit()
        self.build_output.setReadOnly(True)
        self.build_output.setPlaceholderText("Build output...")

        self.top_splitter = QSplitter(Qt.Horizontal)
        self.top_splitter.addWidget(self.sidebar_tabs)
        self.top_splitter.addWidget(editor_container)
        self.top_splitter.setSizes([300, 700])

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_file)

        self.bottom_panel = QTabWidget()
        self.bottom_panel.addTab(self.issues_panel, "Проблемы")
        self.bottom_panel.addTab(self.build_output, "Сборка")

        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.bottom_panel)

        # self.main_splitter.setSizes([600, 150])
        self.main_splitter.setStretchFactor(0, 4)
        self.main_splitter.setStretchFactor(1,1)
        self.top_splitter.setStretchFactor(0, 1)
        self.top_splitter.setStretchFactor(1, 3)

        self.setCentralWidget(self.main_splitter)

        self.status_bar = self.statusBar()
        self.cursor_position_label = QLabel("Ln 1, Col 1")
        self.diagnostics_label = QLabel("0 errors, 0 warnings")
        self.parser_status_label = QLabel("Ready")
        self.modified_label = QLabel("Saved")
        self.status_bar.addPermanentWidget(self.modified_label)
        self.status_bar.addPermanentWidget(self.diagnostics_label)
        self.status_bar.addPermanentWidget(self.cursor_position_label)
        self.status_bar.addPermanentWidget(self.parser_status_label)

        self.navigation = NavigationService(self._tree_model)

        self.commands = EditorCommands(
            editor = None,
            navigation=self.navigation,
            main_window=self
        )
        self.structure_view.set_commands(self.commands)

        self.structure_view.activated.connect(self._on_structure_item_activated)

        self.structure_view.jumpRequested.connect(self._on_tree_jump)
        self.issues_panel.itemClicked.connect(self._on_issue_clicked)

        self._rebuild_timer = QTimer(self)
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.timeout.connect(self._rebuild_structure)

        self._navigation_lock = False
        self._navigation_source: NavigationSource | None = None

        self._create_actions()
        self._create_menu()

        self._restore_session()
        self._check_backup_restore()

    def sync_tree_to_line(self, line_no: int):
        index = self._tree_model.index_for_line(line_no)
        if not index.isValid():
            return

        self.structure_view.selectionMode().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        self.structure_view.scrollTo(index)

    def _on_text_changed(self):
        self._is_modified = True
        self.modified_label.setText("Modified")
        self._update_window_title()
        if self.controller.current_document:
            self.controller.current_document.content = (self.editor.get_content())

        self._rebuild_timer.start(300)

    def _rebuild_structure(self):
        self.parser_status_label.setText("Parsing...")

        if self._navigation_lock:
            return

        doc = self.controller.current_document

        if not doc:
            return

        if not doc.content.strip():
            return

        try:
            parsed = doc.parse()
            self._update_metadata(parsed)
        except Exception as exc:
            print("Parse error:", exc)
            self.parser_status_label.setText("Parse error")
            return

        #issues = self.controller.validator.validate(parsed)
        base_issues = self.controller.validator.validate(parsed)
        rpm_issues = self.controller.rpm_validator.validate(doc.content)
        issues = base_issues + rpm_issues
        expanded = self._save_expanded_lines()

        self._tree_model.rebuild(parsed)
        self._tree_model.update_issues(issues)
        self.show_issues(issues)
        self._update_diagnostics_status(issues)
        self._apply_editor_diagnostics(issues)
        # self.issues_panel.itemClicked.connect(self._on_issue_clicked)
        self._restore_expanded_lines(expanded)
        self._expand_issues_if_needed()
        self.parser_status_label.setText("Ready")

    def _on_issue_clicked(self, item):
        try:
            line = int(item.text(1))
        except ValueError:
            return

        self.editor.go_to_line(line)
        self.editor.highlight_line(line, color="#ffeaa7")
        self.editor.setFocus()

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
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_label.setText(f"Ln {line}, Col {column}")

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
            self.editor.clear_highlight()

        self._navigate_to_line(line_no, NavigationSource.EDITOR) # source="editor"

    def _create_actions(self):
        self.new_action = QAction("Создать", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction("Открыть", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction("Сохранить", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction("Сохранить как...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_file_as)

        self.exit_action = QAction("Выход", self)
        self.exit_action.triggered.connect(self.close)

        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._undo)

        self.redo_action = QAction("Вернуть", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._redo)

        self.cut_action = QAction("Вырезать", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self._cut)

        self.copy_action = QAction("Копировать", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self._copy)

        self.paste_action = QAction("Вставить", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self._paste)

        self.select_all_action = QAction("Выбрать все", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self._select_all)

        self.find_action = QAction("Поиск", self)
        self.find_action.setShortcut("Ctrl+F")
        self.find_action.triggered.connect(self.search_bar.open)

        self.align_action = QAction("Выровнять spec-поля", self)
        self.align_action.setShortcut("Ctrl+Alt+L")
        self.align_action.triggered.connect(self.align_spec_tags)


    def _create_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("Файл")

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu.addMenu("Правка")

        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.align_action)

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

        build_menu = menu.addMenu("Сборка")

        self.build_action = QAction("Build RPM", self)
        self.build_action.setShortcut("Ctrl+B")
        self.build_action.triggered.connect(self.build_rpm)
        build_menu.addAction(self.build_action)

        settings_menu = menu.addMenu("Настройки")

        editor_settings_action = QAction("Настройки", self)
        editor_settings_action.triggered.connect(self._show_settings_dialog)
        settings_menu.addAction(editor_settings_action)

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

    def _update_metadata(self, parsed):
        self.metadata_tree.clear()

        for key, value in parsed.headers.items():
            item = QTreeWidgetItem([key, str(value)])
            self.metadata_tree.addTopLevelItem(item)

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
            #self.editor.set_content(document.content)
            editor = self._create_editor_tab(Path(path).name)
            editor.set_content(document.content)
            self.editor = editor

            self._is_modified = False

            parsed = document.parse()
            self._update_metadata(parsed)
            issues = self.controller.validator.validate(parsed)

            self._tree_model.rebuild(parsed)
            self._tree_model.update_issues(issues)
            self.show_issues(issues)
            self._update_diagnostics_status(issues)
            self._apply_editor_diagnostics(issues)
            # self.issues_panel.itemClicked.connect(self._on_issue_clicked)

            directory = str(Path(path).parent)
            self.file_tree.setRootIndex(self.file_model.index(directory))

            self._update_window_title()
        except FileAccessError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def show_issues(self, issues):
        self.issues_panel.clear()

        for issue in issues:
            item = QTreeWidgetItem([
                issue.level.value,
                str(issue.line_no),
                issue.message
            ])
            self.issues_panel.addTopLevelItem(item)

    def on_issue_clicked(self, item):
        line = int(item.text(1))
        self.editor.go_to_line(line)

    def save_file(self):
        editor = self.current_editor()

        try:
            path = getattr(editor, "file_path", None)

            if not path:
                path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Сохранить spec-файл",
                    "",
                    "RPM spec files (*.spec)"
                )

                if not path:
                    return

                editor.file_path = path

            content = editor.get_content()

            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

            # update current document
            if self.controller.current_document:
                self.controller.current_document.path = path
                self.controller.current_document.content = content

            self._is_modified = False

            self.modified_label.setText("Сохранено")

            index = self.tabs.currentIndex()

            self.tabs.setTabText(
                index,
                Path(path).name
            )

            self.status_bar.showMessage(
                "Файл сохранен",
                3000
            )

            self._update_window_title()

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Ошибка",
                str(exc)
            )


    def _apply_editor_diagnostics(self, issues):
        diagnostics = []

        for issue in issues:
            diagnostics.append({
                "line": issue.line_no,
                "level": issue.level.value.lower(),
                "message": issue.message
            })
        self.editor.apply_diagnostics(diagnostics)


    def _update_window_title(self):
        title = "RPM Spec Editor"
        document = self.controller.current_document

        if document:
            title += f" - {document.path.name}"
        if self._is_modified:
            title += " *"

        self.setWindowTitle(title)

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


    def _search_text(self, text):
        self.editor.highlight_search_results(text)

        if not text:
            return

        self.editor.moveCursor(QTextCursor.Start)
        self.editor.find(text)

    def _find_next(self):
        text = self.search_bar.text()
        if text:
            self.editor.find(text)

    def _find_previous(self):
        text = self.search_bar.text()
        if text:
            self.editor.find(text, QTextDocument.FindBackward)

    def _clear_search(self):
        self.editor.highlight_search_results("")


    def _update_diagnostics_status(self, issues):
        errors = 0
        warnings = 0
        for issue in issues:
            level = issue.level.value.lower()

            if level == "error":
                errors += 1
            elif level == "warning":
                warnings += 1

        self.diagnostics_label.setText(f"{errors} errors, {warnings} warnings")

    def _apply_settings(self):
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))

        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)

            if not isinstance(editor, CodeEditor):
                continue

            editor.setFont(font)
            metrics = editor.fontMetrics()
            editor.setTabStopDistance(metrics.horizontalAdvance(" ") * self.settings.get("tab_size"))
            if self.settings.get("word_wrap"):
                editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            else:
                editor.setLineWrapMode(QPlainTextEdit.NoWrap)

            editor.update_line_number_area_width(0)
            editor.viewport().update()
            editor.line_number_area.update()
            editor.highlighter.rehighlight()

        self._configure_autosave()


    def _show_settings_dialog(self):
        dialog = SettingsDialog(self.settings, self)

        if dialog.exec_():
            dialog.apply_settings()
            self.apply_theme()
            self._apply_settings()


    def build_rpm(self):
        self.build_output.clear()
        self.parser_status_label.setText("Building RPM...")
        self.build_action.setEnabled(False)

        self.build_thread = QThread()

        self.build_worker = BuildWorker(self.controller)

        self.build_worker.moveToThread(self.build_thread)

        self.build_thread.started.connect(self.build_worker.run)
        self.build_worker.finished.connect(self._on_build_finished)
        self.build_worker.failed.connect(self._on_build_failed)

        self.build_worker.finished.connect(self.build_thread.quit)
        self.build_worker.finished.connect(self.build_worker.deleteLater)
        self.build_thread.finished.connect(self.build_thread.deleteLater)

        self.build_thread.start()

    def _on_build_finished(self, result):
        output = ""

        if result.stdout:
            output += result.stdout

        if result.stderr:
            output += ("\n\n=== STDERR ===\n\n")
            output += result.stderr

        self.build_output.setPlainText(output)
        self.bottom_panel.setCurrentIndex(1)

        if result.success:
            self.parser_status_label.setText("Build successful")
        else:
            self.parser_status_label.setText("Build failed")
        self.build_action.setEnabled(True)

    def _on_build_failed(self, message):
        self.build_output.setPlainText(message)
        self.bottom_panel.setCurrentIndex(1)
        self.parser_status_label.setText("Build failed")
        self.build_action.setEnabled(True)

    def apply_theme(self):
        if self.settings.get("theme", "dark") == "light":
            colors = LIGHT_COLORS
        else:
            colors = DARK_COLORS
        self.setStyleSheet(build_style(colors))
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)

            if isinstance(editor, CodeEditor):
                editor.apply_theme(colors)

    def _configure_autosave(self):
        self._autosave_timer.stop()
        if not self.settings.autosave_enabled:
            return

        interval_ms = (self.settings.autosave_interval * 1000)
        self._autosave_timer.start(interval_ms)


    def _autosave(self):
        if not self._is_modified:
            return
        if not self.controller.current_document:
            return

        try:
            if self.controller.current_document:
                self.controller.current_document.content = (self.editor.get_content())
            #self.controller.current_document.update_content(self.editor.get_content())
            self.settings = None
            self.controller.save_current()
            self._is_modified = False
            self.modified_label.setText("Autosaved")
        except Exception as exc:
            print(f"Autosave error: {exc}")

    def _check_backup_restore(self):
        backups = (self.controller.backup_manager.find_backups())

        if not backups:
            return

        dialog = RecoveryDialog(backups, self.controller.backup_manager, self)

        if not dialog.exec_():
            return
        backup = dialog.selected_backup
        if not backup:
            return

        content = (self.controller.backup_manager.read_backup(backup))
        self.editor.set_content(content)
        self.status_bar.showMessage("Backup восстановлен", 5000)

    def _save_session(self):
        editor = self.current_editor()

        current_file = None

        if self.controller.current_document:
            current_file = str(
                self.controller.current_document.path
            )

        cursor_position = 0

        if editor:
            cursor_position = (
                editor.textCursor().position()
            )

        data = {
            "current_file": current_file,
            "cursor_position": cursor_position,
            "theme": self.current_theme,
        }

        self.session_manager.save_session(data)

    def _restore_session(self):
        session = self.session_manager.load_session()

        if not session:
            return

        current_file = session.get("current_file")

        if not current_file:
            return

        path = Path(current_file)

        if not path.exists():
            return

        reply = QMessageBox.question(
            self,
            "Восстановление сессии",
            "Восстановить предыдущую сессию?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            document = self.controller.open_file(str(path))

            editor = self._create_editor_tab(path.name)

            editor.set_content(document.content)

            editor.file_path = str(path)

            self.tabs.setCurrentWidget(editor)

            cursor = editor.textCursor()

            cursor.setPosition(
                session.get("cursor_position", 0)
            )

            editor.setTextCursor(cursor)

            parsed = document.parse()

            self._update_metadata(parsed)

            issues = self.controller.validator.validate(parsed)

            self._tree_model.rebuild(parsed)

            self.show_issues(issues)

        except Exception:
            pass

    def closeEvent(self, event):
        self._save_session()
        super().closeEvent(event)

    def current_editor(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def _create_editor_tab(self, title="Untitled"):
        editor = CodeEditor()
        editor.file_path = None
        editor.is_new_file = True
        colors = (
            LIGHT_COLORS
            if self.settings.get("theme") == "light"
            else DARK_COLORS
        )
        editor.set_actions({
            "undo": self.undo_action,
            "redo": self.redo_action,

            "cut": self.cut_action,
            "copy": self.copy_action,
            "paste": self.paste_action,

            "select_all": self.select_all_action
        })

        editor.apply_theme(colors)
        editor.textChanged.connect(self._on_text_changed)
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self.tabs.addTab(editor, title)
        self.tabs.setCurrentWidget(editor)
        self.commands.editor = editor
        return editor

    def _close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.editor = None
        else:
            self.editor = self.current_editor()

    def _on_tab_changed(self, index):
        self.editor = self.current_editor()

    def _undo(self):
        editor = self.current_editor()

        if editor:
            editor.undo()

    def _redo(self):
        editor = self.current_editor()

        if editor:
            editor.redo()

    def _cut(self):
        editor = self.current_editor()

        if editor:
            editor.cut()

    def _copy(self):
        editor = self.current_editor()

        if editor:
            editor.copy()

    def _paste(self):
        editor = self.current_editor()

        if editor:
            editor.paste()

    def _select_all(self):
        editor = self.current_editor()

        if editor:
            editor.selectAll()

    def new_file(self):
        editor = self._create_editor_tab("Untitled")
        editor.set_content(
            "Name:\n"
            "Summary:\n"
            "URL:\n"
            "License:\n\n"
            "Epoch:\n"
            "Version:\n"
            "Release:\n\n"
            "Source0:\n\n"
            "BuildRequires:\n\n"
            "%description\n\n"
            "%prep\n\n"
            "%build\n\n"
            "%install\n\n"
            "%check\n\n"
            "%files\n\n"
            "%changelog\n"
        )
        self.tabs.setCurrentWidget(editor)
        self.status_bar.showMessage("Создан новый файл", 3000)

    def save_file_as(self):
        editor = self.current_editor()

        if not editor:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл как",
            "",
            "RPM Spec Files (*.spec);;All Files (*)"
        )

        if not path:
            return

        try:
            content = editor.get_content()

            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

            # сохраняем путь в editor
            editor.file_path = path

            # обновляем document model
            if self.controller.current_document:
                self.controller.current_document.path = path
                self.controller.current_document.content = content

            # обновляем вкладку
            from pathlib import Path

            index = self.tabs.currentIndex()

            self.tabs.setTabText(
                index,
                Path(path).name
            )

            self._is_modified = False

            self.modified_label.setText("Сохранено")

            self.status_bar.showMessage(
                "Файл сохранен",
                3000
            )

            self._update_window_title()

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                str(exc)
            )

    def align_spec_tags(self):
        text = self.editor.toPlainText()
        formatted = align_spec_fields(text)
        cursor = self.editor.textCursor()
        self.editor.selectAll()
        self.editor.textCursor().insertText(formatted)
        self.editor.setTextCursor(cursor)
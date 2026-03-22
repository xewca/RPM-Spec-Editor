from lib2to3.fixes.fix_metaclass import remove_trailing_newline

from rpm_spec_editor.gui.spec_tree_model import SpecTreeModel

class EditorCommands:
    def __init__(self, editor, navigation, main_window):
        self._editor = editor
        self._navigation = navigation
        self._main_window = main_window

    def go_to_section(self, name: str):
        line_no = self._navigation.find_section_by_name(name)
        if line_no is None:
            return
        self._apply_navigation(line_no)

    def go_to_next_section(self):
        current_line = self._editor.textCursor().blockNumber() + 1
        line_no = self._navigation.find_next_section(current_line)
        if line_no is None:
            return
        self._apply_navigation(line_no)

    def go_to_prev_section(self):
        current_line = self._editor.textCursor().blockNumber() + 1
        line_no = self._navigation.find_prev_section(current_line)
        if line_no is None:
            return
        self._apply_navigation(line_no)

    def _apply_navigation(self, line_no: int):
        self._editor.move_to_line(line_no)
        self._editor.highlight_line(line_no)
        self._main_window.sync_tree_to_line(line_no)

    def go_to_first_section(self):
        line_no = self._navigation.find_first_section()
        if line_no is None:
            return
        self._apply_navigation(line_no)

    def go_to_last_section(self):
        line_no = self._navigation.find_last_section()
        if line_no is None:
            return
        self._apply_navigation(line_no)

    def select_current_section(self):
        model = self._main_window.structure_view.model()
        if not isinstance(model, SpecTreeModel):
            return

        range_ = model.get_active_section_range()
        if not range_:
            return

        start, end = range_
        self._editor.select_range(start, end)

    def toggle_current_section(self):
        model = self._main_window.structure_view.model()
        if not isinstance(model, SpecTreeModel):
            return

        index = model.get_active_section_index()
        if not index:
            return

        view = self._main_window.structure_view

        if view.isExpanded(index):
            view.collapse(index)
        else:
            view.expand(index)

    def go_to_next_issue(self):
        current = self._editor.textCursor().blockNumber() + 1
        line = self._navigation.find_next_issue(current)
        if line:
            self._apply_navigation(line)

    def go_to_prev_issue(self):
        current = self._editor.textCursor().blockNumber() + 1
        line = self._navigation.find_prev_issue(current)
        if line:
            self._apply_navigation(line)
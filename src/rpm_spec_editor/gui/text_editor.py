from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit

from rpm_spec_editor.gui.syntax.spec_higlighter import SpecSyntaxHighlighter

class TextEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighter = SpecSyntaxHighlighter(self.document())

        self._range_selection = None

    def get_content(self) -> str:
        return self.toPlainText()

    def set_content(self, content: str) -> None:
        self.setPlainText(content)

    def highlight_range(self, start_line: int, end_line: int):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)

        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.MoveAnchor,
            max(0, start_line - 1)
        )

        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.KeepAnchor,
            max(0, end_line - start_line)
        )

        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setBackground(QColor("#f5f5f5"))

        self._range_selection = selection

        extras = [selection]

        extras.extend(self.extraSelections())

        self.setExtraSelections(extras)

    def clear_range_highlight(self):
        self._range_selection = None
        self.setExtraSelections([])

    def select_range(self, start_line: int, end_line: int):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)

        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.MoveAnchor,
            max(0, start_line - 1)
        )

        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.KeepAnchor,
            max(0, end_line - start_line + 1)
        )

        self.setTextCursor(cursor)
        self.setFocus()

    def fold_range(self, start_line: int, end_line: int):
        doc = self.document()

        for line in range(start_line, end_line + 1):
            block = doc.findBlockByNumber(line - 1)
            block.setVisible(line == start_line)
            block.setLineCount(0)

        self.viewport().update()

    def fold_current_section(self):
        model = self._main_window.strucrure_view.model()
        range_ = model.get_active_section_range()
        if not range_:
            return

        self._editor.fold_range(*range_)

    def highlight_line(self, line_no: int):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_no - 1)
        cursor.select(QTextCursor.LineUnderCursor)

        extra = QTextEdit.ExtraSelection()
        extra.cursor = cursor
        extra.format.setBackground(QColor("#ffebee"))

        self.setExtraSelections([extra])

    def clear_highlight(self):
        self.setExtraSelections([])

    def go_to_line(self, line_no: int):
        self.move_to_line(line_no)

    def move_to_line(self, line_no: int):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(
            QTextCursor.Down,
            QTextCursor.MoveAnchor,
            max(0, line_no - 1)
        )
        self.setTextCursor(cursor)
        self.setFocus()
        self.centerCursor()
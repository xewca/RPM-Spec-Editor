from PyQt5.QtWidgets import (
    QPlainTextEdit,
    QWidget,
    QTextEdit,
    QMenu,
    QCompleter,
    QToolTip
)
from PyQt5.QtCore import (
    Qt,
    QRect,
    QSize,
    QStringListModel
)
from PyQt5.QtGui import (
    QPainter, 
    QColor, 
    QTextFormat, 
    QTextCursor, 
    QTextCharFormat,
    QFont
)

from rpm_spec_editor.gui.syntax.spec_highlighter import SpecSyntaxHighlighter
from rpm_spec_editor.gui.theme import DARK_COLORS, LIGHT_COLORS
from rpm_spec_editor.gui.completion_data import RPM_COMPLETIONS

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor


    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)


    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


    def mousePressEvent(self, event):
        self.editor.line_number_area_clicked(event)

    def mouseMoveEvent(self, event):
        self.editor.handle_gutter_hover(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.colors = {}

        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setCenterOnScroll(True)
        self.setMouseTracking(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setUndoRedoEnabled(True)
        self.setCursorWidth(2)
        self.setPlaceholderText("Откройте spec-файл...")

        self.completer = QCompleter()
        self.completer.setModel(QStringListModel(RPM_COMPLETIONS))
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

        self.highlighter = SpecSyntaxHighlighter(self.document())
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.current_line_selection = []
        self.error_selections = []
        self.warning_selections = []
        self.range_selections = []
        self.search_selections = []
        self.line_diagnostics = {}
        self.extral_actions = {}
        self.setMouseTracking(True)

        self.folded_blocks = set()
        self.update_line_number_area_width(0)
        #self.highlight_current_line()


    def line_number_area_width(self):
        digits = len(str(self.blockCount()))
        space = 20 + (self.fontMetrics().horizontalAdvance('9') * digits)
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)


    def update_line_number_area(self, rect, dy):
        if dy:
            self. line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)


    def update_selections(self):
        selections = []

        selections.extend(self.current_line_selection)
        selections.extend(self.error_selections)
        selections.extend(self.warning_selections)
        selections.extend(self.range_selections)
        selections.extend(self.search_selections)
        self.setExtraSelections(selections)


    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self.colors["secondary_background"]))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block)
            .translated(self.contentOffset())
            .top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_number = block_number + 1

                diagnostic = self.line_diagnostics.get(line_number)
                if diagnostic:
                    level = diagnostic["level"]
                    if level == "error":
                        painter.setBrush(QColor(self.colors["error"]))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(
                            2,
                            top + 4,
                            8,
                            8
                        )
                    elif level == "warning":
                        painter.setBrush(QColor(self.colors["warning"]))
                        painter.setPen(Qt.NoPen)
                        painter.drawRect(
                            2,
                            top + 4,
                            8,
                            8
                        )

                foldable_lines = self.get_foldable_lines()
                if line_number in foldable_lines:
                    painter.setPen(QColor(self.colors["text"]))
                    marker = "▶"

                    if line_number not in self.folded_blocks:
                        marker = "▼"

                    painter.drawText(
                        12,
                        top + self.fontMetrics().ascent(),
                        marker
                    )

                current_line = (self.textCursor().blockNumber() + 1)
                if line_number == current_line:
                    painter.fillRect(
                        0,
                        top,
                        self.line_number_area.width(),
                        self.fontMetrics().height(),
                        QColor(self.colors["current_line"])
                    )

                diagnostic = self.line_diagnostics.get(line_number)

                if diagnostic:
                    level = diagnostic.get("level")
                    if level == "error":
                        painter.setBrush(QColor(self.colors["error"]))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(2, top + 4, 8, 8)
                    elif diagnostic == "warning":
                        painter.setBrush(QColor(self.colors["warning"]))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(2, top + 4, 8, 8)


                number = str(block_number + 1)
                painter.setPen(QColor(self.colors["line_number"]))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    
    def highlight_current_line(self):
        self.current_line_selection = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.colors["current_line"])
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.current_line_selection.append(selection)
        self.update_selections()

    def set_content(self, text):
        self.setPlainText(text)

    def get_content(self):
        return self.toPlainText()


    def clear_highlight(self):
        self.error_selections = []
        self.warning_selections = []
        self.range_selections = []
        self.update_selections()


    # color=QColor(self.colors["search_highlight"])
    def highlight_line(self, line_number, color=None):
        self.range_selections = []

        selection = QTextEdit.ExtraSelection()

        if color is None:
            color = self.colors["search_highlight"]
        line_color = QColor(color)

        selection.format.setBackground(line_color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)

        block = self.document().findBlockByLineNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            selection.cursor = cursor
            selection.cursor.clearSelection()
            self.range_selections.append(selection)

        self.update_selections()

    #color=self.colors["search_highlight"]
    def highlight_range(self, start, end, color=None):
        self.range_selections = []
        selection = QTextEdit.ExtraSelection()

        if color is None:
            color = self.colors["search_highlight"]
        selection.format.setBackground(QColor(color))

        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        selection.cursor = cursor

        self.range_selections.append(selection)
        self.update_selections()


    def highlight_error(self, line_number, message=""):
        selection = QTextEdit.ExtraSelection()

        error_format = QTextCharFormat()
        error_format.setUnderlineColor(QColor(self.colors["error"]))
        error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        selection.format = error_format

        block = self.document().findBlockByLineNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.select(QTextCursor.LineUnderCursor)
            selection.cursor = cursor
            self.error_selections.append(selection)

        self.update_selections()


    def highlight_warning(self, line_number):
        selection = QTextEdit.ExtraSelection()

        warning_format = QTextCharFormat()
        warning_format.setUnderlineColor(QColor(self.colors["warning"]))
        warning_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        selection.format = warning_format

        block = self.document().findBlockByLineNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.select(QTextCursor.LineUnderCursor)
            selection.cursor = cursor
            self.warning_selections.append(selection)

        self.update_selections()


    def move_to_line(self, line_number):
        block = self.document().findBlockByLineNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            self.setTextCursor(cursor)
            self.centerCursor()

    def go_to_line(self, line_number):
        self.move_to_line(line_number)


    def apply_diagnostics(self, diagnostics):
        self.error_selections = []
        self.warning_selections = []
        self.line_diagnostics = {}

        for diagnostics in diagnostics:
            line = diagnostics.get("line")
            level = diagnostics.get("level")
            self.line_diagnostics[line] = {
                "level": level,
                "message": diagnostics.get("message", "")
            }


            if not line:
                continue

            selection = QTextEdit.ExtraSelection()
            fmt = QTextCharFormat()

            if level == "warning":
                fmt.setUnderlineColor(QColor(self.colors["warning"]))
            else:
                fmt.setUnderlineColor(QColor(self.colors["current_line"]))

            fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            selection.format = fmt
            block = self.document().findBlockByLineNumber(line - 1)

            if block.isValid():
                cursor = QTextCursor(block)
                cursor.select(QTextCursor.LineUnderCursor)
                selection.cursor = cursor

                if level == "warning":
                    self.warning_selections.append(selection)
                else:
                    self.error_selections.append(selection)

        self.update_selections()


    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        line_number = cursor.blockNumber() + 1
        diagnostic = self.line_diagnostics.get(line_number)

        if diagnostic:
            level = diagnostic.get("level", "").upper()
            message = diagnostic.get("message", "")
            tooltip = f"{level}:\\n{message}"
            self.setToolTip(tooltip)
        else:
            self.setToolTip("")

        super().mouseMoveEvent(event)


    def highlight_search_results(self, text):
        self.search_selections = []

        if not text:
            self.update_selections()
            return

        document = self.document()
        cursor = QTextCursor(document)
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(self.colors["search_highlight"]))

        while True:
            cursor = document.find(text, cursor)

            if cursor.isNull():
                break

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = highlight_format
            self.search_selections.append(selection)

        self.update_selections()


    def _show_context_menu(self, position):
        menu = QMenu(self)

        menu.addAction(self.extral_actions["undo"])
        menu.addACtion(self.extral_actions["redo"])

        menu.addSeparator()

        menu.addAction(self.extral_actions["cut"])
        menu.addAction(self.extral_actions["copy"])
        menu.addAction(self.extral_actions["paste"])

        menu.addSeparator()

        menu.addAction(self.extral_actions["select_all"])
        menu.exec_(self.mapToGlobal(position))


    def get_foldable_lines(self):
        foldable = []
        block = self.document().firstBlock()

        while block.isValid():
            text = block.text().strip()
            if text.startswith("%"):
                foldable.append(block.blockNumber() + 1)
            block = block.next()

        return foldable


    def line_number_area_clicked(self, event):
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())

        while block.isValid():
            bottom = top + int(self.blockBoundingRect(block).height())

            if top <= event.pos().y() <= bottom:
                line = block.blockNumber() + 1

                if line in self.get_foldable_lines():
                    self.toggle_fold(line)

                break

            block = block.next()
            top = bottom

    def toggle_fold(self, line_number):
        block = self.document().findBlockByLineNumber(line_number - 1)

        if not block.isValid():
            return

        hide = line_number not in self.folded_blocks
        current = block.next()

        while current.isValid():
            text = current.text().strip()

            if text.startswith("%"):
                break

            current.setVisible(not hide)
            current.setLineCount(0 if hide else 1)
            current = current.next()

        if hide:
            self.folded_blocks.add(line_number)
        else:
            self.folded_blocks.add(line_number)

        self.document().markContentsDirty(0, self.document().characterCount())

        self.viewport().update()
        self.line_number_area.update()
        self.updateGeometry()
        self.viewport().repaint()


    def set_actions(self, actions):
        self.extral_actions = actions


    def insert_completion(self, completion):
        cursor = self.textCursor()
        extra = len(self.completer.completionPrefix())
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, extra)
        cursor.insertText(completion)
        self.setTextCursor(cursor)

    def text_under_cursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        completion_prefix = self.text_under_cursor()

        if len(completion_prefix):
            self.completer.popup().hide()
            return

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))

        rect = self.cursorRect()
        rect.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(rect)


    def apply_diagnostics(self, diagnostics):
        self.line_diagnostics = {}
        self.clear_highlight()

        for diagnostic in diagnostics:
            line = diagnostic["line"]
            level = diagnostic["level"]
            message = diagnostic["message"]

            self.line_diagnostics[line] = {
                "level": level,
                "message": message
            }

            if level == "error":
                self.highlight_error(line)
            elif level == "warning":
                self.highlight_warning(line)

        self.line_number_area.update()


    def handle_gutter_hover(self, event):
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())

        while block.isValid():
            bottom = top + int(self.blockBoundingRect(block).height())

            if top <= event.pos().y() <= bottom:
                line = block.blockNumber() + 1
                diagnostic = self.line_diagnostics.get(line)

                if diagnostic:
                    QToolTip.showText(event.globalPos(), diagnostic["message"], self)
                else:
                    QToolTip.hideText()

                break
            block = block.next()
            top=bottom


    def apply_theme(self, colors):
        self.colors = colors
        self.highlighter.apply_theme(colors)
        self.highlight_current_line()
        self.viewport().update()
        self.line_number_area.update()
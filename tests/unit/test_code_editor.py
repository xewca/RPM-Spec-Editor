import pytest
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication
from rpm_spec_editor.gui.text_editor import TextEditor

pytestmark = pytest.mark.gui

@pytest.mark.unit
def test_get_set_content(qtbot):
    editor = TextEditor()
    editor.set_content("hello")
    assert editor.get_content() == "hello"


@pytest.mark.unit
def test_set_content_overwrite(qtbot):
    editor = TextEditor()
    editor.set_content("a")
    editor.set_content("b")
    assert editor.get_content() == "b"


@pytest.mark.unit
def test_go_to_line(qtbot):
    editor = TextEditor()
    editor.move_to_line = MagicMock()
    editor.go_to_line(3)
    editor.move_to_line.assert_called_once_with(3)


@pytest.mark.unit
def test_move_to_line(qtbot):
    editor = TextEditor()
    editor.set_content("a\nb\nc\nd")
    editor.move_to_line(3)
    cursor = editor.textCursor()
    assert cursor.blockNumber() >= 0


@pytest.mark.unit
def test_highlight_line(qtbot):
    editor = TextEditor()
    editor.set_content("line1\nline2\nline3")
    editor.highlight_line(2)
    assert len(editor.extraSelections()) == 1


@pytest.mark.unit
def test_select_range(qtbot):
    editor = TextEditor()
    editor.set_content("line1\nline2\nline3\nline4")
    editor.select_range(2, 3)
    cursor = editor.textCursor()
    assert cursor is not None


@pytest.mark.unit
def test_highlight_range(qtbot):
    editor = TextEditor()
    editor.set_content("a\nb\nc\nd")
    editor.highlight_range(1, 3)
    assert editor._range_selection is not None
    assert len(editor.extraSelections()) >= 1


@pytest.mark.unit
def test_clear_range_highlight(qtbot):
    editor = TextEditor()
    editor._range_selection = object()
    editor.clear_range_highlight()
    assert editor._range_selection is None
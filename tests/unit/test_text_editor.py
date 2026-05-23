import pytest
from unittest.mock import MagicMock

from rpm_spec_editor.gui.text_editor import TextEditor

@pytest.mark.unit
def test_get_set_content(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor.set_content("Hello")
    assert editor.get_content() == "Hello"

@pytest.mark.unit
def test_clear_highlight(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor.set_content("A\nB\nC")
    editor.highlight_line(2)

    editor.clear_highlight()

    assert editor.extraSelections() == []

@pytest.mark.unit
def test_highlight_line(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor.set_content("A\nB\nC")
    editor.highlight_line(2)
    assert len(editor.extraSelections()) == 1

@pytest.mark.unit
def test_select_range(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor.set_content("A\nB\nC\nD")

    editor.select_range(2, 3)

    cursor = editor.textCursor()
    assert cursor.hasSelection()


@pytest.mark.unit
def test_highlight_range(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)
    editor.set_content("A\nB\nC\nD")
    editor.highlight_range(2, 3)
    assert len(editor.extraSelections()) >= 1


@pytest.mark.unit
def test_fold_range(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor.set_content("A\nB\nC\nD")
    editor.fold_range(1, 3)

@pytest.mark.unit
def test_go_to_line_alias(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor.set_content("A\nB\nC")

    editor.go_to_line(3)

    cursor = editor.textCursor()
    assert cursor.blockNumber() == 2


@pytest.mark.unit
def test_fold_current_section(qtbot):
    editor = TextEditor()
    qtbot.addWidget(editor)

    editor._main_window = MagicMock()
    editor._editor = editor  # чтобы не падало

    model = MagicMock()
    model.get_active_section_range.return_value = (1, 3)

    editor._main_window.strucrure_view.model.return_value = model

    editor.fold_current_section()
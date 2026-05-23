import pytest
from unittest.mock import MagicMock

from rpm_spec_editor.gui.editor_commands import EditorCommands
from rpm_spec_editor.gui.spec_tree_model import SpecTreeModel
from rpm_spec_editor.gui.navigation_types import NavigationSource

@pytest.mark.unit
def test_go_to_section():
    editor = MagicMock()
    editor.textCursor.return_value.blockNumber.return_value = 0

    navigation = MagicMock()
    navigation.find_section_by_name.return_value = 10

    main_window = MagicMock()

    cmd = EditorCommands(editor, navigation, main_window)

    cmd.go_to_section("test")

    editor.move_to_line.assert_called_once_with(10)
    main_window.sync_tree_to_line.assert_called_once_with(10)


@pytest.mark.unit
def test_go_to_next_section():
    editor = MagicMock()
    cursor = MagicMock()
    cursor.blockNumber.return_value = 4
    editor.textCursor.return_value = cursor

    navigation = MagicMock()
    navigation.find_next_section.return_value = 10

    main_window = MagicMock()

    cmd = EditorCommands(editor, navigation, main_window)
    cmd.go_to_next_section()

    editor.move_to_line.assert_called_with(10)


@pytest.mark.unit
def test_go_to_prev_section():
    editor = MagicMock()
    cursor = MagicMock()
    cursor.blockNumber.return_value = 10
    editor.textCursor.return_value = cursor

    navigation = MagicMock()
    navigation.find_prev_section.return_value = 5

    main_window = MagicMock()

    cmd = EditorCommands(editor, navigation, main_window)
    cmd.go_to_prev_section()

    editor.move_to_line.assert_called_with(5)


@pytest.mark.unit
def test_first_last():
    editor = MagicMock()
    editor.textCursor.return_value.blockNumber.return_value = 0

    navigation = MagicMock()
    navigation.find_first_section.return_value = 1
    navigation.find_last_section.return_value = 99

    main_window = MagicMock()

    cmd = EditorCommands(editor, navigation, main_window)

    cmd.go_to_first_section()
    cmd.go_to_last_section()

    assert editor.move_to_line.call_count == 2

@pytest.mark.unit
def test_select_current_section():
    editor = MagicMock()
    editor.textCursor.return_value.blockNumber.return_value = 0

    model = MagicMock(spec=SpecTreeModel)
    model.get_active_section_range.return_value = (1, 5)

    view = MagicMock()
    view.model.return_value = model

    main_window = MagicMock()
    main_window.structure_view = view

    navigation = MagicMock()

    cmd = EditorCommands(editor, navigation, main_window)
    cmd.select_current_section()

    editor.select_range.assert_called_once_with(1, 5)

@pytest.mark.unit
def test_toggle_current_section_expand():
    editor = MagicMock()

    model = MagicMock(spec=SpecTreeModel)
    model.get_active_section_index.return_value = "idx"

    view = MagicMock()
    view.model.return_value = model
    view.isExpanded.return_value = False

    main_window = MagicMock()
    main_window.structure_view = view

    cmd = EditorCommands(editor, MagicMock(), main_window)
    cmd.toggle_current_section()

    view.expand.assert_called_once()

@pytest.mark.unit
def test_issue_navigation():
    editor = MagicMock()
    cursor = MagicMock()
    cursor.blockNumber.return_value = 3
    editor.textCursor.return_value = cursor

    navigation = MagicMock()
    navigation.find_next_issue.return_value = 10
    navigation.find_prev_issue.return_value = 1

    main_window = MagicMock()

    cmd = EditorCommands(editor, navigation, main_window)

    cmd.go_to_next_issue()
    cmd.go_to_prev_issue()

    assert editor.move_to_line.call_count == 2
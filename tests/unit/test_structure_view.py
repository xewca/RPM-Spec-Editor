import pytest
from unittest.mock import MagicMock

from rpm_spec_editor.gui.structure_view import StructureView

@pytest.mark.unit
def test_jump_requested(qtbot):
    view = StructureView()
    class Item:
        line_no = 5
    index = MagicMock()
    index.internalPointer.return_value = Item()
    captured = {}
    view.jumpRequested.connect(lambda x: captured.setdefault("line", x))
    view._on_item_activated(index)
    assert captured["line"] == 5


@pytest.mark.unit
def test_ignore_invalid_item(qtbot):
    view = StructureView()
    index = MagicMock()
    index.internalPointer.return_value = None
    view._on_item_activated(index)


@pytest.mark.unit
def test_context_menu_invalid():
    view = StructureView()
    pos = MagicMock()
    view.indexAt = MagicMock(return_value=MagicMock(isValid=lambda: False))
    view._show_context_menu(pos)

@pytest.mark.unit
def test_populate_menu_issue():
    view = StructureView()
    class Item:
        is_issue = True
        line_no = 10
    menu = MagicMock()
    view._populate_menu(menu, Item(), MagicMock())
    menu.addAction.assert_called()
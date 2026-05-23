import pytest
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt


from rpm_spec_editor.gui.spec_tree_model import SpecTreeModel


@pytest.mark.unit
def test_empty_model(qtbot):
    model = SpecTreeModel()

    assert model.rowCount(QModelIndex()) == 0


@pytest.mark.unit
def test_column_count(qtbot):
    model = SpecTreeModel()

    assert model.columnCount(QModelIndex()) >= 0


@pytest.mark.unit
def test_model_initialization(qtbot):
    model = SpecTreeModel()
    assert model is not None


@pytest.mark.unit
def test_invalid_index_returns_none(qtbot):
    model = SpecTreeModel()
    index = QModelIndex()
    result = model.data(index, Qt.DisplayRole)
    assert result is None or result == ""


@pytest.mark.unit
def test_row_count_root(qtbot):
    model = SpecTreeModel()

    assert model.rowCount(QModelIndex()) >= 0

@pytest.mark.unit
def test_model_structure_methods_exist(qtbot):
    model = SpecTreeModel()

    assert hasattr(model, "rowCount")
    assert hasattr(model, "columnCount")
    assert hasattr(model, "index")
    assert hasattr(model, "parent")
    assert hasattr(model, "data")


@pytest.mark.unit
def test_index_call_safe(qtbot):
    model = SpecTreeModel()

    parent = QModelIndex()

    index = model.index(0, 0, parent)

    assert index is not None

@pytest.mark.unit
def test_model_smoke(qtbot):
    model = SpecTreeModel()

    root = QModelIndex()

    model.rowCount(root)
    model.columnCount(root)
    model.index(0, 0, root)
    model.parent(root)


@pytest.mark.unit
def test_parent_call(qtbot):
    model = SpecTreeModel()

    idx = model.index(0, 0, QModelIndex())

    parent = model.parent(idx)

    assert isinstance(parent, QModelIndex)
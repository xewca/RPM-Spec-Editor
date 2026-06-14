import pytest
from PyQt5.QtWidgets import QApplication

pytestmark = pytest.mark.gui
from PyQt5.QtCore import QModelIndex

from PyQt5.QtWidgets import QFileDialog

from rpm_spec_editor.gui.main_window import MainWindow


@pytest.mark.integration
def test_open_file_gui_workflow(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "test.spec"

    spec_file.write_text("""
Name: gui-test
Version: 1.0
Release: 1

%description
GUI integration test
""")

    def fake_get_open_file_name(*args, **kwargs):
        return str(spec_file), "RPM spec files (*.spec)"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", fake_get_open_file_name)
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    assert window.controller.current_document is not None
    assert (window.controller.current_document.parsed.headers["Name"] == "gui-test")
    assert window.editor is not None
    assert window.metadata_tree.topLevelItemCount() > 0



@pytest.mark.integration
def test_rebuild_structure_after_edit(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "rebuild.spec"

    spec_file.write_text("""
Name: rebuild-test
Version: 1.0
Release: 1

%description
Initial description
""")

    def fake_get_open_file_name(*args, **kwargs):
        return str(spec_file), "RPM spec files (*.spec)"

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        fake_get_open_file_name
    )
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    assert window.editor is not None
    initial_count = (window.metadata_tree.topLevelItemCount())
    updated_content = """
Name: rebuild-test
Version: 2.0
Release: 2

Summary: Updated package

%description
Updated description

%prep
echo prep
"""
    window.editor.set_content(updated_content)
    window.controller.current_document.content = updated_content
    window._rebuild_structure()
    assert (window.metadata_tree.topLevelItemCount() >= initial_count)
    parsed = window.controller.current_document.parse()
    assert parsed.headers["Version"] == "2.0"
    assert "prep" in parsed.sections



@pytest.mark.integration
def test_issues_panel_updates_after_invalid_spec(qtbot, tmp_path, monkeypatch):

    spec_file = tmp_path / "invalid.spec"
    spec_file.write_text("""
Version: 1.0

%description
Broken package
""")

    def fake_get_open_file_name(*args, **kwargs):
        return str(spec_file), "RPM spec files (*.spec)"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", fake_get_open_file_name)
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    issues_count = window.issues_panel.topLevelItemCount()
    assert issues_count > 0
    diagnostics_text = (window.diagnostics_label.text())
    assert ("ошибок" in diagnostics_text.lower() or "предупреждений" in diagnostics_text.lower())


@pytest.mark.integration
def test_structure_navigation(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "navigation.spec"

    spec_file.write_text("""
    Name: navigation-test
    Version: 1.0
    Release: 1

    %description
    Navigation test

    %prep
    echo prep
    """)

    def fake_get_open_file_name(*args, **kwargs):
        return str(spec_file), "RPM spec files (*.spec)"

    monkeypatch.setattr(QFileDialog, "getOpenFileName", fake_get_open_file_name)
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    called = {}

    def fake_navigate(line_no, source):
        called["line_no"] = line_no
        called["source"] = source

    monkeypatch.setattr(window, "_navigate_to_line", fake_navigate)
    model = window.structure_view.model()
    root_index = model.index(0, 0, QModelIndex())
    assert root_index.isValid()
    window._on_structure_item_activated(root_index)
    assert "line_no" in called


@pytest.mark.integration
def test_build_flow(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "build.spec"
    spec_file.write_text("Name: build-test\nVersion: 1")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(spec_file), ""))
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    result = window.controller.build_current()
    assert result is not None


@pytest.mark.integration
def test_backup_created_on_save(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "backup.spec"
    spec_file.write_text("Name: test")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(spec_file), ""))

    window = MainWindow()
    qtbot.addWidget(window)

    window.open_file()
    window.save_file()

    backups = list(window.controller.backup_manager.backup_dir.rglob("*"))
    assert len(backups) > 0


@pytest.mark.integration
def test_window_state_changes(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "state.spec"
    spec_file.write_text("Name: test")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(spec_file), ""))
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    window.editor.set_content("modified content")
    assert hasattr(window, "_is_modified")

@pytest.mark.integration
def test_structure_navigation_safe(qtbot, tmp_path, monkeypatch):
    spec_file = tmp_path / "nav.spec"
    spec_file.write_text("Name: nav\nVersion: 1")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(spec_file), ""))
    window = MainWindow()
    qtbot.addWidget(window)
    window.open_file()
    model = window.structure_view.model()
    index = model.index(0, 0, QModelIndex())
    try:
        window._on_structure_item_activated(index)
    except Exception:
        pytest.fail("Navigation should not crash")
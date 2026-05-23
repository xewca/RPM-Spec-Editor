import pytest
from pathlib import Path
from unittest.mock import MagicMock


from rpm_spec_editor.storage.file_manager import FileAccessError
from rpm_spec_editor.core.app_controller import AppController


def test_open_file_success(tmp_path, monkeypatch):
    file_path = tmp_path / "test.spec"
    file_path.write_text("Name: test\nVersion: 1.0")
    monkeypatch.setenv("HOME", str(tmp_path))
    controller = AppController()
    doc = controller.open_file(str(file_path))

    assert doc is not None
    assert controller.current_document is not None
    assert controller.current_document.path == Path(file_path)
    assert isinstance(controller.validation_issues, list)

@pytest.mark.unit
def test_open_file_sets_validation_issues(tmp_path, monkeypatch):
    file_path = tmp_path / "test.spec"
    file_path.write_text("Name: test")

    monkeypatch.setenv("HOME", str(tmp_path))

    controller = AppController()

    controller.open_file(str(file_path))

    assert isinstance(controller.validation_issues, list)


@pytest.mark.unit
def test_save_current_no_document(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    controller = AppController()

    with pytest.raises(FileAccessError):
        controller.save_current()

@pytest.mark.unit
def test_save_current_success(tmp_path, monkeypatch):
    file_path = tmp_path / "test.spec"
    file_path.write_text("OLD")

    monkeypatch.setenv("HOME", str(tmp_path))

    controller = AppController()

    controller.open_file(str(file_path))
    controller.current_document.content = "NEW CONTENT"

    controller.save_current()

    assert file_path.read_text() == "NEW CONTENT"

@pytest.mark.unit
def test_save_current_creates_backup(tmp_path, monkeypatch):
    file_path = tmp_path / "test.spec"
    file_path.write_text("OLD")

    monkeypatch.setenv("HOME", str(tmp_path))

    controller = AppController()

    controller.open_file(str(file_path))
    controller.save_current()

    backups = list((tmp_path / ".rpm_spec_editor" / "backups").rglob("*"))
    assert len(backups) > 0

@pytest.mark.unit
def test_build_current_no_document(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    controller = AppController()

    with pytest.raises(FileAccessError):
        controller.build_current()



@pytest.mark.unit
def test_build_current_success(tmp_path, monkeypatch):
    file_path = tmp_path / "test.spec"
    file_path.write_text("Name: test")

    monkeypatch.setenv("HOME", str(tmp_path))

    controller = AppController()

    controller.builder = MagicMock()
    controller.builder.build.return_value = "RPM_OK"

    controller.open_file(str(file_path))

    result = controller.build_current()

    assert result == "RPM_OK"
    controller.builder.build.assert_called_once()


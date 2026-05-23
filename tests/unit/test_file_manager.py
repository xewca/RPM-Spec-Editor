from unittest.mock import patch

import pytest

from rpm_spec_editor.storage.file_manager import FileManager, FileAccessError

@pytest.mark.unit
def test_open_file(tmp_path):
    file_path = tmp_path / "test.spec"
    content = "Name: test-package"
    file_path.write_text(content)
    manager = FileManager()
    result = manager.open_file(str(file_path))
    assert result == content


@pytest.mark.unit
def test_open_missing_file():
    manager = FileManager()
    with pytest.raises(FileAccessError):
        manager.open_file("missing.spec")


@pytest.mark.unit
def test_open_invalid_extension(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("invalid")
    manager = FileManager()
    with pytest.raises(FileAccessError):
        manager.open_file(str(file_path))


@pytest.mark.unit
def test_save_file(tmp_path):
    file_path = tmp_path / "save.spec"
    manager = FileManager()
    content = "Version: 1.0"
    manager.save_file(str(file_path), content)
    assert file_path.read_text() == content


@pytest.mark.unit
def test_utf8_content(tmp_path):
    file_path = tmp_path / "utf8.spec"
    content = "Summary: Тестовый пакет"
    file_path.write_text(content, encoding="utf-8")
    manager = FileManager()
    result = manager.open_file(str(file_path))
    assert result == content


@pytest.mark.unit
def test_create_backup(tmp_path):
    file_path = tmp_path / "backup.spec"
    file_path.write_text("Name: backup-test")
    manager = FileManager()
    backup_path = manager.create_backup(file_path)
    assert backup_path.exists()
    assert backup_path.read_text() == "Name: backup-test"


@pytest.mark.unit
def test_restore_last_backup(tmp_path):
    file_path = tmp_path / "restore.spec"
    file_path.write_text("old content")
    manager = FileManager()
    manager.create_backup(file_path)
    file_path.write_text("new content")
    manager.restore_last_backup(str(file_path))
    restored = file_path.read_text()
    assert restored == "old content"

@pytest.mark.unit
def test_open_empty_file(tmp_path):
    file_path = tmp_path / "empty.spec"
    file_path.write_text("")

    manager = FileManager()

    result = manager.open_file(str(file_path))

    assert result == ""


@pytest.mark.unit
def test_save_overwrite_file(tmp_path):
    file_path = tmp_path / "overwrite.spec"

    manager = FileManager()
    manager.save_file(str(file_path), "old content")
    manager.save_file(str(file_path), "new content")

    assert file_path.read_text() == "new content"



@pytest.mark.unit
def test_open_invalid_encoding(tmp_path):
    file_path = tmp_path / "broken.spec"

    file_path.write_bytes(b"\xff\xfe\x00\x00")

    manager = FileManager()

    with pytest.raises(FileAccessError):
        manager.open_file(str(file_path))


@pytest.mark.unit
def test_open_directory_instead_of_file(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()

    manager = FileManager()

    with pytest.raises(FileAccessError):
        manager.open_file(str(directory))


@pytest.mark.unit
def test_open_file_permission_error(tmp_path):
    file_path = tmp_path / "test.spec"
    file_path.write_text("data")

    manager = FileManager()

    with patch("pathlib.Path.read_text", side_effect=PermissionError):
        with pytest.raises(FileAccessError):
            manager.open_file(str(file_path))

@pytest.mark.unit
def test_open_file_os_error(tmp_path):
    file_path = tmp_path / "test.spec"
    file_path.write_text("data")

    manager = FileManager()

    with patch("pathlib.Path.read_text", side_effect=OSError):
        with pytest.raises(FileAccessError):
            manager.open_file(str(file_path))

@pytest.mark.unit
def test_save_file_permission_error(tmp_path):
    file_path = tmp_path / "save.spec"

    manager = FileManager()

    with patch("pathlib.Path.write_text", side_effect=PermissionError):
        with pytest.raises(FileAccessError):
            manager.save_file(str(file_path), "data")


@pytest.mark.unit
def test_save_file_os_error(tmp_path):
    file_path = tmp_path / "save.spec"

    manager = FileManager()

    with patch("pathlib.Path.write_text", side_effect=OSError):
        with pytest.raises(FileAccessError):
            manager.save_file(str(file_path), "data")


@pytest.mark.unit
def test_create_backup_permission_error(tmp_path):
    file_path = tmp_path / "a.spec"
    file_path.write_text("data")

    manager = FileManager()

    with patch("shutil.copy2", side_effect=PermissionError):
        with pytest.raises(FileAccessError):
            manager.create_backup(file_path)

@pytest.mark.unit
def test_create_backup_os_error(tmp_path):
    file_path = tmp_path / "a.spec"
    file_path.write_text("data")

    manager = FileManager()

    with patch("shutil.copy2", side_effect=OSError):
        with pytest.raises(FileAccessError):
            manager.create_backup(file_path)

@pytest.mark.unit
def test_restore_permission_error(tmp_path):
    file_path = tmp_path / "a.spec"
    file_path.write_text("data")

    manager = FileManager()
    manager.create_backup(file_path)

    with patch("shutil.copy2", side_effect=PermissionError):
        with pytest.raises(FileAccessError):
            manager.restore_last_backup(str(file_path))

@pytest.mark.unit
def test_restore_os_error(tmp_path):
    file_path = tmp_path / "a.spec"
    file_path.write_text("data")

    manager = FileManager()
    manager.create_backup(file_path)

    with patch("shutil.copy2", side_effect=OSError):
        with pytest.raises(FileAccessError):
            manager.restore_last_backup(str(file_path))


import json, pytest
from pathlib import Path

from rpm_spec_editor.core.backup_manager import BackupManager

@pytest.mark.unit
def test_create_backup_creates_structure(tmp_path):
    manager = BackupManager(tmp_path)

    file_path = "test.spec"
    content = "Name: test\nVersion: 1.0"

    manager.create_backup(file_path, content)

    # должна появиться 1 папка (md5 от пути)
    folders = list(tmp_path.iterdir())
    assert len(folders) == 1

    folder = folders[0]

    content_file = folder / "content.spec"
    metadata_file = folder / "metadata.json"

    assert content_file.exists()
    assert metadata_file.exists()

    assert content_file.read_text(encoding="utf-8") == content

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert metadata["original_file"] == file_path
    assert metadata["size"] == len(content)
    assert "timestamp" in metadata


@pytest.mark.unit
def test_backup_folder_is_deterministic(tmp_path):
    manager = BackupManager(tmp_path)

    p1 = manager._backup_folder("file.spec")
    p2 = manager._backup_folder("file.spec")

    assert p1 == p2


@pytest.mark.unit
def test_file_id_is_stable(tmp_path):
    manager = BackupManager(tmp_path)

    id1 = manager._file_id("file.spec")
    id2 = manager._file_id("file.spec")

    assert id1 == id2
    assert len(id1) == 32


@pytest.mark.unit
def test_find_backups_returns_valid_entries(tmp_path):
    manager = BackupManager(tmp_path)

    file_path = "test.spec"
    manager.create_backup(file_path, "content")

    backups = manager.find_backups()

    assert len(backups) == 1

    b = backups[0]
    assert "original_file" in b
    assert "timestamp" in b
    assert "size" in b
    assert "folder" in b
    assert "content_file" in b


@pytest.mark.unit
def test_find_backups_ignores_invalid_folders(tmp_path):
    manager = BackupManager(tmp_path)

    (tmp_path / "random_dir").mkdir()
    (tmp_path / "random_dir" / "metadata.json").write_text("{}")
    backups = manager.find_backups()
    assert backups == []


@pytest.mark.unit
def test_read_backup_returns_content(tmp_path):
    manager = BackupManager(tmp_path)

    manager.create_backup("file.spec", "HELLO")

    backups = manager.find_backups()
    content = manager.read_backup(backups[0])

    assert content == "HELLO"


@pytest.mark.unit
def test_remove_backup_deletes_folder(tmp_path):
    manager = BackupManager(tmp_path)

    manager.create_backup("file.spec", "DATA")
    backups = manager.find_backups()

    folder = backups[0]["folder"]
    manager.remove_backup(backups[0])

    assert not Path(folder).exists()


@pytest.mark.unit
def test_find_backups_skips_corrupt_metadata(tmp_path):
    manager = BackupManager(tmp_path)

    folder = tmp_path / "broken"
    folder.mkdir()

    (folder / "metadata.json").write_text("INVALID JSON")
    (folder / "content.spec").write_text("DATA")

    backups = manager.find_backups()

    assert backups == []

